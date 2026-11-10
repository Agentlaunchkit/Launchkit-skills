#!/usr/bin/env python3
"""Lint an X thread draft before a human posts it.

Usage: check_thread.py thread.md [--facts facts.json] [--long-posts]
       check_thread.py --self-test
thread.md format: posts separated by a line containing only '---'.
A post starting with 'REPLY:' is the first reply (where the link goes).

Length uses X's weighted character count (twitter-text v3):
- each http(s), www, or bare-domain URL counts as 23 (t.co)
- each emoji cluster (ZWJ sequences, flags, keycaps, skin tones) counts as 2
- Latin and a few punctuation ranges count as 1; everything else (including CJK) counts as 2
The limit is 280. --long-posts lifts it for Premium accounts but still warns past 280.

Also checks: at most 1 hashtag per post, no @-mention lists, no engagement bait,
links only in the REPLY post (bare example.com in a command is counted but not warned),
and every number in the thread appears in facts.json (catches invented stats).
Exit code 1 if any ERROR.
"""
import argparse, json, re, sys, unicodedata

# gTLD + ccTLD list from twitter-text (Copyright Twitter, Inc., Apache 2.0).
# Used so bare domains like example.com, t.co/x, readme.md and foo.py count as URLs
# the same way X counts them.
_TLDS = set("""aaa|aarp|abarth|abb|abbott|abbvie|abc|able|abogado|abudhabi|ac|academy|accenture|accountant|accountants|aco|active|actor|ad|adac|ads|adult|ae|aeg|aero|aetna|af|afamilycompany|afl|africa|ag|agakhan|agency|ai|aig|aigo|airbus|airforce|airtel|akdn|al|alfaromeo|alibaba|alipay|allfinanz|allstate|ally|alsace|alstom|am|americanexpress|americanfamily|amex|amfam|amica|amsterdam|an|analytics|android|anquan|anz|ao|aol|apartments|app|apple|aq|aquarelle|ar|arab|aramco|archi|army|arpa|art|arte|as|asda|asia|associates|at|athleta|attorney|au|auction|audi|audible|audio|auspost|author|auto|autos|avianca|aw|aws|ax|axa|az|azure|ba|baby|baidu|banamex|bananarepublic|band|bank|bar|barcelona|barclaycard|barclays|barefoot|bargains|baseball|basketball|bauhaus|bayern|bb|bbc|bbt|bbva|bcg|bcn|bd|be|beats|beauty|beer|bentley|berlin|best|bestbuy|bet|bf|bg|bh|bharti|bi|bible|bid|bike|bing|bingo|bio|biz|bj|bl|black|blackfriday|blanco|blockbuster|blog|bloomberg|blue|bm|bms|bmw|bn|bnl|bnpparibas|bo|boats|boehringer|bofa|bom|bond|boo|book|booking|boots|bosch|bostik|boston|bot|boutique|box|bq|br|bradesco|bridgestone|broadway|broker|brother|brussels|bs|bt|budapest|bugatti|build|builders|business|buy|buzz|bv|bw|by|bz|bzh|ca|cab|cafe|cal|call|calvinklein|cam|camera|camp|cancerresearch|canon|capetown|capital|capitalone|car|caravan|cards|care|career|careers|cars|cartier|casa|case|caseih|cash|casino|cat|catering|catholic|cba|cbn|cbre|cbs|cc|cd|ceb|center|ceo|cern|cf|cfa|cfd|cg|ch|chanel|channel|charity|chase|chat|cheap|chintai|chloe|christmas|chrome|chrysler|church|ci|cipriani|circle|cisco|citadel|citi|citic|city|cityeats|ck|cl|claims|cleaning|click|clinic|clinique|clothing|cloud|club|clubmed|cm|cn|co|coach|codes|coffee|college|cologne|com|comcast|commbank|community|company|compare|computer|comsec|condos|construction|consulting|contact|contractors|cooking|cookingchannel|cool|coop|corsica|country|coupon|coupons|courses|cpa|cr|credit|creditcard|creditunion|cricket|crown|crs|cruise|cruises|csc|cu|cuisinella|cv|cw|cx|cy|cymru|cyou|cz|dabur|dad|dance|data|date|dating|datsun|day|dclk|dds|de|deal|dealer|deals|degree|delivery|dell|deloitte|delta|democrat|dental|dentist|desi|design|dev|dhl|diamonds|diet|digital|direct|directory|discount|discover|dish|diy|dj|dk|dm|dnp|do|docs|doctor|dodge|dog|doha|domains|doosan|dot|download|drive|dtv|dubai|duck|dunlop|duns|dupont|durban|dvag|dvr|dz|earth|eat|ec|eco|edeka|edu|education|ee|eg|eh|email|emerck|energy|engineer|engineering|enterprises|epost|epson|equipment|er|ericsson|erni|es|esq|estate|esurance|et|etisalat|eu|eurovision|eus|events|everbank|exchange|expert|exposed|express|extraspace|fage|fail|fairwinds|faith|family|fan|fans|farm|farmers|fashion|fast|fedex|feedback|ferrari|ferrero|fi|fiat|fidelity|fido|film|final|finance|financial|fire|firestone|firmdale|fish|fishing|fit|fitness|fj|fk|flickr|flights|flir|florist|flowers|flsmidth|fly|fm|fo|foo|food|foodnetwork|football|ford|forex|forsale|forum|foundation|fox|fr|free|fresenius|frl|frogans|frontdoor|frontier|ftr|fujitsu|fujixerox|fun|fund|furniture|futbol|fyi|ga|gal|gallery|gallo|gallup|game|games|gap|garden|gay|gb|gbiz|gd|gdn|ge|gea|gent|genting|george|gf|gg|ggee|gh|gi|gift|gifts|gives|giving|gl|glade|glass|gle|global|globo|gm|gmail|gmbh|gmo|gmx|gn|godaddy|gold|goldpoint|golf|goo|goodhands|goodyear|goog|google|gop|got|gov|gp|gq|gr|grainger|graphics|gratis|green|gripe|grocery|group|gs|gt|gu|guardian|gucci|guge|guide|guitars|guru|gw|gy|hair|hamburg|hangout|haus|hbo|hdfc|hdfcbank|health|healthcare|help|helsinki|here|hermes|hgtv|hiphop|hisamitsu|hitachi|hiv|hk|hkt|hm|hn|hockey|holdings|holiday|homedepot|homegoods|homes|homesense|honda|honeywell|horse|hospital|host|hosting|hot|hoteles|hotels|hotmail|house|how|hr|hsbc|ht|htc|hu|hughes|hyatt|hyundai|ibm|icbc|ice|icu|id|ie|ieee|ifm|iinet|ikano|il|im|imamat|imdb|immo|immobilien|in|inc|industries|infiniti|info|ing|ink|institute|insurance|insure|int|intel|international|intuit|investments|io|ipiranga|iq|ir|irish|is|iselect|ismaili|ist|istanbul|it|itau|itv|iveco|iwc|jaguar|java|jcb|jcp|je|jeep|jetzt|jewelry|jio|jlc|jll|jm|jmp|jnj|jo|jobs|joburg|jot|joy|jp|jpmorgan|jprs|juegos|juniper|kaufen|kddi|ke|kerryhotels|kerrylogistics|kerryproperties|kfh|kg|kh|ki|kia|kim|kinder|kindle|kitchen|kiwi|km|kn|koeln|komatsu|kosher|kp|kpmg|kpn|kr|krd|kred|kuokgroup|kw|ky|kyoto|kz|la|lacaixa|ladbrokes|lamborghini|lamer|lancaster|lancia|lancome|land|landrover|lanxess|lasalle|lat|latino|latrobe|law|lawyer|lb|lc|lds|lease|leclerc|lefrak|legal|lego|lexus|lgbt|li|liaison|lidl|life|lifeinsurance|lifestyle|lighting|like|lilly|limited|limo|lincoln|linde|link|lipsy|live|living|lixil|lk|llc|llp|loan|loans|locker|locus|loft|lol|london|lotte|lotto|love|lpl|lplfinancial|lr|ls|lt|ltd|ltda|lu|lundbeck|lupin|luxe|luxury|lv|ly|ma|macys|madrid|maif|maison|makeup|man|management|mango|map|market|marketing|markets|marriott|marshalls|maserati|mattel|mba|mc|mcd|mcdonalds|mckinsey|md|me|med|media|meet|melbourne|meme|memorial|men|menu|meo|merckmsd|metlife|mf|mg|mh|miami|microsoft|mil|mini|mint|mit|mitsubishi|mk|ml|mlb|mls|mm|mma|mn|mo|mobi|mobile|mobily|moda|moe|moi|mom|monash|money|monster|montblanc|mopar|mormon|mortgage|moscow|moto|motorcycles|mov|movie|movistar|mp|mq|mr|ms|msd|mt|mtn|mtpc|mtr|mu|museum|mutual|mutuelle|mv|mw|mx|my|mz|na|nab|nadex|nagoya|name|nationwide|natura|navy|nba|nc|ne|nec|net|netbank|netflix|network|neustar|new|newholland|news|next|nextdirect|nexus|nf|nfl|ng|ngo|nhk|ni|nico|nike|nikon|ninja|nissan|nissay|nl|no|nokia|northwesternmutual|norton|now|nowruz|nowtv|np|nr|nra|nrw|ntt|nu|nyc|nz|obi|observer|off|office|okinawa|olayan|olayangroup|oldnavy|ollo|om|omega|one|ong|onion|onl|online|onyourside|ooo|open|oracle|orange|org|organic|orientexpress|origins|osaka|otsuka|ott|ovh|pa|page|pamperedchef|panasonic|panerai|paris|pars|partners|parts|party|passagens|pay|pccw|pe|pet|pf|pfizer|pg|ph|pharmacy|phd|philips|phone|photo|photography|photos|physio|piaget|pics|pictet|pictures|pid|pin|ping|pink|pioneer|pizza|pk|pl|place|play|playstation|plumbing|plus|pm|pn|pnc|pohl|poker|politie|porn|post|pr|pramerica|praxi|press|prime|pro|prod|productions|prof|progressive|promo|properties|property|protection|pru|prudential|ps|pt|pub|pw|pwc|py|qa|qpon|quebec|quest|qvc|racing|radio|raid|re|read|realestate|realtor|realty|recipes|red|redstone|redumbrella|rehab|reise|reisen|reit|reliance|ren|rent|rentals|repair|report|republican|rest|restaurant|review|reviews|rexroth|rich|richardli|ricoh|rightathome|ril|rio|rip|rmit|ro|rocher|rocks|rodeo|rogers|room|rs|rsvp|ru|rugby|ruhr|run|rw|rwe|ryukyu|sa|saarland|safe|safety|sakura|sale|salon|samsclub|samsung|sandvik|sandvikcoromant|sanofi|sap|sapo|sarl|sas|save|saxo|sb|sbi|sbs|sc|sca|scb|schaeffler|schmidt|scholarships|school|schule|schwarz|science|scjohnson|scor|scot|sd|se|search|seat|secure|security|seek|select|sener|services|ses|seven|sew|sex|sexy|sfr|sg|sh|shangrila|sharp|shaw|shell|shia|shiksha|shoes|shop|shopping|shouji|show|showtime|shriram|si|silk|sina|singles|site|sj|sk|ski|skin|sky|skype|sl|sling|sm|smart|smile|sn|sncf|so|soccer|social|softbank|software|sohu|solar|solutions|song|sony|soy|space|spiegel|sport|spot|spreadbetting|sr|srl|srt|ss|st|stada|staples|star|starhub|statebank|statefarm|statoil|stc|stcgroup|stockholm|storage|store|stream|studio|study|style|su|sucks|supplies|supply|support|surf|surgery|suzuki|sv|swatch|swiftcover|swiss|sx|sy|sydney|symantec|systems|sz|tab|taipei|talk|taobao|target|tatamotors|tatar|tattoo|tax|taxi|tc|tci|td|tdk|team|tech|technology|tel|telecity|telefonica|temasek|tennis|teva|tf|tg|th|thd|theater|theatre|tiaa|tickets|tienda|tiffany|tips|tires|tirol|tj|tjmaxx|tjx|tk|tkmaxx|tl|tm|tmall|tn|to|today|tokyo|tools|top|toray|toshiba|total|tours|town|toyota|toys|tp|tr|trade|trading|training|travel|travelchannel|travelers|travelersinsurance|trust|trv|tt|tube|tui|tunes|tushu|tv|tvs|tw|tz|ua|ubank|ubs|uconnect|ug|uk|um|unicom|university|uno|uol|ups|us|uy|uz|va|vacations|vana|vanguard|vc|ve|vegas|ventures|verisign|versicherung|vet|vg|vi|viajes|video|vig|viking|villas|vin|vip|virgin|visa|vision|vista|vistaprint|viva|vivo|vlaanderen|vn|vodka|volkswagen|volvo|vote|voting|voto|voyage|vu|vuelos|wales|walmart|walter|wang|wanggou|warman|watch|watches|weather|weatherchannel|webcam|weber|website|wed|wedding|weibo|weir|wf|whoswho|wien|wiki|williamhill|win|windows|wine|winners|wme|wolterskluwer|woodside|work|works|world|wow|ws|wtc|wtf|xbox|xerox|xfinity|xihuan|xin|xperia|xxx|xyz|yachts|yahoo|yamaxun|yandex|ye|yodobashi|yoga|yokohama|you|youtube|yt|yun|za|zappos|zara|zero|zip|zippo|zm|zone|zuerich|zw|ελ|ευ|бг|ею|рф|გე|コム|世界|中信|中国|中國|企业|佛山|信息|健康|八卦|公司|公益|台湾|台灣|商城|商店|商标|嘉里|在线|大拿|娱乐|家電|工行|广东|微博|慈善|手机|手表|招聘|政务|政府|新闻|时尚|書籍|机构|游戏|澳門|点看|珠宝|移动|网址|网店|网站|网络|联通|谷歌|购物|通販|集团|食品|餐厅|香港|닷넷|닷컴|삼성|한국|бел|ком|мкд|мон|орг|рус|срб|укр|қаз|հայ|קום|عرب|قطر|كوم|مصر|कॉम|नेट|คอม|ไทย|ລາວ|みんな|ストア|セール|中文网|天主教|我爱你|新加坡|淡马锡|诺基亚|飞利浦|дети|сайт|بارت|بيتك|تونس|شبكة|عراق|عمان|موقع|ڀارت|भारत|ভারত|ভাৰত|ਭਾਰਤ|ભારત|ଭାରତ|ಭಾರತ|ලංකා|クラウド|グーグル|ポイント|大众汽车|组织机构|電訊盈科|香格里拉|ایران|بازار|بھارت|سودان|سورية|همراه|भारोत|संगठन|বাংলা|భారత్|ഭാരതം|嘉里大酒店|москва|онлайн|ابوظبي|ارامكو|الاردن|المغرب|امارات|فلسطين|مليسيا|भारतम्|இலங்கை|ファッション|католик|اتصالات|البحرين|الجزائر|العليان|كاثوليك|موبايلي|پاکستان|இந்தியா|السعودية|موريتانيا|சிங்கப்பூர்|vermögensberater|vermögensberatung""".split("|"))

# Trailing punctuation X peels off a URL; commas inside a query string stay.
_TRAIL = set(".,!?;:")

# Weight-1 ranges from twitter-text v3 (scale 100, default 200).
def _unit(cp):
    if cp <= 0x10FF or 0x2000 <= cp <= 0x200D or 0x2010 <= cp <= 0x201F or 0x2032 <= cp <= 0x2037:
        return 1
    return 2

def _is_vs(cp):
    return cp in (0xFE0E, 0xFE0F)

def _is_skin(cp):
    return 0x1F3FB <= cp <= 0x1F3FF

def _is_regional(cp):
    return 0x1F1E6 <= cp <= 0x1F1FF

def _is_tag(cp):
    return 0xE0020 <= cp <= 0xE007F

def _is_zwj(cp):
    return cp == 0x200D

def _is_keycap(cp):
    return cp == 0x20E3

# Bases that start an emoji cluster. Includes emoji-capable BMP symbols (❤️, ©️, ☺️)
# and the supplemental emoji blocks. Latin-1 symbols such as © are only treated as
# a base when a variation selector or keycap follows (see _emoji_end).
_EMOJI_RANGES = (
    (0x203C, 0x203C), (0x2049, 0x2049),
    (0x2122, 0x2122), (0x2139, 0x2139),
    (0x2194, 0x2199), (0x21A9, 0x21AA),
    (0x231A, 0x231B), (0x2328, 0x2328), (0x23CF, 0x23CF),
    (0x23E9, 0x23F3), (0x23F8, 0x23FA),
    (0x24C2, 0x24C2),
    (0x25AA, 0x25AB), (0x25B6, 0x25B6), (0x25C0, 0x25C0), (0x25FB, 0x25FE),
    (0x2600, 0x27BF),
    (0x2934, 0x2935),
    (0x2B05, 0x2B07), (0x2B1B, 0x2B1C), (0x2B50, 0x2B50), (0x2B55, 0x2B55),
    (0x3030, 0x3030), (0x303D, 0x303D), (0x3297, 0x3297), (0x3299, 0x3299),
    (0x1F000, 0x1FFFF),
)
_VS_ONLY_BASES = {0x00A9, 0x00AE, 0x2122}  # © ® ™ — weight 1 unless presented as emoji

def _is_emoji_base(cp):
    if cp in _VS_ONLY_BASES:
        return True
    for a, b in _EMOJI_RANGES:
        if a <= cp <= b:
            return True
    return False

def _take_modifiers(s, j):
    """Consume optional FE0F / skin tone after a base. Returns new index."""
    n = len(s)
    if j < n and _is_vs(ord(s[j])):
        j += 1
    if j < n and _is_skin(ord(s[j])):
        j += 1
        if j < n and _is_vs(ord(s[j])):
            j += 1
    return j

def _emoji_end(s, i):
    """If s[i:] starts with an emoji cluster, return the index after it, else None.

    A cluster is one emoji as X counts it: a ZWJ sequence, a flag, a keycap,
    a tag sequence (e.g. 🏴󠁧󠁢󠁥󠁮󠁧󠁿), or a single emoji with optional variation
    selector and skin tone. The whole cluster weighs 2.
    """
    n = len(s)
    if i >= n:
        return None
    cp = ord(s[i])

    # Flag: two regional indicators.
    if _is_regional(cp) and i + 1 < n and _is_regional(ord(s[i + 1])):
        return i + 2

    # Subdivision flag: 🏴 + tag characters + cancel tag (U+E007F).
    if cp == 0x1F3F4 and i + 1 < n and _is_tag(ord(s[i + 1])):
        j = i + 1
        while j < n and _is_tag(ord(s[j])) and ord(s[j]) != 0xE007F:
            j += 1
        if j < n and ord(s[j]) == 0xE007F:
            return j + 1

    # Keycap: [0-9#*] + optional VS + combining enclosing keycap.
    if s[i] in "0123456789#*" and i + 1 < n:
        j = i + 1
        if j < n and _is_vs(ord(s[j])):
            j += 1
        if j < n and _is_keycap(ord(s[j])):
            return j + 1

    if not _is_emoji_base(cp):
        return None
    # © / ® alone are Latin-1 (weight 1); only cluster them with a VS or keycap.
    if cp in _VS_ONLY_BASES:
        if i + 1 < n and (_is_vs(ord(s[i + 1])) or _is_keycap(ord(s[i + 1]))):
            return _take_modifiers(s, i + 1)
        return None

    j = _take_modifiers(s, i + 1)
    # ZWJ continuations (families, professions, etc.).
    while j < n and _is_zwj(ord(s[j])):
        k = j + 1
        if k >= n:
            break
        nxt = ord(s[k])
        if _is_regional(nxt) and k + 1 < n and _is_regional(ord(s[k + 1])):
            j = k + 2
            continue
        if not _is_emoji_base(nxt) and nxt not in _VS_ONLY_BASES:
            break
        j = _take_modifiers(s, k + 1)
    return j

# Host labels: ASCII LDH, or an IDN label of unicode letters (no punctuation,
# so a preceding "(" is not swallowed into the domain).
_LABEL = r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?|[^\W\d_](?:[^\W_]*[^\W\d_])?)"
_TLD_RE = "|".join(re.escape(t) for t in sorted(_TLDS, key=len, reverse=True))
# Preceding char cannot be something that would glue the URL into a token.
_URL_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9@._-])"
    r"((?:https?://|www\.)?"
    r"(?:%s\.)+(?:%s)(?=[^0-9A-Za-z@+-]|$)"
    r"(?::\d{2,5})?"
    r"(?:/[^\s]*)?)" % (_LABEL, _TLD_RE)
)

def _trim_url(u):
    # Stop at an unmatched closing paren/bracket in the path
    # (X does not include "https://example.com/a)b"'s ")b" in the URL).
    depth_p = depth_b = 0
    cut = len(u)
    for i, ch in enumerate(u):
        if ch == "(":
            depth_p += 1
        elif ch == ")":
            if depth_p == 0:
                cut = i
                break
            depth_p -= 1
        elif ch == "[":
            depth_b += 1
        elif ch == "]":
            if depth_b == 0:
                cut = i
                break
            depth_b -= 1
    u = u[:cut]
    # Peel trailing punctuation (dots, commas, ...). Commas inside a query stay.
    while u and u[-1] in _TRAIL:
        u = u[:-1]
    while u and u[-1] == ")" and u.count("(") < u.count(")"):
        u = u[:-1]
    while u and u[-1] == "]" and u.count("[") < u.count("]"):
        u = u[:-1]
    while u and u[-1] in "'\"":
        q = u[-1]
        if u.count(q) % 2 == 1:
            u = u[:-1]
        else:
            break
    return u

def iter_urls(text):
    """Yield (start, end) spans of URLs as X would t.co-wrap them."""
    for m in _URL_RE.finditer(text):
        raw = m.group(1)
        # file://example.com should not count the scheme-less host? Skip file:
        # We never match a file: scheme (only http, https, www, or bare).
        trimmed = _trim_url(raw)
        if not trimmed:
            continue
        # Require a real TLD in the host part (the regex already does).
        yield m.start(1), m.start(1) + len(trimmed)

def extract_urls(text):
    return [text[a:b] for a, b in iter_urls(text)]

def weight(text):
    """Weighted length of a post, matching twitter-text v3 with emoji parsing."""
    # Punch URLs out first so their characters are not also counted.
    marks = []
    for a, b in iter_urls(text):
        marks.append((a, b))
    n = 0
    i = 0
    url_at = {a: b for a, b in marks}
    L = len(text)
    while i < L:
        if i in url_at:
            n += 23
            i = url_at[i]
            continue
        end = _emoji_end(text, i)
        if end is not None:
            n += 2
            i = end
            continue
        n += _unit(ord(text[i]))
        i += 1
    return n

# http(s) or www. — used to decide when to warn about a "link in a main post".
# Bare example.com in a command is still counted as 23, but isn't a posted link.
_EXPLICIT_LINK = re.compile(r"(?i)https?://|www\.")

BAIT = ["rt if", "retweet if", "like if", "follow for", "follow me", "drop a", "comment below",
        "who else", "smash", "don't miss", "you won't believe", "game changer", "game-changer", "🧵👇"]

def lint(posts, facts=None, long_posts=False):
    errs = warns = 0
    lines = []
    for i, p in enumerate(posts, 1):
        is_reply = p.startswith("REPLY:")
        body = p[len("REPLY:"):].strip() if is_reply else p
        w = weight(body); tag = "reply" if is_reply else f"post {i}"
        msgs = []
        if w > 280:
            if long_posts: msgs.append(("WARN", f"{w} chars (over 280, OK only on Premium)"))
            else: msgs.append(("ERROR", f"{w} chars > 280"))
        if len(re.findall(r"(?<!\w)#\w+", body)) > 1: msgs.append(("ERROR", "more than 1 hashtag"))
        if len(re.findall(r"(?<!\w)@\w+", body)) > 2: msgs.append(("WARN", "3+ @mentions reads as spam"))
        low = body.lower()
        for b in BAIT:
            if b in low: msgs.append(("ERROR", f"engagement bait: '{b}'"))
        if _EXPLICIT_LINK.search(body) and not is_reply:
            msgs.append(("WARN", "link in a main post; consider moving it to the REPLY"))
        if facts:
            for num in re.findall(r"\b\d[\d,.]*k?\b", body):
                core = num.rstrip(".,")
                if len(core) >= 2 and core not in facts and core.replace(",", "") not in facts:
                    msgs.append(("WARN", f"number '{core}' not found in facts.json; verify or remove"))
        lines.append(f"[{tag}] {w}/280" + ("" if msgs else "  ok"))
        for lvl, m in msgs:
            lines.append(f"   {lvl}: {m}")
            errs += lvl == "ERROR"; warns += lvl == "WARN"
    lines.append(f"\n{len(posts)} posts, {errs} errors, {warns} warnings")
    return "\n".join(lines) + "\n", errs

def split_posts(text):
    return [p.strip() for p in re.split(r"^\s*---\s*$", text, flags=re.M) if p.strip()]

def self_test():
    # Cases checked against twitter-text 3.1.0 parseTweet().weightedLength, plus
    # modern ZWJ emoji (🧑‍💻) that library's 2020 emoji data missed and X counts as 2.
    cases = {
        "hello": 5,
        "https://github.com/foo/bar": 23,
        "https://github.com/foo/bar.": 24,
        "See https://github.com/foo/bar.": 28,
        "😀": 2,
        "❤️": 2,
        "❤": 2,
        "👨‍👩‍👧‍👦": 2,
        "🇺🇸": 2,
        "👍🏾": 2,
        "1️⃣": 2,
        "©": 1,
        "©️": 2,
        "你": 2,
        "e": 1,
        "café": 4,
        "agent-browser open example.com": 42,
        "Docs: https://agent-browser.dev": 29,
        "Repo: https://github.com/vercel-labs/agent-browser\nDocs: https://agent-browser.dev": 59,
        "Visit www.example.com today": 35,
        "www.example.com": 23,
        "example.com": 23,
        "foo.dev/path": 23,
        "a.com.": 24,
        "Hello 👋 world": 14,
        "✨": 2,
        "☺️": 2,
        "🇬🇧": 2,
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿": 2,
        "👩‍🚀": 2,
        "👨‍👩‍👧": 2,
        "#️⃣": 2,
        "3.14": 4,
        "100": 3,
        "a" * 280: 280,
        "https://x.com/foo https://x.com/bar": 47,
        "Check (https://example.com).": 32,
        "https://example.com/path?q=1&x=2": 23,
        "mailto:x@y.com": 14,
        "http://example.com": 23,
        "HTTP://EXAMPLE.COM": 23,
        "https://example.com/foo.": 24,
        "https://example.com/foo...": 26,
        "go to example.com, then stop": 40,
        "file://foo": 10,
        "t.co/abc": 23,
        "https://t.co/abc": 23,
        "x.com": 23,
        "github.com/foo": 23,
        "not a.sentence": 14,
        "OK.Sure": 7,
        "end.org": 23,
        "foo.bar": 23,
        "test.ai": 23,
        "foo.sh": 23,
        "foo.io/x": 23,
        "sub.domain.co.uk": 23,
        "https://sub.domain.co.uk/a": 23,
        "see example.com/path?x=1,y=2": 27,
        "https://example.com/a)b": 25,
        "(https://example.com)": 25,
        "https://example.com)": 24,
        "v0.42.0": 7,
        "48.9k": 5,
        "191.9k": 6,
        "node.js": 7,
        "index.html": 10,
        "readme.md": 23,
        "foo.py": 23,
        "a.b": 3,
        "🧑‍💻": 2,
    }
    failed = 0
    for text, expect in cases.items():
        got = weight(text)
        if got != expect:
            print(f"FAIL {got} != {expect}: {text!r}")
            failed += 1
    print(f"{len(cases) - failed}/{len(cases)} passed")
    return failed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("thread", nargs="?")
    ap.add_argument("--facts")
    ap.add_argument("--long-posts", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if not a.thread:
        ap.error("thread.md is required (or pass --self-test)")
    posts = split_posts(open(a.thread).read())
    facts = open(a.facts).read() if a.facts else None
    report, errs = lint(posts, facts, a.long_posts)
    sys.stdout.write(report)
    sys.exit(1 if errs else 0)

if __name__ == "__main__":
    main()

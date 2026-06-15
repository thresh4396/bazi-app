"""八字综合分析引擎，引用经典典籍"""

from calculator import *
from data.wuxing import *

# ===== 经典典籍核心规则 =====

# 穷通宝典：各日干十二月调候用神
QIONGTONG = {
    "甲": {1:"丙癸", 2:"丙癸", 3:"庚丁", 4:"癸丁庚", 5:"癸庚丁", 6:"癸庚丁", 7:"丁庚", 8:"丁丙", 9:"甲丙庚", 10:"丙戊庚", 11:"丁庚丙", 12:"丙丁"},
    "乙": {1:"丙癸", 2:"丙癸", 3:"癸戊", 4:"癸辛丙", 5:"癸丙", 6:"癸丙", 7:"癸丙己", 8:"癸丙丁", 9:"癸辛金", 10:"丙丁", 11:"丙戊", 12:"丙火"},
    "丙": {1:"壬庚", 2:"壬己", 3:"壬甲", 4:"壬庚癸", 5:"壬庚", 6:"壬庚", 7:"壬戊", 8:"壬癸", 9:"甲壬", 10:"甲壬", 11:"壬戊己", 12:"壬甲"},
    "丁": {1:"甲庚", 2:"庚甲", 3:"甲庚", 4:"甲庚癸", 5:"壬庚癸", 6:"甲壬庚", 7:"甲庚丙", 8:"甲庚丙", 9:"甲庚戊", 10:"甲庚戊", 11:"甲庚", 12:"甲庚"},
    "戊": {1:"丙甲癸", 2:"丙甲癸", 3:"甲丙癸", 4:"甲丙癸", 5:"壬甲丙", 6:"癸丙甲", 7:"丙癸甲", 8:"丙癸", 9:"甲丙癸", 10:"甲丙", 11:"丙甲", 12:"丙甲"},
    "己": {1:"丙庚甲", 2:"甲丙癸", 3:"丙甲癸", 4:"癸丙辛", 5:"癸丙辛", 6:"癸丙辛", 7:"丙癸", 8:"丙癸", 9:"丙癸", 10:"丙甲戊", 11:"丙甲", 12:"丙甲"},
    "庚": {1:"丙甲", 2:"丁甲庚", 3:"甲庚丁", 4:"壬丙戊", 5:"壬癸", 6:"丁甲", 7:"丁甲", 8:"丁丙", 9:"甲壬", 10:"甲壬", 11:"丙火", 12:"丙丁"},
    "辛": {1:"己壬庚", 2:"壬甲", 3:"壬甲", 4:"壬甲癸", 5:"壬甲己", 6:"壬庚", 7:"壬甲戊", 8:"壬甲", 9:"壬甲戊", 10:"壬丙", 11:"丙壬戊", 12:"丙壬"},
    "壬": {1:"庚丙戊", 2:"戊辛庚", 3:"甲庚", 4:"壬辛", 5:"癸庚辛", 6:"辛甲", 7:"戊丁", 8:"丁丙", 9:"戊丁", 10:"戊丙庚", 11:"丙戊", 12:"丙火"},
    "癸": {1:"辛丙", 2:"丙辛", 3:"丙辛甲", 4:"壬辛", 5:"庚壬癸", 6:"庚辛", 7:"丁", 8:"辛丙", 9:"辛甲壬", 10:"戊辛", 11:"丙辛", 12:"丙辛"},
}

# 十神所代表的性格
SHISHEN_CHARACTER = {
    "比肩": "独立自主，自尊心强，重朋友义气",
    "劫财": "热情豪爽，竞争心强，但易冲动用事",
    "食神": "温和宽厚，有艺术才华，热爱生活享受",
    "伤官": "聪明才智，个性张扬，不拘一格有创意",
    "偏财": "慷慨大方，善于投资理财，不喜拘束",
    "正财": "勤俭持家，重视物质安全感，务实稳重",
    "七杀": "果断刚毅，有魄力冲劲，但压力大易急躁",
    "正官": "正直负责，守法守纪，注重名誉和形象",
    "偏印": "思维独特，喜欢钻研冷门学问，有时孤僻",
    "正印": "温文尔雅，乐于助人，重视精神生活",
}

# 五行性格
WUXING_CHARACTER = {
    "木": "仁慈善良，有进取心，性格直率，有时固执",
    "火": "热情洋溢，行动迅速，礼节周到，容易急躁",
    "土": "诚实守信，稳重踏实，包容力强，稍嫌保守",
    "金": "刚毅果断，讲义气，重视规则，有时冷酷",
    "水": "聪明灵活，善于变通，富有智慧，但容易犹豫",
}

# 十神事业方向
SHISHEN_CAREER = {
    "正官": "公务员、行政管理、法律、教育",
    "七杀": "军警、安保、外科医生、竞技体育",
    "正印": "教师、研究员、出版、文化传播",
    "偏印": "玄学、科研、技术、专精领域",
    "正财": "金融会计、固定工资、传统商贸",
    "偏财": "投资、贸易、自由职业、销售",
    "食神": "餐饮美食、艺术设计、演艺、写作",
    "伤官": "创意策划、技艺表演、科技创新",
    "比肩": "合伙创业、体力劳动、职业运动员",
    "劫财": "保险推销、娱乐服务、新兴行业",
}


def analyze_full(chart):
    """生成完整命盘分析报告"""
    ec = chart["eight_char"]
    ri_gan = chart["ri_gan"]
    ri_zhi = chart["ri_zhi"]
    month_zhi = ec["month"]["zhi"]
    season = get_season(month_zhi)

    parts = []

    # === 1. 日主分析 ===
    parts.append(_analyze_rizhu(chart))

    # === 2. 五行平衡 ===
    parts.append(_analyze_wuxing(chart))

    # === 3. 格局 ===
    parts.append(_analyze_geju(chart))

    # === 4. 性格 ===
    parts.append(_analyze_character(chart))

    # === 5. 事业 ===
    parts.append(_analyze_career(chart))

    # === 6. 财运 ===
    parts.append(_analyze_wealth(chart))

    # === 7. 婚姻 ===
    parts.append(_analyze_marriage(chart))

    # === 8. 健康 ===
    parts.append(_analyze_health(chart))

    # === 9. 大运 ===
    parts.append(_analyze_dayun(chart))

    # === 10. 当前流年 ===
    parts.append(_analyze_current_year(chart))

    return parts


def analyze_topic(chart, topic):
    """针对特定话题进行深入分析"""
    topic_map = {
        "事业": _analyze_career,
        "财运": _analyze_wealth,
        "婚姻": _analyze_marriage,
        "感情": _analyze_marriage,
        "健康": _analyze_health,
        "性格": _analyze_character,
        "大运": _analyze_dayun,
        "流年": _analyze_current_year,
        "格局": _analyze_geju,
        "用神": _analyze_yongshen,
        "喜用": _analyze_yongshen,
        "学业": _analyze_study,
        "出国": _analyze_abroad,
        "方位": _analyze_direction,
        "行业": _analyze_career,
        "离婚": _analyze_marriage,
        "子女": _analyze_children,
    }
    func = topic_map.get(topic)
    if func:
        return func(chart)
    return _general_qa(chart, topic)


def _analyze_rizhu(chart):
    ec = chart["eight_char"]
    ri_gan = chart["ri_gan"]
    wx = TIAN_GAN_WUXING[ri_gan]
    yy = TIAN_GAN_YINYANG[ri_gan]
    ws = chart["wangshuai"]

    return {
        "title": "🌊 日主分析",
        "content": f"""**日主：{ri_gan}{wx}（{yy}{wx}）**

日主{ri_gan}在命局中{ws['detail']}。

按《滴天髓》旺衰判断原则：日干在月令处于旺相之地则为"得令"（最重要），在地支中有同五行根气则为"得地"，在天干有比劫印生扶则为"得势"。三得之中，得令最为关键。

{ri_gan}{wx}生于{get_season(ec['month']['zhi'])}季，五行属{wx}，{_get_wx_nature(wx)}。日主{ws['level']}，{'身强能任财官' if ws['level'] in ['身旺','中和偏旺'] else '需要印比扶助'}。"""
    }


def _analyze_wuxing(chart):
    wc = chart["wuxing_count"]
    xiyong = chart["xiyong"]

    lines = ["**五行力量分布：**\n"]
    for wx in ["金","木","水","火","土"]:
        bar = "█" * int(wc[wx] * 2)
        lines.append(f"- {wx}: {bar} ({wc[wx]:.1f})")

    lines.append(f"\n**最强五行**：{xiyong['strongest']}")
    lines.append(f"**最弱五行**：{xiyong['weakest']}")
    lines.append(f"\n**喜用神**：{'、'.join(xiyong['xi_shen'])}（对日主有利的五行）")
    lines.append(f"**忌神**：{'、'.join(xiyong.get('ji_shen', []))}（对日主不利的五行）")

    return {
        "title": "⚖️ 五行分析",
        "content": "\n".join(lines)
    }


def _analyze_geju(chart):
    ec = chart["eight_char"]
    month_zhi = ec["month"]["zhi"]
    ri_gan = chart["ri_gan"]

    # 取月支藏干本气为格
    main_cg = CANG_GAN[month_zhi][0][0]
    ss = get_shi_shen(ri_gan, main_cg)

    lines = [
        f"**月令格局：{ss}格**",
        f"\n月支{month_zhi}藏{main_cg}（{ss}）为本气，以月令透干取格。",
        f"\n按《子平真诠》论格局之法：月令为纲，四柱为辅。{ss}格需看是否透出天干、有无辅助、有无破格之物。",
    ]

    return {
        "title": "📐 格局判定",
        "content": "\n".join(lines),
    }


def _analyze_character(chart):
    ec = chart["eight_char"]
    ri_gan = chart["ri_gan"]
    wx = TIAN_GAN_WUXING[ri_gan]

    lines = [f"**日主{ri_gan}{wx}的五行性格：**", f"\n{WUXING_CHARACTER.get(wx, '')}"]

    # 各柱十神对性格影响
    for pillar, name in [("month","月柱"), ("hour","时柱")]:
        ss = ec[pillar]["shishen"]
        if ss in SHISHEN_CHARACTER:
            lines.append(f"\n**{name}十神（{ss}）**：{SHISHEN_CHARACTER[ss]}")

    return {
        "title": "🧠 性格特征",
        "content": "\n".join(lines)
    }


def _analyze_career(chart):
    ec = chart["eight_char"]
    ri_gan = chart["ri_gan"]
    ri_wx = TIAN_GAN_WUXING[ri_gan]
    xiyong = chart["xiyong"]
    ws = chart["wangshuai"]
    month_ss = ec["month"]["shishen"]
    hour_ss = ec["hour"]["shishen"]
    all_gan = chart["all_gan"]
    all_zhi = chart["all_zhi"]

    lines = [f"**事业方向综合分析：**\n"]

    # 1. 格局取向
    lines.append(f"**格局**：月令{month_ss}格，时柱{hour_ss}透干。")
    # 食伤旺则适合技术/创意，官印旺则适合管理/学术
    has_shishang = any(get_shi_shen(ri_gan, g) in ["食神","伤官"] for g in all_gan)
    has_guan = any(get_shi_shen(ri_gan, g) in ["正官","七杀"] for g in all_gan)
    has_yin = any(get_shi_shen(ri_gan, g) in ["正印","偏印"] for g in all_gan)

    if has_shishang:
        lines.append(f"食伤吐秀格倾向 → **技术型/专家型**路线，靠专业能力立身，不宜做纯管理或纯社交类工作。")
    if has_yin:
        lines.append(f"印星加持 → 适合需要深度学习和证书背书的领域。")

    lines.append("")

    # 2. 喜用神行业（最重要）
    lines.append(f"**喜用神**：{'、'.join(xiyong['xi_shen'])} → 以下行业最为匹配：")

    direction_map = {
        "金": "矿业、金属冶炼、精密机械、科技硬件、工程师、金融精算、法律、数据分析",
        "水": "贸易物流、航运、传媒、教育科研、咨询顾问、软件开发、人工智能",
        "木": "文化教育、医疗健康、环保、创意设计、出版",
        "火": "能源电力、互联网运营、市场营销、电子通信",
        "土": "房地产、建筑、农业、行政管理、监理",
    }
    for x in xiyong["xi_shen"]:
        if x in direction_map:
            lines.append(f"- **喜{x}** → {direction_map[x]}")

    # 3. 忌神规避
    if xiyong.get("ji_shen"):
        lines.append(f"\n**忌神**：{'、'.join(xiyong['ji_shen'])} → 相关行业需谨慎：")
        for j in xiyong["ji_shen"]:
            if j in direction_map:
                lines.append(f"- 忌**{j}** → {direction_map[j]}（易消耗精力而回报少）")

    # 4. 身强弱建议
    lines.append("")
    if ws["level"] in ["身弱","中和偏弱"]:
        lines.append(f"日主{ws['level']} → **不宜高强度高压**岗位。适合做精深的专家而非面面俱到的管理者。先深耕一门技术，再图扩展。")
    else:
        lines.append(f"日主{ws['level']} → 能扛事，适合需要决断力和承担责任的位置。")

    # 5. 十神性格与工作风格
    lines.append(f"\n**工作风格**：")
    for pillar, name in [("month","月柱"), ("hour","时柱")]:
        ss = ec[pillar]["shishen"]
        if ss in SHISHEN_CHARACTER:
            lines.append(f"- {name}**{ss}**：{SHISHEN_CHARACTER[ss]}")

    # 6. 综合推荐
    lines.append(f"\n**综合推荐路径**：")
    xi_list = xiyong["xi_shen"]
    if "金" in xi_list and "水" in xi_list:
        lines.append("金水双用 → **科技/工程/数据 + 教育/咨询** 的复合路线最为理想。先以金（硬技能）立足，再以水（智慧灵活）拓宽。")
    elif "金" in xi_list:
        lines.append("以**金**为主 → 深耕技术/工程领域，积累硬实力。")
    elif "水" in xi_list:
        lines.append("以**水**为主 → 发挥智慧灵活的优势，适合知识密集型行业。")

    return {
        "title": "💼 事业方向",
        "content": "\n".join(lines)
    }


def _analyze_wealth(chart):
    ec = chart["eight_char"]
    ri_gan = chart["ri_gan"]
    ws = chart["wangshuai"]

    lines = []
    lines.append(f"日主{ws['level']}，{'身强能任财' if ws['level'] in ['身旺','中和偏旺'] else '身弱需先强身再求财'}。")

    # 看正财偏财位置
    for pillar, name in [("year","年柱"), ("month","月柱"), ("day","日柱"), ("hour","时柱")]:
        ss = ec[pillar]["shishen"]
        if ss in ["正财", "偏财"]:
            lines.append(f"\n{name}见**{ss}**：{'早年财运' if name == '年柱' else '中年求财' if name == '日柱' else '晚年财运'}")

    lines.append(f"\n按《神峰通考》病药说：{'身强财旺为吉' if ws['level'] in ['身旺','中和偏旺'] else '身弱须待帮扶大运方能担财'}。")

    return {
        "title": "💰 财运分析",
        "content": "\n".join(lines)
    }


def _analyze_marriage(chart):
    ec = chart["eight_char"]
    ri_gan = chart["ri_gan"]
    ri_zhi = chart["ri_zhi"]
    gender = chart["gender"]

    lines = [f"**配偶宫：日支{ri_zhi}**"]
    lines.append(f"\n{ri_zhi}中藏：{'、'.join([g + '(' + l + ')' for g, l in ec['day']['canggan']])}")

    # 男女看不同
    if gender == "男":
        # 看正财（妻）
        for pillar, name in [("year","年柱"), ("month","月柱"), ("day","日柱"), ("hour","时柱")]:
            ss = ec[pillar]["shishen"]
            if ss in ["正财", "偏财"]:
                lines.append(f"\n{name}见**{ss}**，{'正财为妻，早见早婚' if ss == '正财' and name in ['年柱','月柱'] else '偏财为异性缘' if ss == '偏财' else ''}")
        lines.append(f"\n配偶宫{ri_zhi}，{'寅申巳亥为四马之地，配偶性格外向活泼' if ri_zhi in ['寅','申','巳','亥'] else '子午卯酉为四正之地，配偶品貌端正' if ri_zhi in ['子','午','卯','酉'] else '辰戌丑未为四库之地，配偶性格稳重包容'}")
    else:
        # 看正官（夫）
        for pillar, name in [("year","年柱"), ("month","月柱"), ("day","日柱"), ("hour","时柱")]:
            ss = ec[pillar]["shishen"]
            if ss in ["正官", "七杀"]:
                lines.append(f"\n{name}见**{ss}**，{'正官为夫，早见早婚' if ss == '正官' and name in ['年柱','月柱'] else '七杀为偏夫'}")
        lines.append(f"\n按《渊海子平》：女命以正官为夫星。官星一位为清贵，多则情缘复杂。")

    return {
        "title": "💔 婚姻分析",
        "content": "\n".join(lines)
    }


def _analyze_health(chart):
    ri_gan = chart["ri_gan"]
    wx = TIAN_GAN_WUXING[ri_gan]

    body_map = {
        "金": "肺、大肠、呼吸道、皮肤、骨骼",
        "水": "肾、膀胱、泌尿系统、听力",
        "木": "肝、胆、筋、神经系统",
        "火": "心、小肠、血液循环、眼睛",
        "土": "脾、胃、消化系统、肌肉",
    }

    xiyong = chart["xiyong"]

    lines = [
        f"**日主{ri_gan}{wx}的身体薄弱点：**",
        f"\n{wx}主**{body_map.get(wx, '')}**，日主{'强' if chart['wangshuai']['level'] in ['身旺','中和偏旺'] else '弱'}，{'以上部位先天较强' if chart['wangshuai']['level'] in ['身旺','中和偏旺'] else '以上部位需多加保养'}。",
        f"\n\n忌神{'、'.join(xiyong.get('ji_shen', []))}过旺时相关脏腑易受克：",
    ]

    for j in xiyong.get("ji_shen", []):
        if j in body_map:
            lines.append(f"- {j}主{body_map[j]}")

    return {
        "title": "🏥 健康分析",
        "content": "\n".join(lines)
    }


def _analyze_dayun(chart):
    dayun = chart["dayun"]
    lines = [
        f"**起运年龄**：{dayun['qiyun_age']}岁",
        f"**大运方向**：{dayun['direction']}（阳年男/阴年女顺排，阴年男/阳年女逆排）\n",
    ]

    lines.append("| 大运 | 年龄 | 干支 | 天干 | 地支 |")
    lines.append("|------|------|------|------|------|")
    for dy in dayun["dayun_list"]:
        lines.append(f"| 第{dy['index']}步 | {dy['age_range']} | {dy['gan_zhi']} | {dy['gan']} | {dy['zhi']} |")

    return {
        "title": "📅 大运排列",
        "content": "\n".join(lines)
    }


def _analyze_current_year(chart):
    """当前流年分析"""
    solar = chart["solar"]
    today = date.today()
    birth_date = date(solar.getYear(), solar.getMonth(), solar.getDay())
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1

    liunian = get_liunian(solar, today.year)
    current_dy = get_current_dayun(chart["dayun"], age) or chart["dayun"]["dayun_list"][0]

    lines = [
        f"**当前年龄**：{age}岁",
        f"**当前大运**：{current_dy['gan_zhi']}（{current_dy['age_range']}）",
        f"**{today.year}流年**：{liunian['gan_zhi']}",
    ]

    return {
        "title": "🔮 当前运势",
        "content": "\n".join(lines)
    }


def _analyze_yongshen(chart):
    xiyong = chart["xiyong"]
    lines = [
        "根据《渊海子平》用神取法：",
        "1. 扶抑：身弱扶之，身旺抑之",
        "2. 调候：寒暖燥湿需调节",
        "3. 通关：两行交战取通关之物",
        "4. 顺势：从格则顺其势",
        f"\n**本命喜用神**：{'、'.join(xiyong['xi_shen'])}",
        f"**本命忌神**：{'、'.join(xiyong.get('ji_shen', []))}",
    ]
    return {
        "title": "🎯 用神分析",
        "content": "\n".join(lines)
    }


def _analyze_study(chart):
    ec = chart["eight_char"]
    ri_gan = chart["ri_gan"]

    # 看正印偏印
    lines = ["印星代表学业、学历、贵人。"]

    for pillar, name in [("year","年柱"), ("month","月柱"), ("day","日柱"), ("hour","时柱")]:
        ss = ec[pillar]["shishen"]
        if ss in ["正印", "偏印"]:
            lines.append(f"\n{name}见**{ss}**：学业运势{'早年聪明' if name == '年柱' else '中年求学' if name in ['月柱','日柱'] else '终身学习'}")

    if not any(ec[p]["shishen"] in ["正印","偏印"] for p in ["year","month","day","hour"]):
        lines.append("\n命局缺印星，学业需后天努力补足，大运逢金（印）时学业有成。")

    return {
        "title": "📚 学业分析",
        "content": "\n".join(lines)
    }


def _analyze_abroad(chart):
    shensha = chart["shensha"]
    ec = chart["eight_char"]

    lines = ["驿马星代表走动、迁移、出国。"]
    if shensha["驿马"]:
        lines.append(f"\n本命驿马在：{'、'.join(shensha['驿马'])}，天生有出远门的倾向。")

    # 食伤旺也主动
    ri_gan = chart["ri_gan"]
    for p in ["year","month","day","hour"]:
        ss = ec[p]["shishen"]
        if ss in ["食神", "伤官"]:
            lines.append(f"\n{p}柱见**{ss}**，食伤主动，有向外发展的欲望。")

    return {
        "title": "✈️ 出行/出国",
        "content": "\n".join(lines)
    }


def _analyze_direction(chart):
    xiyong = chart["xiyong"]
    dir_map = {
        "金": "西方（欧美）",
        "水": "北方（中国北方、加拿大北部）",
        "木": "东方（中国东部、日本）",
        "火": "南方（东南亚、澳洲南部）",
        "土": "中部（内陆、中原）",
    }

    lines = ["根据喜用神五行对应的方位："]
    for x in xiyong["xi_shen"]:
        lines.append(f"- **喜{x}** → 适合 **{dir_map.get(x, '')}**")

    for j in xiyong.get("ji_shen", []):
        lines.append(f"- **忌{j}** → 避开 **{dir_map.get(j, '')}**")

    return {
        "title": "🧭 方位吉凶",
        "content": "\n".join(lines)
    }


def _analyze_children(chart):
    ri_gan = chart["ri_gan"]
    ec = chart["eight_char"]
    gender = chart["gender"]

    if gender == "女":
        lines = ["女命以食神/伤官为子女。"]
        for p, n in [("year","早年"),("month","青年"),("day","中年"),("hour","晚年")]:
            ss = ec[p]["shishen"]
            if ss in ["食神","伤官"]:
                lines.append(f"\n{n}见**{ss}**于{p}柱。")
    else:
        lines = ["男命以官杀为子女（传统以七杀为子、正官为女）。"]
        for p, n in [("year","早年"),("month","青年"),("day","中年"),("hour","晚年")]:
            ss = ec[p]["shishen"]
            if ss in ["正官","七杀"]:
                lines.append(f"\n{n}见**{ss}**于{p}柱。")

    return {
        "title": "👶 子女分析",
        "content": "\n".join(lines)
    }


def _general_qa(chart, question):
    """通用问答"""
    return {
        "title": f"💬 关于：{question}",
        "content": f"根据您的命盘（日主{chart['ri_gan']}，{chart['wangshuai']['level']}），「{question}」这个问题涉及命盘的多个方面。建议您点击具体话题按钮查看详细分析，或者追问更具体的内容。"
    }


def _get_wx_nature(wx):
    natures = {
        "木": "仁慈善良，有进取心",
        "火": "热情洋溢，行动迅速",
        "土": "诚实守信，稳重踏实",
        "金": "刚毅果断，讲义气",
        "水": "聪明灵活，善于变通",
    }
    return natures.get(wx, "")

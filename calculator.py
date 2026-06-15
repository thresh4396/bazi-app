"""八字排盘核心计算引擎"""

from datetime import date, timedelta
from lunar_python import Solar, Lunar
from data.wuxing import *

def calc_from_solar(year, month, day, hour=0, minute=0, gender="男"):
    """
    根据阳历日期时间计算完整八字命盘
    返回 dict 包含四柱、十神、藏干、大运等所有信息
    """
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()

    # 获取八字
    bazi = lunar.getEightChar()

    # 四柱干支
    year_gan = bazi.getYearGan()
    year_zhi = bazi.getYearZhi()
    month_gan = bazi.getMonthGan()
    month_zhi = bazi.getMonthZhi()
    day_gan = bazi.getDayGan()
    day_zhi = bazi.getDayZhi()

    # 时柱（根据出生时间计算）
    hour_zhi = _get_hour_zhi(hour, minute)
    hour_gan = get_hour_stem(day_gan, DI_ZHI.index(hour_zhi))

    # 藏干
    hg_year = CANG_GAN[year_zhi]
    hg_month = CANG_GAN[month_zhi]
    hg_day = CANG_GAN[day_zhi]
    hg_hour = CANG_GAN[hour_zhi]

    # 十神（以日干为中心）
    shishen_year = get_shi_shen(day_gan, year_gan)
    shishen_month = get_shi_shen(day_gan, month_gan)
    shishen_day = "日主"
    shishen_hour = get_shi_shen(day_gan, hour_gan)

    # 纳音
    nayin_year = get_na_yin(year_gan + year_zhi)
    nayin_month = get_na_yin(month_gan + month_zhi)
    nayin_day = get_na_yin(day_gan + day_zhi)
    nayin_hour = get_na_yin(hour_gan + hour_zhi)

    # 十二长生
    c_year = _get_chang_sheng_state(day_gan, year_zhi)
    c_month = _get_chang_sheng_state(day_gan, month_zhi)
    c_day = _get_chang_sheng_state(day_gan, day_zhi)
    c_hour = _get_chang_sheng_state(day_gan, hour_zhi)

    # 五行统计
    all_gan = [year_gan, month_gan, day_gan, hour_gan]
    all_zhi = [year_zhi, month_zhi, day_zhi, hour_zhi]
    wuxing_count = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    for g in all_gan:
        wuxing_count[TIAN_GAN_WUXING[g]] += 1
    for z in all_zhi:
        wuxing_count[DI_ZHI_WUXING[z]] += 1
    # 藏干加权
    for z in all_zhi:
        for cg, level in CANG_GAN[z]:
            w = 0.6 if level == "本气" else (0.3 if level == "中气" else 0.1)
            wuxing_count[TIAN_GAN_WUXING[cg]] += w

    # 地支关系
    relations = _find_relations(all_zhi)

    # 大运
    dayun = _calc_dayun(solar, lunar, year_gan, month_gan, month_zhi, gender)

    # 日主旺衰
    wangshuai = _calc_wangshuai(day_gan, month_zhi, all_gan, all_zhi, wuxing_count)

    # 喜用神
    xiyong = _calc_xiyong(day_gan, month_zhi, wuxing_count, wangshuai["level"])

    # 神煞
    shensha = {
        "天乙贵人": get_tian_yi_gui_ren(day_gan),
        "桃花": get_tao_hua(year_zhi, day_zhi),
        "驿马": get_yi_ma(year_zhi, day_zhi),
    }

    # 命宫
    ming_gong = _calc_ming_gong(month_zhi, hour_zhi)

    return {
        "solar_date": f"{year}年{month}月{day}日",
        "lunar_date": f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
        "gender": gender,
        "eight_char": {
            "year": {"gan": year_gan, "zhi": year_zhi, "shishen": shishen_year,
                     "canggan": hg_year, "nayin": nayin_year, "chang_sheng": c_year},
            "month": {"gan": month_gan, "zhi": month_zhi, "shishen": shishen_month,
                      "canggan": hg_month, "nayin": nayin_month, "chang_sheng": c_month},
            "day": {"gan": day_gan, "zhi": day_zhi, "shishen": shishen_day,
                    "canggan": hg_day, "nayin": nayin_day, "chang_sheng": c_day},
            "hour": {"gan": hour_gan, "zhi": hour_zhi, "shishen": shishen_hour,
                     "canggan": hg_hour, "nayin": nayin_hour, "chang_sheng": c_hour},
        },
        "ri_gan": day_gan,
        "ri_zhi": day_zhi,
        "all_gan": all_gan,
        "all_zhi": all_zhi,
        "wuxing_count": wuxing_count,
        "relations": relations,
        "dayun": dayun,
        "wangshuai": wangshuai,
        "xiyong": xiyong,
        "shensha": shensha,
        "ming_gong": ming_gong,
        "lunar": lunar,
        "solar": solar,
        "bazi": bazi,
    }

def _get_hour_zhi(hour, minute=0):
    """根据时间返回时辰地支"""
    total = hour + minute / 60.0
    if 23 <= total or total < 1: return "子"
    if total < 3: return "丑"
    if total < 5: return "寅"
    if total < 7: return "卯"
    if total < 9: return "辰"
    if total < 11: return "巳"
    if total < 13: return "午"
    if total < 15: return "未"
    if total < 17: return "申"
    if total < 19: return "酉"
    if total < 21: return "戌"
    return "亥"

def _get_chang_sheng_state(ri_gan, zhi):
    """返回日干在某个地支的十二长生状态"""
    lst = CHANG_SHENG.get(ri_gan, [])
    if zhi in lst:
        return CHANG_SHENG_NAMES[lst.index(zhi)]
    return ""

def _find_relations(all_zhi):
    """找出地支间的冲合刑害关系"""
    rels = []
    names = ["年", "月", "日", "时"]
    for i in range(len(all_zhi)):
        for j in range(i+1, len(all_zhi)):
            key = (all_zhi[i], all_zhi[j])
            # 六合
            if key in DI_ZHI_HE:
                rels.append(f"{names[i]}{names[j]}六合({all_zhi[i]}{all_zhi[j]}合{DI_ZHI_HE[key]})")
            # 六冲
            if DI_ZHI_CHONG.get(all_zhi[i]) == all_zhi[j]:
                rels.append(f"{names[i]}{names[j]}相冲")
            # 相刑
            if key in DI_ZHI_XING:
                rels.append(f"{names[i]}{names[j]}{DI_ZHI_XING[key]}")
            # 相害
            if DI_ZHI_HAI.get(all_zhi[i]) == all_zhi[j]:
                rels.append(f"{names[i]}{names[j]}相害")
        # 自刑
        if all_zhi[i] in DI_ZHI_ZI_XING:
            cnt = all_zhi.count(all_zhi[i])
            if cnt >= 2 and all_zhi.index(all_zhi[i]) == i:
                rels.append(f"{names[i]}支{all_zhi[i]}自刑(共{cnt}个)")
    return rels

def _calc_dayun(solar, lunar, year_gan, month_gan, month_zhi, gender):
    """计算大运"""
    is_yang = TIAN_GAN_YINYANG[year_gan] == "阳"

    # 阳男阴女顺排，阴男阳女逆排
    shun_pai = (is_yang and gender == "男") or (not is_yang and gender == "女")

    # 计算起运年龄
    jie_dates = lunar.getJieQiTable()

    # 找到出生前后最近的"节"
    jie_list = []
    for name, solar_obj in jie_dates.items():
        if name in ["立春","惊蛰","清明","立夏","芒种","小暑","立秋","白露","寒露","立冬","大雪","小寒"]:
            jie_list.append((name, date(solar_obj.getYear(), solar_obj.getMonth(), solar_obj.getDay())))

    jie_list.sort(key=lambda x: x[1])
    birth_date = date(solar.getYear(), solar.getMonth(), solar.getDay())

    if shun_pai:
        # 顺排：到下一个节
        diff_days = 30  # 默认值
        for name, d in jie_list:
            if d >= birth_date:
                diff_days = (d - birth_date).days
                break
    else:
        # 逆排：到上一个节
        diff_days = 30  # 默认值
        for name, d in reversed(jie_list):
            if d <= birth_date:
                diff_days = (birth_date - d).days
                break

    qiyun_age = max(0, round(diff_days / 3)) if diff_days > 0 else 0

    # 排列大运
    month_gan_idx = TIAN_GAN.index(month_gan)
    month_zhi_idx = DI_ZHI.index(month_zhi)

    dayun_list = []
    for i in range(8):
        if shun_pai:
            g_idx = (month_gan_idx + i + 1) % 10
            z_idx = (month_zhi_idx + i + 1) % 12
        else:
            g_idx = (month_gan_idx - i - 1) % 10
            z_idx = (month_zhi_idx - i - 1) % 12

        gan = TIAN_GAN[g_idx]
        zhi = DI_ZHI[z_idx]
        age_start = qiyun_age + i * 10
        age_end = age_start + 9

        dayun_list.append({
            "index": i + 1,
            "gan_zhi": gan + zhi,
            "gan": gan,
            "zhi": zhi,
            "age_start": age_start,
            "age_end": age_end,
            "age_range": f"{age_start}-{age_end}岁",
            "current": False,  # 后续在 analyzer 中标记
        })

    return {
        "direction": "顺排" if shun_pai else "逆排",
        "qiyun_age": qiyun_age,
        "dayun_list": dayun_list,
    }

def _calc_wangshuai(ri_gan, month_zhi, all_gan, all_zhi, wuxing_count):
    """判断日主旺衰"""
    wx = TIAN_GAN_WUXING[ri_gan]
    season = get_season(month_zhi)

    # 得令：月支五行
    month_wx = DI_ZHI_WUXING[month_zhi]
    de_ling = month_wx == wx or (wx == "水" and month_wx == "金")

    # 得地：其他地支是否有根（同五行三合或藏干本气）
    de_di = 0
    for z in all_zhi:
        if DI_ZHI_WUXING[z] == wx: de_di += 1
        if CANG_GAN[z] and CANG_GAN[z][0][0]:  # 藏干本气
            if TIAN_GAN_WUXING[CANG_GAN[z][0][0]] == wx:
                de_di += 1

    # 得势：天干是否有比劫印
    de_shi = 0
    for g in all_gan:
        if g == ri_gan:
            continue
        ss = get_shi_shen(ri_gan, g)
        if ss in ["比肩", "劫财", "正印", "偏印"]:
            de_shi += 1

    # 综合判断
    total_score = (1 if de_ling else 0) + min(de_di, 3) * 0.5 + min(de_shi, 3) * 0.5

    if total_score >= 3:
        level = "身旺"
    elif total_score >= 1.5:
        level = "中和偏旺"
    elif total_score >= 0.8:
        level = "中和偏弱"
    else:
        level = "身弱"

    return {
        "level": level,
        "de_ling": de_ling,
        "de_di": de_di >= 1,
        "de_shi": de_shi >= 1,
        "score": round(total_score, 1),
        "detail": f"得令:{de_ling}, 得地:{de_di>=1}, 得势:{de_shi>=1}, 综合:{level}"
    }

def _calc_xiyong(ri_gan, month_zhi, wuxing_count, ws_level=""):
    """根据旺衰和五行分布判断喜用神和忌神"""
    wx = TIAN_GAN_WUXING[ri_gan]

    # 生我者为印，我生者为食伤，克我者为官杀，我克者为财，同我者为比劫
    sheng_me = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
    wo_sheng = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    ke_me = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}
    wo_ke = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

    wc = wuxing_count
    sorted_wx = sorted(wc.items(), key=lambda x: x[1], reverse=True)
    weakest = min(wc.items(), key=lambda x: x[1])

    xi_shen = []
    ji_shen = []

    # 核心逻辑：身弱则扶，身旺则抑
    is_weak = ws_level in ["身弱", "中和偏弱"]

    if is_weak:
        # 身弱 → 需要生扶
        # 喜：生我者（印）+ 同我者（比劫）
        xi_shen.append(sheng_me[wx])  # 印星（人生贵人、知识支撑）
        xi_shen.append(wx)            # 比劫（同伴助力）
        # 忌：克我者（官杀）+ 我生者（食伤泄气）+ 我克者（财耗气）
        ji_shen.append(ke_me[wx])     # 官杀（压力小人是非）
        ji_shen.append(wo_sheng[wx])   # 食伤（过度消耗精力）
        ji_shen.append(wo_ke[wx])     # 财星（身弱不胜财）
        # 去重
        ji_shen = [j for j in ji_shen if j not in xi_shen]
    else:
        # 身旺 → 需要克制或泄秀
        xi_shen.append(ke_me[wx])     # 官杀（用权力约束）
        xi_shen.append(wo_sheng[wx])  # 食伤（才华泄秀）
        xi_shen.append(wo_ke[wx])     # 财星（身强能任财）
        # 忌：生我者（印）+ 同我者（比劫）- 不可再帮扶
        ji_shen.append(sheng_me[wx])
        ji_shen.append(wx)
        ji_shen = [j for j in ji_shen if j not in xi_shen]

    return {
        "xi_shen": list(set(xi_shen)),
        "ji_shen": list(set(ji_shen)),
        "strongest": sorted_wx[0][0],
        "weakest": weakest[0],
    }

def _calc_ming_gong(month_zhi, hour_zhi):
    """推算命宫"""
    # 命宫推算法：以月支为基准，按生时顺数
    month_idx = DI_ZHI.index(month_zhi)
    hour_idx = DI_ZHI.index(hour_zhi)

    # 寅上起正月，顺数至生时
    ming_gong_idx = (month_idx - 2 + hour_idx) % 12
    return DI_ZHI[ming_gong_idx]

def get_current_dayun(dayun_data, current_age):
    """获取当前所处的大运"""
    for dy in dayun_data["dayun_list"]:
        if dy["age_start"] <= current_age <= dy["age_end"]:
            dy["current"] = True
            return dy
    return None

def get_liunian(solar_birth, current_year):
    """获取当前流年干支"""
    birth_year = solar_birth.getYear()
    age = current_year - birth_year

    # 流年干支：用六十甲子
    # 1984年是甲子年
    base_year = 1984
    base_index = 0  # 甲子=0
    offset = current_year - base_year
    gan_zhi = get_sexagenary((base_index + offset) % 60)

    return {
        "year": current_year,
        "age": age,
        "gan_zhi": gan_zhi,
        "gan": gan_zhi[0],
        "zhi": gan_zhi[1],
    }

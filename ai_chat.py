"""AI 对话模块 — 调用 DeepSeek/Anthropic 兼容 API"""

import requests
from data.wuxing import TIAN_GAN_WUXING, TIAN_GAN_YINYANG

# 最多保留多少条历史消息发给 API
MAX_HISTORY = 8


def build_system_prompt(chart, name):
    """构建紧凑的命盘 system prompt"""
    ec = chart["eight_char"]
    dy = chart["dayun"]
    xiyong = chart["xiyong"]

    # 四柱一行压缩
    pillars = f"{ec['year']['gan']}{ec['year']['zhi']} {ec['month']['gan']}{ec['month']['zhi']} {ec['day']['gan']}{ec['day']['zhi']} {ec['hour']['gan']}{ec['hour']['zhi']}"
    shishens = f"{ec['year']['shishen']}/{ec['month']['shishen']}/日主/{ec['hour']['shishen']}"
    canggan = f"年{ec['year']['zhi']}藏{'、'.join([g for g,_ in ec['year']['canggan']])} 月{ec['month']['zhi']}藏{'、'.join([g for g,_ in ec['month']['canggan']])} 日{ec['day']['zhi']}藏{'、'.join([g for g,_ in ec['day']['canggan']])} 时{ec['hour']['zhi']}藏{'、'.join([g for g,_ in ec['hour']['canggan']])}"

    # 大运压缩为一行
    dayun_str = " ".join([f"{d['age_range']}{d['gan_zhi']}" for d in dy["dayun_list"]])

    # 地支关系
    rels = '; '.join(chart['relations']) if chart['relations'] else '无'

    return f"""你是精通《穷通宝典》《三命通会》《滴天髓》《渊海子平》《子平真诠》《神峰通考》的八字命理师。结合命盘数据回答用户问题，引用典籍标注出处，语气中性建设性，结尾提醒「命理分析仅供参考，人生在于自身的努力和选择」，用中文。

【{name}】{chart['solar_date']}({chart['lunar_date']}) {chart['gender']} 四柱:{pillars} 十神:{shishens} 日主{chart['ri_gan']}{TIAN_GAN_WUXING[chart['ri_gan']]}{TIAN_GAN_YINYANG[chart['ri_gan']]}性 旺衰:{chart['wangshuai']['level']} 喜用:{'、'.join(xiyong['xi_shen'])} 忌:{'、'.join(xiyong.get('ji_shen',[]))} 五行:金{chart['wuxing_count']['金']:.0f}木{chart['wuxing_count']['木']:.0f}水{chart['wuxing_count']['水']:.0f}火{chart['wuxing_count']['火']:.0f}土{chart['wuxing_count']['土']:.0f} 藏干:{canggan} 纳音:年{ec['year']['nayin']}月{ec['month']['nayin']}日{ec['day']['nayin']}时{ec['hour']['nayin']} 关系:{rels} 大运({dy['direction']}{dy['qiyun_age']}岁起):{dayun_str} 命宫:{chart['ming_gong']}"""


def chat_with_ai(messages, chart, name, api_key, base_url, model="deepseek-v4-pro"):
    """调用 AI API 对话，只发最近 MAX_HISTORY 条消息"""
    system_prompt = build_system_prompt(chart, name)

    # 只保留最近的对话历史
    recent = [m for m in messages if m["role"] in ("user", "assistant")][-MAX_HISTORY:]

    payload = {
        "model": model,
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [{"role": m["role"], "content": m["content"]} for m in recent],
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    url = base_url.rstrip("/") + "/v1/messages"

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        return text or "AI 未返回有效回复。"
    except requests.exceptions.Timeout:
        return "请求超时，请稍后重试。"
    except requests.exceptions.HTTPError as e:
        return f"API 错误({e.response.status_code})：{e.response.text[:200]}"
    except Exception as e:
        return f"请求出错：{str(e)}"

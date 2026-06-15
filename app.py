"""八字命理分析应用 — 基于 Streamlit 的交互式算命 App"""

import streamlit as st
from datetime import date, datetime
from calculator import calc_from_solar
from analyzer import analyze_full, analyze_topic
from ai_chat import chat_with_ai

# ===== 页面配置 =====
st.set_page_config(
    page_title="八字命理分析",
    page_icon="☯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("☯️ 八字命理分析系统")
st.caption("四柱八字排盘 · 专业命理分析 · 经典典籍参考")

# ===== 初始化 Session State =====
if "chart" not in st.session_state:
    st.session_state.chart = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_analysis" not in st.session_state:
    st.session_state.full_analysis = None
if "history_verified" not in st.session_state:
    st.session_state.history_verified = []
if "name" not in st.session_state:
    st.session_state.name = ""
if "ai_enabled" not in st.session_state:
    st.session_state.ai_enabled = False
if "ai_api_key" not in st.session_state:
    st.session_state.ai_api_key = ""
if "ai_base_url" not in st.session_state:
    st.session_state.ai_base_url = "https://api.deepseek.com/anthropic"
if "ai_model" not in st.session_state:
    st.session_state.ai_model = "deepseek-v4-pro"

# ===== 侧边栏：输入区 =====
with st.sidebar:
    st.header("📋 输入信息")

    name = st.text_input("姓名", value=st.session_state.name)
    st.session_state.name = name

    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input("出生日期（阳历）", value=date(2000, 1, 1),
                                   min_value=date(1900, 1, 1), max_value=date.today())
    with col2:
        gender = st.selectbox("性别", ["男", "女"])

    col3, col4 = st.columns(2)
    with col3:
        birth_hour = st.number_input("出生时辰（时）", 0, 23, 12)
    with col4:
        birth_minute = st.number_input("出生分钟", 0, 59, 0)

    birth_place = st.text_input("出生地", "请输入省市")

    # 时辰显示
    hour_names = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    h_idx = (birth_hour + 1) % 24 // 2
    if birth_hour == 23:
        h_idx = 0
    st.caption(f"👉 对应时辰：**{hour_names[h_idx]}时**（{hour_names[h_idx]}时：{'23' if h_idx==0 else f'{h_idx*2-1 if h_idx>0 else 23}'}:00-{'1' if h_idx==0 else f'{(h_idx+1)*2-1}'}:00）")

    st.divider()

    if st.button("🔮 开始排盘", type="primary", use_container_width=True):
        with st.spinner("正在排盘计算中..."):
            chart = calc_from_solar(
                birth_date.year, birth_date.month, birth_date.day,
                birth_hour, birth_minute, gender
            )
            st.session_state.chart = chart
            st.session_state.full_analysis = analyze_full(chart)
            st.session_state.messages = []
            st.session_state.history_verified = []

            # 第一条系统消息
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"## ☯️ {name}的四柱八字命盘已排出\n\n"
                          f"**基本信息**：{chart['solar_date']}（{chart['lunar_date']}）{chart['eight_char']['hour']['zhi']}时 · {gender}\n\n"
                          f"请点击下方的分析话题查看详细命理分析，也可以在底部聊天框提问任何问题。"
            })

        st.rerun()

    # 显示已有命盘信息
    if st.session_state.chart:
        st.divider()
        st.success(f"✅ **{st.session_state.name}** 的命盘已就绪")
        ec = st.session_state.chart["eight_char"]
        st.markdown(f"""
        | | 年柱 | 月柱 | 日柱 | 时柱 |
        |---|------|------|------|------|
        | 天干 | {ec['year']['gan']} | {ec['month']['gan']} | {ec['day']['gan']} | {ec['hour']['gan']} |
        | 地支 | {ec['year']['zhi']} | {ec['month']['zhi']} | {ec['day']['zhi']} | {ec['hour']['zhi']} |
        """)

        if st.button("🔄 重新排盘", use_container_width=True):
            for key in ["chart", "full_analysis", "messages", "history_verified", "name",
                       "ai_enabled", "ai_api_key", "ai_base_url", "ai_model"]:
                if key in st.session_state:
                    st.session_state[key] = None if key in ["chart", "full_analysis"] else (
                        [] if key in ["messages", "history_verified"] else (
                            "" if key in ["name", "ai_api_key", "ai_base_url", "ai_model"] else False))
            st.rerun()

    # AI 设置区
    st.divider()
    st.subheader("🤖 AI 对话设置")

    ai_on = st.toggle("启用 AI 对话", value=st.session_state.ai_enabled,
                      help="开启后使用 AI API 进行对话，回答更智能、更个性化")
    st.session_state.ai_enabled = ai_on

    if ai_on:
        api_key = st.text_input("API Key", type="password",
                                value=st.session_state.ai_api_key,
                                placeholder="输入 DeepSeek 或其他兼容 API Key")
        st.session_state.ai_api_key = api_key

        base_url = st.text_input("API 地址", value=st.session_state.ai_base_url,
                                 placeholder="https://api.deepseek.com/anthropic")
        st.session_state.ai_base_url = base_url

        model = st.selectbox("模型", ["deepseek-v4-pro", "deepseek-v4-flash", "claude-sonnet-4-6", "claude-opus-4-8"],
                             index=0 if st.session_state.ai_model in ["deepseek-v4-pro", ""] else 0)
        st.session_state.ai_model = model

        if not api_key:
            st.warning("请输入 API Key 才能使用 AI 对话")
    else:
        st.caption("开启后可使用 AI 进行更智能的命理对话")

# ===== 主区域 =====
if st.session_state.chart is None:
    # 未排盘时的引导页
    st.info("👈 请在左侧输入出生信息，然后点击「开始排盘」按钮")
    st.markdown("""
    ### 使用说明
    1. 在左侧输入姓名、出生日期、时辰、性别和出生地
    2. 点击「开始排盘」自动计算四柱八字
    3. 点击下方分析话题查看详细报告
    4. 在聊天框中追问更多细节（如「我的婚姻怎么样」「适合什么行业」）
    5. 通过反复提问，分析会越来越精准
    """)
else:
    chart = st.session_state.chart
    ec = chart["eight_char"]

    # 命盘概览区
    with st.expander("📊 完整命盘", expanded=False):
        col_y, col_m, col_d, col_h = st.columns(4)
        for col, pillar, name in [
            (col_y, ec["year"], "年柱"), (col_m, ec["month"], "月柱"),
            (col_d, ec["day"], "日柱"), (col_h, ec["hour"], "时柱")
        ]:
            with col:
                st.markdown(f"**{name}**")
                st.markdown(f"天干：{pillar['gan']}（{pillar['shishen']}）")
                st.markdown(f"地支：{pillar['zhi']}（{pillar['nayin']}）")
                st.markdown(f"藏干：{' '.join([g for g,_ in pillar['canggan']])}")
                st.markdown(f"十二长生：{pillar['chang_sheng']}")

        # 五行统计
        wc = chart["wuxing_count"]
        st.markdown("**五行力量**")
        import pandas as pd
        df = pd.DataFrame({
            "五行": ["金","木","水","火","土"],
            "力量": [wc["金"], wc["木"], wc["水"], wc["火"], wc["土"]]
        })
        st.bar_chart(df.set_index("五行"))

        # 地支关系
        if chart["relations"]:
            st.markdown("**地支关系**：" + "；".join(chart["relations"]))

        # 大运表
        st.markdown("**大运排列**")
        dy_data = []
        for dy in chart["dayun"]["dayun_list"]:
            dy_data.append({
                "大运": f"第{dy['index']}步",
                "年龄": dy["age_range"],
                "干支": dy["gan_zhi"],
            })
        st.dataframe(dy_data, use_container_width=True, hide_index=True)

    # 分析报告区
    st.subheader("📖 命理分析报告")

    # 话题按钮行
    topics = ["性格", "事业", "财运", "婚姻", "健康", "大运", "流年", "用神", "学业", "出国", "方位", "子女"]
    cols = st.columns(len(topics))
    for i, topic in enumerate(topics):
        with cols[i]:
            if st.button(topic, key=f"btn_{topic}", use_container_width=True):
                result = analyze_topic(chart, topic)
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"分析：{topic}"
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"### {result['title']}\n\n{result['content']}"
                })
                st.rerun()

    st.divider()

    # 历史验证区
    with st.expander("📝 历史事件校准（帮助提高分析准确度）", expanded=False):
        st.caption("在此记录已确认的人生大事，系统会据此调整分析")
        event_year = st.number_input("年份", 1900, 2100, 2000, key="event_year")
        event_desc = st.text_input("事件描述", key="event_desc", placeholder="例如：考上大学、结婚、换工作、搬家...")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 确认此事件", use_container_width=True):
                st.session_state.history_verified.append({
                    "year": event_year,
                    "desc": event_desc,
                })
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"历史事件确认：{event_year}年 - {event_desc}"
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"已记录 ✅ **{event_year}年 - {event_desc}**。我会在后续分析中参考这个信息，校准对命盘的理解。"
                })
                st.rerun()
        with col2:
            if st.button("🗑️ 清空记录", use_container_width=True):
                st.session_state.history_verified = []
                st.rerun()

        if st.session_state.history_verified:
            st.markdown("**已记录的事件：**")
            for evt in st.session_state.history_verified:
                st.markdown(f"- {evt['year']}年：{evt['desc']}")

    st.divider()

    # 聊天区
    if st.session_state.ai_enabled:
        st.subheader("💬 AI 命理对话")
        mode_text = f"**AI 模式**：{st.session_state.ai_model} | 可自由提问，AI 会根据命盘和经典典籍回答"
    else:
        st.subheader("💬 深入探讨")
        mode_text = "**离线模式**：在下方输入你的问题，系统根据规则进行分析"
    st.caption(mode_text)

    # 显示聊天历史
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 输入框
    if prompt := st.chat_input("输入你的问题..." if st.session_state.ai_enabled else "输入你的问题，如「分析我的婚姻」「我什么时候能发财」「适合什么行业」"):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})

        if st.session_state.ai_enabled and st.session_state.ai_api_key:
            # AI 模式
            with st.spinner("AI 正在分析..."):
                ai_reply = chat_with_ai(
                    messages=st.session_state.messages,
                    chart=chart,
                    name=st.session_state.name,
                    api_key=st.session_state.ai_api_key,
                    base_url=st.session_state.ai_base_url,
                    model=st.session_state.ai_model,
                )
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        elif st.session_state.ai_enabled and not st.session_state.ai_api_key:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "⚠️ 请先在侧边栏输入 API Key 才能使用 AI 对话。"
            })
        else:
            # 离线规则模式（原有逻辑）
            matched_topic = None
            topic_keywords = {
                "事业": ["工作", "行业", "职业", "跳槽", "升职", "老板", "同事", "创业", "就业", "做什么"],
                "财运": ["钱", "财", "发财", "赚钱", "收入", "工资", "投资", "理财", "股票", "基金", "富"],
                "婚姻": ["婚姻", "结婚", "老公", "老婆", "老公", "妻子", "丈夫", "配偶", "感情", "恋爱", "离婚", "分手", "网恋", "对象"],
                "健康": ["病", "健康", "身体", "疼", "痛", "医院", "手术", "锻炼", "保健", "养生"],
                "性格": ["性格", "个性", "脾气", "特点", "优点", "缺点"],
                "学业": ["学习", "考试", "学校", "毕业", "学位", "论文", "考研", "留学", "读书"],
                "出国": ["出国", "海外", "国外", "移民", "签证", "留学"],
                "方位": ["方位", "方向", "搬家", "去哪个城市", "去哪", "西北", "东南"],
                "子女": ["孩子", "小孩", "子女", "生育", "儿子", "女儿"],
                "用神": ["用神", "喜用", "喜神", "忌神", "五行缺", "五行"],
            }

            prompt_lower = prompt.lower()
            for topic, keywords in topic_keywords.items():
                for kw in keywords:
                    if kw in prompt_lower:
                        matched_topic = topic
                        break
                if matched_topic:
                    break

            if matched_topic:
                result = analyze_topic(chart, matched_topic)
            else:
                result = analyze_topic(chart, prompt_lower)

            history_note = ""
            if st.session_state.history_verified:
                history_note = "\n\n**📝 历史校准参考**：\n"
                for evt in st.session_state.history_verified:
                    history_note += f"- {evt['year']}年：{evt['desc']}\n"

            full_content = f"### {result['title']}\n\n{result['content']}{history_note}"
            st.session_state.messages.append({"role": "assistant", "content": full_content})
        st.rerun()

    # 提示词
    if not st.session_state.messages:
        if st.session_state.ai_enabled:
            st.info("🤖 AI 对话模式已开启！直接输入任何问题，AI 会根据你的命盘和经典典籍回答。")
        else:
            st.info("👆 点击上面的话题按钮开始分析，或在底部输入框提问。推荐先看看「性格」和「事业」！")

# 页脚
st.divider()
st.caption("""
⚠️ **免责声明**：命理分析仅供文化研究和参考，不应被视为科学预测。人生在于自身的努力和选择。
分析参考典籍：《穷通宝典》《三命通会》《滴天髓》《渊海子平》《子平真诠》《神峰通考》
""")

import streamlit as st

# 初期化
if "running" not in st.session_state:
    st.session_state.running = False

if "results" not in st.session_state:
    st.session_state.results = []

# -----------------------------
# CSS
# -----------------------------

st.markdown("""
<style>

.gpt-box {
    background-color: #e8f5e9;
    padding: 15px;
    border-radius: 10px;
}

.gemini-box {
    background-color: #e3f2fd;
    padding: 15px;
    border-radius: 10px;
}

.phase-title {
    font-size: 24px;
    margin-top: 25px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

import os
# OpenAI
from openai import OpenAI
# Gemini
from google import genai
from google.genai import types

# OpenAI クライアント生成
openai_client = OpenAI()
# Gemini クライアント生成
gemini_client = genai.Client()

# タイトル文字
st.title("GPTとGeminiでの対話")

# 説明
st.write("""
ChatGPT が地方イベント案を提案し、
Gemini が批判・改善提案を行います。

フェーズを重ねながら、
企画を磨き上げていく実験ページです。
(フェーズは 1 から 5 まで選択できます。)
""")

phase_count = st.slider(
    "フェーズ数",
    min_value=1,
    max_value=5,
    value=2
)

# インプットテキスト
theme = st.text_input("初めの提案テーマを入力してください。（例：地元でとれる甘いにんじんを題材にした、企画を提案）")

# ボタン制御用
button_clicked = st.button(
    "開始",
    disabled=st.session_state.running
)

if button_clicked:
    st.session_state.running = True
    st.rerun()

if st.session_state.running:

    with st.spinner("AIたちが議論中..."):

        # 対話履歴
        phase_results = []

        current_input = theme

        for phase in range(1, phase_count + 1):

            # GPT
            gpt_res = openai_client.responses.create(
                model="gpt-5.4",
                instructions="地方のイベント企画を考案する役割です。",
                input=current_input
            )

            gpt_text = gpt_res.output_text

            # DEBUG
            # with st.expander("GPT Raw Response"):
            #     st.code(repr(gpt_text))

            # Gemini
            gemini_res = gemini_client.models.generate_content(
                model="gemini-3-flash-preview",
                config=types.GenerateContentConfig(
                    system_instruction="あなたは厳格なイベントレビュー担当です。企画の弱点を指摘する。集客性を評価する。"),
                contents=gpt_text
            )

            gemini_text = gemini_res.text

            # DEBUG
            # with st.expander("Gemini Raw Response"):
            #     st.code(repr(gemini_text))

            phase_results.append({
                "phase": phase,
                "gpt": gpt_text,
                "gemini": gemini_text
            })

            # 次フェーズ入力
            current_input = gemini_text


    st.session_state.results = phase_results
    st.session_state.running = False
    st.rerun()


conversation_text = ""
if st.session_state.results:
    # -----------------------------
    # 表示
    # -----------------------------

    for item in st.session_state.results:

        st.markdown(
            f"<div class='phase-title'>Phase {item['phase']}</div>",
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:

            # gpt_html = item["gpt"].replace("\n", "<br>")
            gpt_html = item["gpt"]

            st.markdown(f"""
            <div class="gpt-box">
            <h3>💡 ChatGPT</h3>
            {gpt_html}
            """, unsafe_allow_html=True)


        with col2:

            # gemini_html = item["gemini"].replace("\n", "<br>")
            gemini_html = item["gemini"]

            st.markdown(f"""
            <div class="gemini-box">
            <h3>👀 Gemini</h3>
            {gemini_html}
            """, unsafe_allow_html=True)

    for item in st.session_state.results:

        conversation_text += (
            f"Phase {item['phase']}\n"
        )

        conversation_text += (
            f"[ChatGPT]\n"
            f"{item['gpt']}\n\n"
        )

        conversation_text += (
            f"[Gemini]\n"
            f"{item['gemini']}\n\n"
        )

        conversation_text += (
            "-------------------\n\n"
        )


st.download_button(
    label="対話ログをダウンロード",

    data=conversation_text,

    file_name="ai_discussion.txt",

    mime="text/plain"
)
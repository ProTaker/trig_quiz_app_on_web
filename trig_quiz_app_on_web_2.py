import random
import streamlit as st
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
import time

st.title("三角比クイズ (θの簡単化)")

# --- 簡単化ルール ---
def simplify(func, base_angle):
    rules = {
        "sin": {0: "sinθ", 90: "cosθ", 180: "-sinθ", 270: "-cosθ", 360: "sinθ",
                -90: "-cosθ", -180: "-sinθ", -270: "cosθ"},
        "cos": {0: "cosθ", 90: "-sinθ", 180: "-cosθ", 270: "sinθ", 360: "cosθ",
                -90: "sinθ", -180: "-cosθ", -270: "-sinθ"},
        "tan": {0: "tanθ", 90: "1/tanθ", 180: "tanθ", 270: "-1/tanθ", 360: "tanθ",
                -90: "-1/tanθ", -180: "tanθ", -270: "1/tanθ"}
    }
    return rules[func][base_angle]

# --- 選択肢固定 ---
OPTIONS = ["sinθ", "-sinθ", "cosθ", "-cosθ", "tanθ", "-tanθ", "1/tanθ", "-1/tanθ"]

# --- セッションステート初期化 ---
if "question_number" not in st.session_state:
    st.session_state.question_number = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "feedback" not in st.session_state:
    st.session_state.feedback = []
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "results" not in st.session_state:
    st.session_state.results = []

# --- 問題生成関数 ---
def generate_question():
    funcs = ["sin", "cos", "tan"]
    base_angles = [0, 90, 180, 270, 360, -90, -180, -270]
    func = random.choice(funcs)
    angle = random.choice(base_angles)
    if angle == 0:
        problem = f"{func}θ"
    else:
        sign = "+" if angle > 0 else ""
        problem = f"{func}({angle}°{sign}θ)"
    correct = simplify(func, angle)
    return problem, correct

# --- メインロジック ---
if st.session_state.question_number < 10:
    problem, correct = generate_question()
    st.subheader(f"問題 {st.session_state.question_number+1}")
    st.markdown(f"### {problem} を簡単にせよ")

    cols = st.columns(4)
    for idx, option in enumerate(OPTIONS):
        if cols[idx % 4].button(option):
            if option == correct:
                st.success("正解！")
                st.session_state.score += 1
                st.session_state.feedback.append(f"問題{st.session_state.question_number+1}: 正解")
            else:
                st.error(f"不正解。正解は {correct}")
                st.session_state.feedback.append(f"問題{st.session_state.question_number+1}: × 正解は {correct}")
            st.session_state.question_number += 1
            st.experimental_rerun()
else:
    # --- 結果表示 ---
    end_time = time.time()
    elapsed = Decimal(str(end_time - st.session_state.start_time)).quantize(Decimal('0.01'), ROUND_HALF_UP)
    total = st.session_state.score * 10
    st.subheader("結果発表")
    st.write(f"得点: {total}/100 点")
    st.write(f"経過時間: {elapsed} 秒")

    st.write("### 各問題の結果")
    for f in st.session_state.feedback:
        st.write(f)

    # --- 履歴テーブル ---
    st.session_state.results.append((total, elapsed))
    df = pd.DataFrame(st.session_state.results, columns=["得点", "時間"])
    st.write("### 試験結果の履歴")
    st.dataframe(df)

    if st.button("もう一度やる"):
        st.session_state.question_number = 0
        st.session_state.score = 0
        st.session_state.feedback = []
        st.session_state.start_time = time.time()
        st.experimental_rerun()

# --- スコア表示 ---
st.write(f"現在のスコア: {st.session_state.score * 10}/100 点")
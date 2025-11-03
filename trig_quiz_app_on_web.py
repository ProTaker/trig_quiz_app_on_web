# trig_transform_quiz_app_dynamic_4_options.py
import streamlit as st
import random
import time
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

st.set_page_config(page_title="三角比クイズ（変換公式編）", layout="centered")
st.title("三角比クイズ（変換公式編）")

# -----------------------------
# CSS（ボタンサイズ調整と列幅固定、中央揃え）
# -----------------------------
st.markdown("""
<style>
/* 選択肢ボタンのサイズとフォントを統一 */
div.stButton > button {
    width: 200px !important; /* ボタン幅を少し広げた */
    height: 70px !important;
    font-size: 20px;
}
/* st.table/st.dataframe のセル内の数式表示を調整 */
.stTable, .stDataFrame {
    font-size: 18px; /* 全体フォントサイズ調整 */
}

/* テーブル全体の配置を中央に */
.stTable {
    width: fit-content; 
    margin-left: auto;  
    margin-right: auto; 
}

/* すべてのセルを中央揃えにする */
.stTable table th, .stTable table td {
    white-space: nowrap; 
    text-align: center !important; 
    vertical-align: middle !important;
}

/* 列幅固定 */
.stTable table th:nth-child(1), .stTable table td:nth-child(1) {
    width: 60px; 
}
.stTable table th:nth-child(2), .stTable table td:nth-child(2) {
    min-width: 250px; /* 問題文用に幅を調整 */
}
.stTable table th:nth-child(3), .stTable table td:nth-child(3) {
    min-width: 200px; 
}
.stTable table th:nth-child(4), .stTable table td:nth-child(4) {
    min-width: 200px; 
}
.stTable table th:nth-child(5), .stTable table td:nth-child(5) {
    width: 60px; 
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 変換公式の定義 (選択肢グループを定義)
# -----------------------------

# 問題として使用する関数
functions = ["sin", "cos", "tan"]

# 変換のオフセット
OFFSETS = {
    "neg_t": r"(-\theta)",
    "p90_t": r"(90^\circ+\theta)",
    "m90_t": r"(90^\circ-\theta)",
    "p180_t": r"(180^\circ+\theta)",
    "m180_t": r"(180^\circ-\theta)",
    "p270_t": r"(270^\circ+\theta)",
    "m270_t": r"(270^\circ-\theta)",
    "p360_t": r"(360^\circ+\theta)",
    "m360_t": r"(360^\circ-\theta)",
}

# 全ての変換後の結果（内部キーとLaTeX表示）
RESULT_OPTIONS = {
    "sin_t": r"\sin\theta",
    "-sin_t": r"-\sin\theta",
    "cos_t": r"\cos\theta",
    "-cos_t": r"-\cos\theta",
    "tan_t": r"\tan\theta",
    "-tan_t": r"-\tan\theta",
    "cot_t": r"\frac{1}{\tan\theta}",
    "-cot_t": r"-\frac{1}{\tan\theta}",
}

# 関数ごとの選択肢グループの定義 (キーのリスト)
SIN_COS_OPTIONS_KEYS = ["sin_t", "-sin_t", "cos_t", "-cos_t"]
TAN_OPTIONS_KEYS = ["tan_t", "-tan_t", "cot_t", "-cot_t"]


# 問題と正解の対応表 (前回のものと同じ)
TRANSFORM_ANSWERS = {
    "sin": {
        "neg_t": "-sin_t", "p90_t": "cos_t", "m90_t": "cos_t",
        "p180_t": "-sin_t", "m180_t": "sin_t", "p270_t": "-cos_t",
        "m270_t": "-cos_t", "p360_t": "sin_t", "m360_t": "-sin_t",
    },
    "cos": {
        "neg_t": "cos_t", "p90_t": "-sin_t", "m90_t": "sin_t",
        "p180_t": "-cos_t", "m180_t": "-cos_t", "p270_t": "sin_t",
        "m270_t": "-sin_t", "p360_t": "cos_t", "m360_t": "cos_t",
    },
    "tan": {
        "neg_t": "-tan_t", "p90_t": "-cot_t", "m90_t": "cot_t", 
        "p180_t": "tan_t", "m180_t": "-tan_t", "p270_t": "-cot_t",
        "m270_t": "cot_t", "p360_t": "tan_t", "m360_t": "-tan_t",
    },
}

MAX_QUESTIONS = 10

# -----------------------------
# セッション操作関数
# -----------------------------
def new_question():
    """新しい問題を生成し、セッション状態を更新する"""
    st.session_state.func = random.choice(functions)
    st.session_state.offset_key = random.choice(list(OFFSETS.keys()))
    
    # 関数に応じて選択肢のキーリストを選択
    if st.session_state.func in ["sin", "cos"]:
        options_base = SIN_COS_OPTIONS_KEYS
    else: # tan
        options_base = TAN_OPTIONS_KEYS
        
    # 選択肢はベースのリストをシャッフルして使用
    shuffled_options = options_base.copy()
    random.shuffle(shuffled_options)
    st.session_state.display_options = shuffled_options
    
    st.session_state.selected = None
    st.session_state.show_result = False

def initialize_session_state():
    """セッション状態を初期化する"""
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    
    if not st.session_state.quiz_started:
        st.session_state.score = 0
        st.session_state.question_count = 0
        st.session_state.history = []
        st.session_state.show_result = False
        st.session_state.start_time = time.time()
        # 最初の問題の準備
        new_question()

def start_quiz():
    """クイズ開始ボタンが押された時の処理"""
    st.session_state.quiz_started = True
    initialize_session_state()
    st.rerun()

def check_answer_and_advance(selected_key):
    """回答をチェックし、次の問題または結果画面へ進む"""
    st.session_state.selected = selected_key # クリックされた選択肢のキーを保存

    current_func = st.session_state.func
    current_offset_key = st.session_state.offset_key
    correct_key = TRANSFORM_ANSWERS[current_func][current_offset_key]

    is_correct = (st.session_state.selected == correct_key)

    # 問題文の表示形式を決定
    question_latex = rf"\text{{{current_func}}} {OFFSETS[current_offset_key]}"
    
    st.session_state.history.append({
        "question_disp": question_latex, # 問題のLaTeX表示文字列を保存
        "
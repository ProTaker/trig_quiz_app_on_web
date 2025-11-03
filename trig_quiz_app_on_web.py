# trig_transform_quiz_app_range_selected_v2.py
import streamlit as st
import random
import time
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

# ページ設定
st.set_page_config(page_title="三角比クイズ（補角・余角編）", layout="centered")

# タイトル
st.title("三角比クイズ（補角・余角編）")

# -----------------------------
# CSS（変更なし）
# -----------------------------
st.markdown("""
<style>
/* 選択肢ボタンのサイズとフォントを統一 */
div.stButton > button {
    width: 160px !important; 
    height: 70px !important;
    font-size: 18px; 
}

/* st.table/st.dataframe のセル内の数式表示を調整 */
.stTable, .stDataFrame {
    font-size: 20px; 
}

/* テーブル全体の配置を中央に */
.stTable {
    width: fit-content; 
    margin-left: auto;  
    margin-right: auto; 
}

/* テーブルの行の高さを調整 (分数の見やすさ向上) */
.stTable table th, .stTable table td {
    white-space: nowrap; 
    text-align: center !important; 
    vertical-align: middle !important;
    padding-top: 15px !important;    
    padding-bottom: 15px !important; 
    line-height: 1.5;                
}

/* 列幅固定 (変更なし) */
.stTable table th:nth-child(1), .stTable table td:nth-child(1) {
    width: 60px; 
}
.stTable table th:nth-child(2), .stTable table td:nth-child(2) {
    min-width: 250px; 
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
# 変換公式の定義（問題形式と解答）
# -----------------------------

functions = ["sin", "cos", "tan"]

# 変換公式のオフセット (問題形式)
OFFSETS = {
    "neg_t": r"(-\theta)", "p90_t": r"(90^\circ+\theta)", "m90_t": r"(90^\circ-\theta)",
    "p180_t": r"(180^\circ+\theta)", "m180_t": r"(180^\circ-\theta)", "p270_t": r"(270^\circ+\theta)",
    "m270_t": r"(270^\circ-\theta)", "p360_t": r"(360^\circ+\theta)", "m360_t": r"(360^\circ-\theta)",
    "mneg90_t": r"(-90^\circ+\theta)", "mneg90m_t": r"(-90^\circ-\theta)", 
    "mneg180_t": r"(-180^\circ+\theta)", "mneg180m_t": r"(-180^\circ-\theta)", 
    "mneg270_t": r"(-270^\circ+\theta)", "mneg270m_t": r"(-270^\circ-\theta)",
}

# ★★★ ユーザー要望に基づきキーリストを修正 ★★★
OFFSET_RANGES = {
    "0~180": {
        "label": r"$0^\circ \sim 180^\circ$",
        # 90-θ, 90+θ, 180-θ のみ
        "keys": ["m90_t", "p90_t", "m180_t"] 
    },
    "0~360": {
        "label": r"$0^\circ \sim 360^\circ$",
        # 360+θ (p360_t) を除外
        "keys": ["m90_t", "p90_t", "m180_t", "p180_t", "m270_t", "p270_t", "m360_t"]
    },
    "-180~180": {
        "label": r"$-180^\circ \sim 180^\circ$",
        # 180+θ (p180_t) と -180-θ (mneg180m_t) を除外
        "keys": ["neg_t", "m90_t", "p90_t", "m180_t", "mneg90_t", "mneg90m_t", "mneg180_t"]
    },
    "ALL": {
        "label": "全範囲",
        "keys": list(OFFSETS.keys())
    }
}
# ★★★ 修正箇所はここまで ★★★

# 変換結果の選択肢 (LaTeX 表示用)（変更なし）
RESULT_OPTIONS = {
    "sin_t": r"\sin\theta", "-sin_t": r"-\sin\theta",
    "cos_t": r"\cos\theta", "-cos_t": r"-\cos\theta",
    "tan_t": r"\tan\theta", "-tan_t": r"-\tan\theta",
    "cot_t": r"\dfrac{1}{\tan\theta}", 
    "-cot_t": r"-\dfrac{1}{\tan\theta}",
}

SIN_COS_OPTIONS_KEYS = ["sin_t", "-sin_t", "cos_t", "-cos_t"] 
TAN_OPTIONS_KEYS = ["tan_t", "-tan_t", "cot_t", "-cot_t"] 

# 変換公式の正解データ（変更なし）
TRANSFORM_ANSWERS = {
    "sin": {
        "neg_t": "-sin_t", "p90_t": "cos_t", "m90_t": "cos_t",
        "p180_t": "-sin_t", "m180_t": "sin_t", "p270_t": "-cos_t",
        "m270_t": "-cos_t", "p360_t": "sin_t", "m360_t": "-sin_t",
        "mneg90_t": "-cos_t", "mneg90m_t": "-cos_t", 
        "mneg180_t": "-sin_t", "mneg180m_t": "sin_t", 
        "mneg270_t": "cos_t", 
        "mneg270m_t": "cos_t", 
    },
    "cos": {
        "neg_t": "cos_t", "p90_t": "-sin_t", "m90_t": "sin_t",
        "p180_t": "-cos_t", "m180_t": "-cos_t", "p270_t": "sin_t",
        "m270_t": "-sin_t", "p360_t": "cos_t", "m360_t": "cos_t",
        "mneg90_t": "sin_t", "mneg90m_t": "-sin_t", 
        "mneg180_t": "-cos_t", "mneg180m_t": "-cos_t", 
        "mneg270_t": "-sin_t", "mneg270m_t": "sin_t",
    },
    "tan": {
        "neg_t": "-tan_t", "p90_t": "-cot_t", "m90_t": "cot_t", 
        "p180_t": "tan_t", "m180_t": "-tan_t", "p270_t": "-cot_t",
        "m270_t": "cot_t", "p360_t": "tan_t", "m360_t": "-tan_t",
        "mneg90_t": "-cot_t", "mneg90m_t": "cot_t", 
        "mneg180_t": "tan_t", "mneg180m_t": "-tan_t", 
        "mneg270_t": "-cot_t", 
        "mneg270m_t": "cot_t",  
    },
}

MAX_QUESTIONS = 10

# -----------------------------
# セッション操作関数（変更なし）
# -----------------------------
def new_question():
    st.session_state.func = random.choice(functions)
    
    # 選択された範囲からランダムに問題形式を選択
    possible_offsets = OFFSET_RANGES[st.session_state.offset_range]["keys"]
    st.session_state.offset_key = random.choice(possible_offsets)
    
    if st.session_state.func in ["sin", "cos"]:
        options_base = SIN_COS_OPTIONS_KEYS
    else: # tan
        options_base = TAN_OPTIONS_KEYS
        
    st.session_state.display_options = options_base
    st.session_state.selected = None
    st.session_state.show_result = False

def initialize_session_state():
    # 範囲選択の状態を管理するためのフラグを追加
    if 'range_selected' not in st.session_state:
        st.session_state.range_selected = False
        st.session_state.offset_range = "ALL" # デフォルト値
    
    # range_selected が True の場合のみクイズの状態を初期化して最初の出題を作る
    if 'score' not in st.session_state and st.session_state.range_selected:
        st.session_state.score = 0
        st.session_state.question_count = 0
        st.session_state.history = []
        st.session_state.show_result = False
        st.session_state.start_time = time.time()
        new_question()

def check_answer_and_advance(selected_key):
    st.session_state.selected = selected_key 

    current_func = st.session_state.func
    current_offset_key = st.session_state.offset_key
    correct_key = TRANSFORM_ANSWERS.get(current_func, {}).get(current_offset_key)
    
    if correct_key is None:
        st.error("問題データにエラーがあります。")
        return

    is_correct = (st.session_state.selected == correct_key)

    question_latex = rf"$$ \text{{{current_func}}} {OFFSETS[current_offset_key]} $$"
    
    st.session_state.history.append({
        "question_disp": question_latex, 
        "user_answer_key": st.session_state.selected,
        "correct_answer_key": correct_key,
        "is_correct": is_correct
    })

    if is_correct:
        st.session_state.score += 1

    st.session_state.question_count += 1

    if st.session_state.question_count >= MAX_QUESTIONS:
        st.session_state.show_result = True
    else:
        new_question()

    st.rerun()

# 初期化呼び出し
initialize_session_state()

# -----------------------------------------------
# アプリの描画（変更なし）
# -----------------------------------------------

if not st.session_state.range_selected:
    # 範囲選択画面
    st.header("出題範囲を選択してください")
    st.markdown("---")
    #st.write("どの変換公式のグループを中心に解きますか？")

    # ボタンを2行に分ける
    row1 = st.columns(2)
    row2 = st.columns(2)
    
    # $0^\circ \sim 180^\circ$
    if row1[0].button(OFFSET_RANGES["0~180"]["label"], use_container_width=True, key="range_0_180"):
        st.session_state.offset_range = "0~180"
        st.session_state.range_selected = True
        initialize_session_state()
        st.rerun()
        
    # $0^\circ \sim 360^\circ$
    if row1[1].button(OFFSET_RANGES["0~360"]["label"], use_container_width=True, key="range_0_360"):
        st.session_state.offset_range = "0~360"
        st.session_state.range_selected = True
        initialize_session_state()
        st.rerun()
        
    # $-180^\circ \sim 180^\circ$
    if row2[0].button(OFFSET_RANGES["-180~180"]["label"], use_container_width=True, key="range_-180_180"):
        st.session_state.offset_range = "-180~180"
        st.session_state.range_selected = True
        initialize_session_state()
        st.rerun()
        
    # 全範囲
    if row2[1].button(OFFSET_RANGES["ALL"]["label"], use_container_width=True, key="range_all"):
        st.session_state.offset_range = "ALL"
        st.session_state.range_selected = True
        initialize_session_state()
        st.rerun()

elif st.session_state.show_result:
    # 結果表示
    end_time = time.time()
    elapsed = Decimal(str(end_time - st.session_state.start_time)).quantize(Decimal('0.01'), ROUND_HALF_UP)

    st.header("✨ クイズ終了！ 結果発表 ✨")
    st.markdown(f"**あなたのスコア: {st.session_state.score} / {MAX_QUESTIONS} 問正解**")
    st.write(f"**経過時間: {elapsed} 秒**")
    st.divider()

    st.subheader("全解答の確認")

    table_data = []
    for i, item in enumerate(st.session_state.history, 1):
        problem_disp = rf"{item['question_disp']} " 
        
        user_latex = RESULT_OPTIONS[item['user_answer_key']]
        correct_latex = RESULT_OPTIONS[item['correct_answer_key']]

        # 純粋な数式文字列を $$ で囲む (LaTeXコンパイルが最も安定する形式)
        user_disp = rf"$$ {user_latex} $$"
        correct_disp = rf"$$ {correct_latex} $$"

        mark = "○" if item['is_correct'] else "×"

        table_data.append({
            "番号": i,
            "問題": problem_disp,
            "あなたの解答": user_disp,
            "正解": correct_disp,
            "正誤": mark
        })

    df = pd.DataFrame(table_data)

    st.table(df.set_index("番号"))

    if st.button("もう一度挑戦する", use_container_width=True, type="primary"):
        st.session_state.clear()
        initialize_session_state() # 範囲選択から再開
        st.rerun()

else:
    # クイズ本体
    st.subheader(f"問題 {st.session_state.question_count + 1} / {MAX_QUESTIONS}")

    current_func = st.session_state.func
    current_offset_key = st.session_state.offset_key
    
    question_latex = rf"$$ \text{{{current_func}}} {OFFSETS[current_offset_key]} $$を簡単にせよ"

    st.markdown(question_latex)
    st.markdown("---")


    # 選択肢の表示（4つのカラムに分割、順番は固定）
    display_options_keys = st.session_state.display_options
    
    cols = st.columns(4)
    for i, key in enumerate(display_options_keys):
        # ボタンのラベルも純粋な数式文字列を $$ で囲む
        latex_label = rf"$$ {RESULT_OPTIONS[key]} $$" 
        
        with cols[i]:
            button_key = f"option_{st.session_state.question_count}_{key}"
            if st.button(latex_label, use_container_width=True, key=button_key):
                check_answer_and_advance(key)
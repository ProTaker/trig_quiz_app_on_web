# trig_transform_quiz_app_final_fixed_v3.py
import streamlit as st
import random
import time
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

# ページ設定
st.set_page_config(page_title="三角比の変換公式クイズ", layout="centered")

# -----------------------------
# CSS（テーブルセルの縦幅を広げる調整を含む）
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
# 変換公式の定義 (変更なし)
# -----------------------------

functions = ["sin", "cos", "tan"]
MAX_QUESTIONS = 10

# 角度オフセットグループの定義
OFFSETS_GROUPS = {
    # 0°〜180°の範囲に対応する変換
    "0_180": ["m90_t", "m180_t", "p90_t", "mneg90_t"], 
    
    # 0°〜360°の範囲に対応する変換
    "0_360": ["m90_t", "m180_t", "m270_t", "p90_t", "p180_t", "p270_t", "m360_t", "p360_t"],

    # -180°〜180°の範囲に対応する変換
    "-180_180": ["neg_t", "m90_t", "m180_t", "p90_t", "mneg90_t", "mneg180_t", "p180_t"],

    # 全範囲（すべての変換をランダムに出題）
    "all_range": ["neg_t", "p90_t", "m90_t", "p180_t", "m180_t", "p270_t", "m270_t", "p360_t", "m360_t", "mneg90_t", "mneg90m_t", "mneg180_t", "mneg180m_t", "mneg270_t", "mneg270m_t"],
}


# LaTeX表示
OFFSETS = {
    "neg_t": r"(-\theta)", "p90_t": r"(90^\circ+\theta)", "m90_t": r"(90^\circ-\theta)",
    "p180_t": r"(180^\circ+\theta)", "m180_t": r"(180^\circ-\theta)", "p270_t": r"(270^\circ+\theta)",
    "m270_t": r"(270^\circ-\theta)", "p360_t": r"(360^\circ+\theta)", "m360_t": r"(360^\circ-\theta)",
    "mneg90_t": r"(-90^\circ+\theta)", "mneg90m_t": r"(-90^\circ-\theta)", 
    "mneg180_t": r"(-180^\circ+\theta)", "mneg180m_t": r"(-180^\circ-\theta)", 
    "mneg270_t": r"(-270^\circ+\theta)", "mneg270m_t": r"(-270^\circ-\theta)",
}

# \dfrac を使用
RESULT_OPTIONS = {
    "sin_t": r"\sin\theta", "-sin_t": r"-\sin\theta",
    "cos_t": r"\cos\theta", "-cos_t": r"-\cos\theta",
    "tan_t": r"\tan\theta", "-tan_t": r"-\tan\theta",
    "cot_t": r"\dfrac{1}{\tan\theta}", 
    "-cot_t": r"-\dfrac{1}{\tan\theta}",
}

SIN_COS_OPTIONS_KEYS = ["sin_t", "-sin_t", "cos_t", "-cos_t"] 
TAN_OPTIONS_KEYS = ["tan_t", "-tan_t", "cot_t", "-cot_t"] 

# 正解データ（最終確定版）
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

# -----------------------------
# セッション操作関数
# -----------------------------
def new_question():
    """新しい問題を生成し、セッション状態を更新する"""
    st.session_state.func = random.choice(functions)
    
    # ★★★ 選択された範囲に基づいて offset_key を選択 ★★★
    selected_range_key = st.session_state.get('angle_range_key', 'all_range')
    available_offsets = OFFSETS_GROUPS.get(selected_range_key, OFFSETS_GROUPS['all_range'])
    st.session_state.offset_key = random.choice(available_offsets)
    # ★★★ 選択処理はここまで ★★★
    
    if st.session_state.func in ["sin", "cos"]:
        options_base = SIN_COS_OPTIONS_KEYS
    else: # tan
        options_base = TAN_OPTIONS_KEYS
        
    st.session_state.display_options = options_base
    st.session_state.selected = None
    st.session_state.show_result = False

def initialize_session_state():
    """セッション状態を初期化する"""
    if 'quiz_started' not in st.session_state:
        # 初期設定画面を出すため、問題を生成しない
        st.session_state.quiz_started = False
        st.session_state.angle_range_key = 'all_range'
    
    if st.session_state.quiz_started and 'score' not in st.session_state:
        st.session_state.score = 0
        st.session_state.question_count = 0
        st.session_state.history = []
        st.session_state.show_result = False
        st.session_state.start_time = time.time()
        # 最初の問題の準備
        new_question()

def start_quiz():
    """クイズ開始ボタンが押されたときの処理"""
    st.session_state.clear() # 既存の状態をリセット
    st.session_state.quiz_started = True
    # 選択した範囲は保持
    # st.session_state.angle_range_key はフォームで更新される
    initialize_session_state()
    st.rerun()
    
def check_answer_and_advance(selected_key):
    """回答をチェックし、次の問題または結果画面へ進む (変更なし)"""
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
# アプリの描画
# -----------------------------------------------

if not st.session_state.quiz_started:
    # ★★★ 初期設定画面 ★★★
    st.header("🎯 出題角度範囲の設定")
    st.markdown("出題される変換公式の角度（例: $180^\circ - \theta$）の範囲を選択してください。")
    st.markdown("---")
    
    range_options = {
        '0_180': r'0^\circ \sim 180^\circ',
        '0_360': r'0^\circ \sim 360^\circ',
        '-180_180': r'-180^\circ \sim 180^\circ',
        'all_range': r'全範囲（-360^\circ \sim 360^\circ 程度）',
    }

    # ラジオボタンで選択
    selected_range_key = st.radio(
        "**出題範囲を選択**",
        options=list(range_options.keys()),
        format_func=lambda x: range_options[x],
        key='angle_range_key' # 選択をセッションステートに保存
    )
    
    st.markdown("---")

    if st.button("クイズ開始", use_container_width=True, type="primary"):
        start_quiz()

elif st.session_state.show_result:
    # 結果表示 (変更なし)
    end_time = time.time()
    elapsed = Decimal(str(end_time - st.session_state.start_time)).quantize(Decimal('0.01'), ROUND_HALF_UP)

    st.header("✨ クイズ終了！ 結果発表 ✨")
    st.markdown(f"**あなたのスコア: {st.session_state.score} / {MAX_QUESTIONS} 問正解**")
    st.write(f"**経過時間: {elapsed} 秒**")
    st.divider()

    st.subheader("全解答の確認")

    table_data = []
    for i, item in enumerate(st.session_state.history, 1):
        problem_disp = rf"{item['question_disp']} = ?" 
        
        user_latex = RESULT_OPTIONS[item['user_answer_key']]
        correct_latex = RESULT_OPTIONS[item['correct_answer_key']]

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
        st.rerun()

else:
    # クイズ本体 (変更なし)
    st.subheader(f"問題 {st.session_state.question_count + 1} / {MAX_QUESTIONS}")

    current_func = st.session_state.func
    current_offset_key = st.session_state.offset_key
    
    question_latex = rf"$$ \text{{{current_func}}} {OFFSETS[current_offset_key]} = ? $$"

    st.markdown(question_latex)
    st.markdown("---")

    display_options_keys = st.session_state.display_options
    
    cols = st.columns(4)
    for i, key in enumerate(display_options_keys):
        latex_label = rf"$$ {RESULT_OPTIONS[key]} $$" 
        
        with cols[i]:
            button_key = f"option_{st.session_state.question_count}_{key}"
            if st.button(latex_label, use_container_width=True, key=button_key):
                check_answer_and_advance(key)
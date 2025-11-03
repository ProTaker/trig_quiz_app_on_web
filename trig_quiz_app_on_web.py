# trig_transform_quiz_app.py
import streamlit as st
import random
import time
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

st.set_page_config(page_title="三角比クイズ（変換公式編）", layout="centered")
st.title("三角比クイズ（変換公式編）")

# -----------------------------
# CSS（ボタンサイズ調整と列幅固定、中央揃え）
# 既存の有名角クイズのCSSを流用
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
# 変換公式の定義
# -----------------------------

# 問題として使用する関数
functions = ["sin", "cos", "tan"]

# 変換のオフセット（例: -θ, 90+θ, 180-θ, ...）
# Streamlitでは特殊文字の表示に r"" ではなく r"$\text{...}$" のような形で \\ を使わないLaTeXが必要
# 内部キーをシンプルに保つため、キーは簡略化
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

# 変換後の結果（正解）
# キー: 変換後の式を識別する内部名
# 値: 変換後の式をLaTeXで表示するための文字列
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

# 全ての選択肢（重複を避けるためにセットからリストへ）
all_result_keys = list(RESULT_OPTIONS.keys())


# 問題と正解の対応表 (func, offset) -> result_key
# ユーザーが提供した公式データに基づき定義
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
        "neg_t": "-tan_t", "p90_t": "-cot_t", "m90_t": "cot_t", # 90+θの正解を1/tanθから-1/tanθに修正
        "p180_t": "tan_t", "m180_t": "-tan_t", "p270_t": "-cot_t",
        "m270_t": "cot_t", "p360_t": "tan_t", "m360_t": "-tan_t",
    },
}

# 選択肢の表示順序（ランダムに4つ選ぶためのベース）
SHUFFLED_OPTIONS_BASE = all_result_keys.copy()


MAX_QUESTIONS = 10

# -----------------------------
# セッション操作関数
# -----------------------------
def generate_options(correct_key):
    """正解を含む4つの選択肢のキーリストを生成し、シャッフルする"""
    incorrect_keys = [k for k in all_result_keys if k != correct_key]
    
    # 不正解の選択肢からランダムに3つ選ぶ
    if len(incorrect_keys) >= 3:
        random_incorrect = random.sample(incorrect_keys, 3)
    else:
        # 不足分は全選択肢から重複を許して選ぶが、通常は発生しない
        random_incorrect = random.sample(incorrect_keys * 2, 3)

    options = [correct_key] + random_incorrect
    random.shuffle(options)
    return options

def new_question():
    """新しい問題を生成し、セッション状態を更新する"""
    st.session_state.func = random.choice(functions)
    st.session_state.offset_key = random.choice(list(OFFSETS.keys()))
    
    # 正解のキーを取得
    correct_key = TRANSFORM_ANSWERS[st.session_state.func][st.session_state.offset_key]
    
    # 選択肢を生成し、セッションに保存
    st.session_state.display_options = generate_options(correct_key)
    
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

    # 回答処理後にページを再描画して次の問題へ
    st.rerun()

# 初期化呼び出し (ここでは 'quiz_started' の状態だけを見る)
if 'quiz_started' not in st.session_state:
    initialize_session_state()

# -----------------------------------------------
# アプリの描画
# -----------------------------------------------

if not st.session_state.quiz_started:
    # クイズ開始画面
    st.header("三角比の変換公式クイズ")
    st.write("$\sin(90^\circ+\theta)$ のように、角度が変換されたときの三角比の値を答えるクイズです。")
    st.markdown(f"全 **{MAX_QUESTIONS}** 問に挑戦します。")
    st.markdown("---")
    if st.button("クイズ開始", use_container_width=True, type="primary"):
        start_quiz()

elif st.session_state.show_result:
    # 結果表示
    end_time = time.time()
    elapsed = Decimal(str(end_time - st.session_state.start_time)).quantize(Decimal('0.01'), ROUND_HALF_UP)

    st.header("✨ クイズ終了！ 結果発表 ✨")
    st.markdown(f"**あなたのスコア: {st.session_state.score} / {MAX_QUESTIONS} 問正解**")
    st.write(f"**経過時間: {elapsed} 秒**")
    st.divider()

    st.subheader("全解答の確認")

    # DataFrame生成
    table_data = []
    for i, item in enumerate(st.session_state.history, 1):
        # 問題と解答を $$ で囲んで表示準備
        problem_disp = rf"$$ {item['question_disp']} $$"
        user_disp = rf"$$ {RESULT_OPTIONS[item['user_answer_key']]} $$"
        correct_disp = rf"$$ {RESULT_OPTIONS[item['correct_answer_key']]} $$"
        mark = "○" if item['is_correct'] else "×"

        table_data.append({
            "番号": i,
            "問題": problem_disp,
            "あなたの解答": user_disp,
            "正解": correct_disp,
            "正誤": mark
        })

    df = pd.DataFrame(table_data)

    # インデックスを番号にして表示（CSSで中央揃え等を維持）
    # Streamlitのst.tableは、内部のMarkdown/LaTeXをHTMLに変換して表示する
    st.table(df.set_index("番号"))

    if st.button("もう一度挑戦する", use_container_width=True):
        # セッションをクリアして再スタート
        st.session_state.clear()
        # 'quiz_started'をFalseに戻して初期画面へ
        st.session_state.quiz_started = False 
        initialize_session_state()
        st.rerun()

else:
    # クイズ本体
    st.subheader(f"問題 {st.session_state.question_count + 1} / {MAX_QUESTIONS}")

    current_func = st.session_state.func
    current_offset_key = st.session_state.offset_key
    
    # 問題文の LaTeX 表示
    question_latex = rf"$$ \text{{{current_func}}} {OFFSETS[current_offset_key]} = ? $$"

    st.markdown(question_latex)
    st.markdown("---")


    # 選択肢の表示（4つのカラムに分割）
    display_options_keys = st.session_state.display_options
    cols = st.columns(4)
    for i, key in enumerate(display_options_keys):
        # 選択肢のLaTeX表示文字列を取得
        latex_label = rf"$$ {RESULT_OPTIONS[key]} $$" 
        
        # Streamlitのボタンは押された時にスクリプトを最初から再実行する
        # on_clickとargs/kwargsを使用して、ボタンが押された時の処理と引数を指定するのが標準的な方法
        # ただし、現状のコード構造（st.rerunに依存）に合わせて、ボタンの戻り値で処理を行う
        with cols[i % 4]:
            button_key = f"option_{st.session_state.question_count}_{key}"
            # ボタンが押されたら check_answer_and_advance を呼び出す
            if st.button(latex_label, use_container_width=True, key=button_key):
                # どのボタンが押されたかを引数として渡し、回答を処理
                check_answer_and_advance(key)
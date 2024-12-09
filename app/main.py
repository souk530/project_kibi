import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
from app.utils.data_loader import DataLoader
from app.utils.map_utils import MapUtils
from app.utils.components import ShowDetailPage
from app.utils.custom_css import CustomCSS
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# ページ全体の設定
st.set_page_config(page_title="観光アプリ", layout="wide", initial_sidebar_state="expanded")
# CSSの適用
CustomCSS.apply("style.css")

# データの読み込み
model_route = DataLoader.load_model_route()
tourist_list = DataLoader.load_tourist_list()

# サイドバーのカスタマイズナビゲーション
with st.sidebar:
    selected_page = option_menu(
        "",
        ["観光地リスト", "観光地マップ", "観光地提案", "おはなし"],  # 新しい項目を追加
        icons=["list", "map", "lightbulb", "volume-up"],  # アイコンも追加
        menu_icon="menu-app",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#00274d"},
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "padding": "10px 15px",
                "color": "white",
            },
            "nav-link-selected": {
                "background-color": "#1e90ff",  # 選択時の背景色
                "color": "white",  # 選択時の文字色
                "font-weight": "bold",  # 選択時の文字を太字に
            },
        },
    )


# 観光地リストページ
def display_list_page():
    st.title("観光地リスト")

    # 選択された観光地を追跡するためのセッションステート
    if "selected_spot" not in st.session_state:
        st.session_state.selected_spot = None

    # 詳細ページが選択された場合の処理
    if st.session_state.selected_spot is not None:
        ShowDetailPage.display(st.session_state.selected_spot)
        return

    # 検索機能
    search_query = st.text_input("検索（観光地名やタグで絞り込み）:")
    filtered_tourist_list = filter_tourist_list(search_query)

    # ページネーションを含む観光地リストの表示
    paginate_and_display(filtered_tourist_list)

def paginate_and_display(filtered_list):
    """ページネーションを適用し、観光地を表示"""
    items_per_page = 20
    current_page = st.session_state.get("current_page", 1)
    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    # リストの表示
    for _, row in filtered_list.iloc[start_idx:end_idx].iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                if pd.notna(row["画像"]):
                    st.image(row["画像"], use_container_width=True)
            with col2:
                st.markdown(f"### {row['観光地名']}")
                st.write(f"- **タグ**: {row['タグ']}")
                st.write(f"- **住所**: {row['住所']}")
                # 詳細を見るボタンをクリックするとセッションを更新
                if st.button("詳細を見る", key=f"detail_{row['観光地名']}"):
                    st.session_state.selected_spot = row

    # ページネーションコントロールの表示
    display_pagination_controls(filtered_list, items_per_page, current_page)

def display_pagination_controls(filtered_list, items_per_page, current_page):
    """ページネーションのコントロールを表示"""
    total_pages = (len(filtered_list) + items_per_page - 1) // items_per_page

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("＜ 前ページ", disabled=current_page == 1):
            st.session_state.current_page = max(1, current_page - 1)
    with col3:
        if st.button("次ページ ＞", disabled=current_page >= total_pages):
            st.session_state.current_page = min(total_pages, current_page + 1)



def filter_tourist_list(query):
    """検索クエリに基づいて観光地リストをフィルタリング"""
    if query:
        return tourist_list[
            tourist_list["観光地名"].str.contains(query, case=False, na=False) |
            tourist_list["タグ"].str.contains(query, case=False, na=False)
        ]
    return tourist_list


# 観光地マップページ
def display_map_page():
    st.title("観光地マップ")
    map_center = [34.8609, 133.8118]
    m = MapUtils.create_map(tourist_list, map_center)
    st_folium(m, width=700, height=500)

    display_selected_spot()

def display_selected_spot():
    query_params = st.query_params
    if "spot" in query_params:
        clicked_name = query_params["spot"]
        if clicked_name:
            selected_spot = tourist_list[tourist_list["観光地名"] == clicked_name].iloc[0]
            st.session_state.selected_spot = selected_spot
            ShowDetailPage.display(selected_spot)

# 観光地提案ページ
def display_proposal_page():
    st.title("質問に答えて観光地を検索")

    # 質問に対する回答を収集
    responses = collect_responses()

    # ボタンのスタイルを適用
    button_css = """
    <style>
      div.stButton > button:first-child  {
        font-weight: bold;             /* 文字を太字に */
        border: 2px solid #00509e;     /* 青色の枠線 */
        border-radius: 8px;            /* 角を丸める */
        background: #00509e;           /* 背景色を青色に */
        color: white;                  /* 文字色を白に */
        padding: 0.6rem 1.2rem;        /* 余白を調整 */
        cursor: pointer;               /* マウスをホバー時にポインタ */
        transition: all 0.3s ease;     /* なめらかなアニメーション */
      }
      div.stButton > button:first-child:hover {
        background: #003f7f;           /* ホバー時の背景色 */
        border-color: #003f7f;         /* ホバー時の枠線色 */
      }
      div.stButton > button:first-child:active {
        background: #00274d;           /* 押下時の背景色 */
        border-color: #00274d;         /* 押下時の枠線色 */
      }
    </style>
    """
    st.markdown(button_css, unsafe_allow_html=True)

    # ボタンが押された場合のみ結果を表示
    if st.button("回答を送信"):
        display_results(responses)

def collect_responses():
    questions_data = [
        {"質問": "Q1. 今やりたいことは？", "選択肢": ['美味しい物を食べたい！', '自然を感じたい！', '文化に触れたい！', 'リフレッシュしたい！']},
        {"質問": "Q2. どんな風に観光したいですか？", "選択肢": ['一人で静かに', '友人と楽しく', '家族水入らずで']},
        {"質問": "Q3. あなたの年代は？", "選択肢": ['10代以下', '20代', '30代', '40代', '50代']},
        {"質問": "Q4. 交通手段は？", "選択肢": ['自動車・バイク・原付', '自転車・徒歩', '電車・バス']}
    ]
    responses = {}
    for question_data in questions_data:
        question = question_data["質問"]
        options = question_data["選択肢"]
        responses[question] = st.selectbox(question, options)
    return responses

def display_results(responses):
    filtered_data = model_route[
        (model_route["Q1. 今やりたいことは？"] == responses["Q1. 今やりたいことは？"]) &
        (model_route["Q2. どんな風に観光したいですか？"] == responses["Q2. どんな風に観光したいですか？"]) &
        (model_route["Q3. あなたの年代は？"] == responses["Q3. あなたの年代は？"]) &
        (model_route["Q4. 交通手段は？"] == responses["Q4. 交通手段は？"])
    ]
    if not filtered_data.empty:
        st.subheader("おすすめの観光地")
        for i in range(1, 4):  # 最大3つの提案を表示
            column_name = f"Q1による観光地{i}"
            if column_name in filtered_data.columns:
                display_spot_details(filtered_data.iloc[0][column_name])
    else:
        st.write("該当する観光地が見つかりませんでした。")

def display_spot_details(spot_name):
    spot_info = tourist_list[tourist_list["観光地名"] == spot_name]

    if not spot_info.empty:
        spot_row = spot_info.iloc[0]
        st.markdown(f"### {spot_name}")

        # 画像表示
        if pd.notna(spot_row["画像"]):
            st.image(spot_row["画像"], caption=spot_name, use_container_width=True)

        # タグ
        st.write(f"- **タグ**: {spot_row['タグ']}")

        # 電話番号
        st.write(f"- **電話番号**: {spot_row['電話番号'] or '情報なし'}")

        # Google Map埋め込み
        if pd.notna(spot_row["緯度経度"]):
            try:
                lat_lon = spot_row["緯度経度"].split(',')
                if len(lat_lon) == 2:
                    latitude, longitude = map(float, lat_lon)
                    map_url = f"https://www.google.com/maps?q={latitude},{longitude}&z=15&output=embed"
                    st.components.v1.iframe(map_url, height=400)
            except ValueError:
                st.write("- 緯度経度情報が不正です。")
        else:
            st.write("- 緯度経度情報がありません。")
    else:
        st.write(f"- 情報が見つかりませんでした: {spot_name}")

def display_audio_page():
    st.title("おはなし")

    # データの読み込み
    audio_data = pd.read_csv("朝日塾_語り.csv")  # 適切なファイルパスに置き換えてください

    # 各行のデータをカード形式で表示
    for _, row in audio_data.iterrows():
        with st.container():
            # カードのスタイルを設定
            st.markdown(
                """
                <style>
                .card {
                    background-color: #f9f9f9;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }
                .card img {
                    width: 100%;
                    height: auto;
                    border-radius: 10px;
                }
                .card h3 {
                    margin-top: 10px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            # カードの内容を表示
            st.markdown('<div class="card">', unsafe_allow_html=True)

            # ヘッダー画像
            if pd.notna(row["ヘッダー"]):
                st.image(row["ヘッダー"], use_container_width=True)

            # タイトル
            st.subheader(row["タイトル"])

            # 日本語音声
            if pd.notna(row["音声"]):
                st.audio(row["音声"], format="audio/mp3", start_time=0)

            # 英語音声
            if pd.notna(row["音声英語"]):
                st.write("英語版")
                st.audio(row["音声英語"], format="audio/mp3", start_time=0)

            # 中国語音声
            if pd.notna(row["音声中国"]):
                st.write("中国語版")
                st.audio(row["音声中国"], format="audio/mp3", start_time=0)

            st.markdown('</div>', unsafe_allow_html=True)

# ページ切り替え部分に追加
if selected_page == "観光地リスト":
    display_list_page()
elif selected_page == "観光地マップ":
    display_map_page()
elif selected_page == "観光地提案":
    display_proposal_page()
elif selected_page == "おはなし": 
    display_audio_page()

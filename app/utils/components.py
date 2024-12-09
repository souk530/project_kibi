import streamlit as st
import pandas as pd

class ShowDetailPage:
    """観光地の詳細ページを表示するクラス"""

    @staticmethod
    def display(spot_data):
        st.title(spot_data["観光地名"])
        
        if pd.notna(spot_data["画像"]):
            st.image(spot_data["画像"], use_container_width=True)

        st.markdown(f"**タグ**: {spot_data['タグ']}")

        st.subheader("基本情報")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**電話番号**: {spot_data['電話番号'] or 'なし'}")
        with col2:
            if pd.notna(spot_data["ホームページ"]):
                st.write(f"[ホームページはこちら]({spot_data['ホームページ']})")

        st.subheader("Google Map")
        if pd.notna(spot_data["緯度経度"]):
            lat_lon = spot_data["緯度経度"].split(',')
            if len(lat_lon) == 2:
                latitude, longitude = lat_lon
                map_url = f"https://www.google.com/maps?q={latitude},{longitude}&z=15&output=embed"
                st.components.v1.iframe(map_url, height=400)

        st.subheader("詳細情報")
        st.markdown(spot_data["詳細説明"] or "詳細情報はありません。")

        st.subheader("ギャラリー")
        for img in [spot_data[f"追加画像{i}"] for i in range(1, 5) if pd.notna(spot_data[f"追加画像{i}"])]:
            st.image(img, use_container_width=True)

        if st.button("戻る"):
            st.session_state.selected_spot = None

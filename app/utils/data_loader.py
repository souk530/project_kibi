import pandas as pd
import streamlit as st

class DataLoader:
    """データの読み込みを担当するクラス"""
    
    @staticmethod
    @st.cache_data
    def load_model_route():
        """モデルルートデータを読み込む"""
        return pd.read_csv('モデルルート.csv')

    @staticmethod
    @st.cache_data
    def load_tourist_list():
        """観光地リストデータを読み込む"""
        return pd.read_csv('観光地リスト_11.csv')

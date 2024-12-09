import streamlit as st
from pathlib import Path

class CustomCSS:
    """CSS適用を担当するクラス"""

    @staticmethod
    def apply(file_name: str):
        """指定されたCSSファイルを読み込み適用する"""
        try:
            # デフォルトパスの設定
            css_path = Path(file_name)
            if not css_path.is_file():
                raise FileNotFoundError(f"CSSファイルが見つかりません: {file_name}")

            # ファイルの読み込み
            with css_path.open("r", encoding="utf-8") as f:
                css_content = f.read()

            # CSSを適用
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"CSSの適用中にエラーが発生しました: {e}")

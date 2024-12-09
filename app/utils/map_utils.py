import folium
from folium import Popup
import pandas as pd


class MapUtils:
    """地図作成ユーティリティクラス"""

    @staticmethod
    def create_map(tourist_list, map_center):
        """観光地の地図を作成"""
        m = folium.Map(location=map_center, zoom_start=11)

        for _, row in tourist_list.iterrows():
            # 緯度経度が有効かどうかを確認
            if pd.notna(row["緯度経度"]):
                try:
                    lat_lon = row["緯度経度"].split(',')
                    if len(lat_lon) == 2:
                        latitude, longitude = map(float, lat_lon)

                        # ピンにポップアップを設定
                        image_html = f"""
                        <a href="?spot={row['観光地名']}" target="_self">
                            <img src='{row['画像']}' width='200' style='border-radius:10px;' />
                        </a>
                        """
                        popup_html = f"""
                        <div style="text-align:center;">
                            {image_html}
                            <p><b>{row['観光地名']}</b></p>
                        </div>
                        """
                        popup = Popup(popup_html, max_width=300)
                        folium.Marker(
                            location=[latitude, longitude],
                            popup=popup,
                            tooltip=row["観光地名"]
                        ).add_to(m)
                except (ValueError, AttributeError) as e:
                    # 無効な緯度経度データをスキップ
                    print(f"Invalid coordinate data: {row['緯度経度']}, error: {e}")

        return m

"""
このモジュールは指定の文字列を描画した画像を作成します。
Streamlit で動作します。
"""

import imageio
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


class ImageGenerator:
    """
    Pillow ライブラリを利用して画像データを作成します
    """

    def __init__(
        self,
        image_size: int = 128,
        bg_color: str = "black",
        font_color: str = "green",
        stroke_width: int = 1,
        font_path: str = "fonts/IPAfont00303/ipag.ttf",
        spacing: float = 4.0,
    ):
        """
        コンストラクタ
        Pillow Image を初期化して背景を描画します。
        """
        self.bg_color = bg_color
        self.font_color = font_color
        self.stroke_width = stroke_width
        self.font_path = font_path
        self.spacing = spacing

        self.img = Image.new(
            "RGBA", (image_size, image_size), color=(255, 255, 255, 0)
        )
        self.draw = ImageDraw.Draw(self.img)
        self.fill_background()

    def get_pil_image(self):
        """
        画像データを返します
        """
        return self.img

    def fill_background(self):
        """
        背景を描画します
        """
        self.draw.rectangle(
            (0, 0, self.img.width, self.img.height), fill=self.bg_color
        )

    def _getbbox_split_lines(self, text, font):
        """
        文字列を改行で分割して Bounding Box のサイズを計算します
        """
        text_by_line = text.split("\n")

        width = max([font.getbbox(x)[2] for x in text_by_line])
        height = sum(
            [
                font.getbbox(x, stroke_width=self.stroke_width)[3]
                + self.spacing
                + self.stroke_width
                for x in text_by_line
            ]
        )
        return width, height

    def draw_text(
        self,
        text: str,
        font_size: float = None,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
        align: str = "center",
    ):

        # 指定のフォントサイズで描画
        font = ImageFont.truetype(self.font_path, font_size)
        text_width, text_height = self._getbbox_split_lines(
            text,
            font,
        )
        x = (self.img.width) / 2 + x_offset
        y = (self.img.height) / 2 + y_offset

        self.draw.multiline_text(
            (x, y),
            text,
            font=font,
            fill=self.font_color,
            anchor="mm",
            stroke_width=self.stroke_width,
            spacing=self.spacing,
            align=align,
        )

    def draw_text_auto_fit(
        self,
        text: str,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
        align: str = "center",
    ):
        # 計測用の仮のフォントで幅と高さを計算
        temp_font_size = 100.0
        font = ImageFont.truetype(self.font_path, temp_font_size)
        text_width, text_height = self._getbbox_split_lines(
            text,
            font,
        )
        ratio = max(text_width / self.img.width, text_height / self.img.height)

        # フィットするフォントサイズを設定
        font_size = temp_font_size / ratio

        self.draw_text(
            text, font_size, x_offset=x_offset, y_offset=y_offset, align=align
        )

    def draw_particle(self, num_particles=20, max_particle_size=10):
        """
        粒子を表示する
        """
        low = np.array([0, 0, 0, 192, 192, 192])
        high = np.array(
            [self.img.width, self.img.height, max_particle_size, 230, 230, 230]
        )
        values = np.random.randint(
            low[:, np.newaxis],
            high[:, np.newaxis],
            size=(6, num_particles),
            dtype=int,
        ).T
        for e in values:
            x = e[0]
            y = e[1]
            size = e[2]
            color = (e[3], e[4], e[5])
            self.draw.ellipse((x, y, x + size, y + size), fill=color)


def create_main_panel(main_panel, gif_bytes, text_input):

    # GIF データ表示
    main_panel.image(gif_bytes)

    # ダウンロード
    download_filename = text_input.replace("\n", "") + ".gif"
    main_panel.download_button(
        "画像をダウンロード", gif_bytes, file_name=download_filename
    )


def create_control_panel(control_panel):
    text_input = control_panel.text_area(
        "画像に入れたい文字:", value="あざ\nます"
    ).strip()

    with control_panel.container(border=True):
        cols = st.columns(2)
        font_color = cols[0].color_picker("文字の色", "#E204F7")
        bg_transparent = st.checkbox("背景を透明にする", value=False)
        bg_color = cols[1].color_picker(
            "背景の色", "#111111", disabled=bg_transparent
        )
        if bg_transparent:
            bg_color = "#00000000"

    with control_panel.container(border=True):
        cols = st.columns(3)
        if st.checkbox("文字を画像にフィットさせる", value=True):
            font_size_auto = True
        else:
            font_size_auto = False

        font_size = cols[0].slider(
            "フォントのサイズ:",
            min_value=10,
            max_value=300,
            value=70,
            disabled=font_size_auto,
        )
        stroke_width = cols[1].slider(
            "線の太さ:", min_value=0, max_value=4, value=1
        )
        spacing = cols[2].slider("行間幅:", min_value=0, max_value=10, value=4)

    with control_panel.container(border=True):
        cols = st.columns(3)
        radius = cols[0].slider(
            "移動半径:", min_value=0, max_value=64, value=8, step=4
        )
        fps = cols[1].slider(
            "フレームレート:", min_value=1, max_value=10, value=5
        )
        total_frames = cols[2].slider(
            "トータルフレーム数:", min_value=1, max_value=50, value=10
        )
    with control_panel.container(border=True):
        draw_particle = st.checkbox("パーティクルを表示する", value=True)

    return (
        text_input,
        font_color,
        bg_color,
        bg_transparent,
        font_size_auto,
        font_size,
        stroke_width,
        spacing,
        radius,
        fps,
        total_frames,
        draw_particle,
    )


def main():
    """
    メイン処理
    """

    # フォントを指定
    font_path = "fonts/IPAfont00303/ipag.ttf"
    image_size: int = 128  # slack 公式に絵文字サイズの記載あり

    # タイトルを描画
    st.title("文字 GIF メーカー")

    # 分割
    main_panel, control_panel = st.columns([0.3, 0.7])

    # メインパネルを描画
    (
        text_input,
        font_color,
        bg_color,
        bg_transparent,
        font_size_auto,
        font_size,
        stroke_width,
        spacing,
        radius,
        fps,
        total_frames,
        draw_particle,
    ) = create_control_panel(control_panel)

    # frame 毎に画像を作成
    frames = []
    for frame_ts in np.linspace(0, 1, total_frames, endpoint=False):

        # フレームを初期化
        generator = ImageGenerator(
            image_size=image_size,
            bg_color=bg_color,
            font_color=font_color,
            stroke_width=stroke_width,
            font_path=font_path,
            spacing=spacing,
        )

        # 描画位置を決める
        x_offset = float(radius * np.sin(-2 * np.pi * frame_ts))
        y_offset = float(radius * np.cos(-2 * np.pi * frame_ts))

        # 粒子を表示
        if draw_particle:
            generator.draw_particle()

        # 描画
        if font_size_auto:
            generator.draw_text_auto_fit(
                text_input,
                x_offset=x_offset,
                y_offset=y_offset,
            )
        else:
            generator.draw_text(
                text_input,
                font_size=font_size,
                x_offset=x_offset,
                y_offset=y_offset,
            )

        # フレームリストに追加
        frames.append(generator.get_pil_image())

    # GIF データ作成
    gif_bytes = imageio.mimsave(
        imageio.RETURN_BYTES, frames, format="GIF", fps=fps, loop=0
    )

    # GIF データを描画
    create_main_panel(main_panel, gif_bytes, text_input)


if __name__ == "__main__":
    main()

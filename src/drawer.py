"""
このモジュールは指定の文字列を描画した画像を作成します。
"""

from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.animation import Animation


class Drawer(ABC):
    """
    Animation class に描画するクラスの抽象クラス
    """

    def __init__(self) -> None:
        """
        コンストラクタ
        """
        pass

    @abstractmethod
    def draw(self, animation: Animation) -> None:
        """
        描画
        """
        pass


class FillDrawer(Drawer):
    """
    フレーム全体を指定の色で塗りつぶす Drawer
    """

    def __init__(
        self, color: Tuple[int, int, int, int] = (0, 0, 0, 255)
    ) -> None:
        """
        コンストラクタ
        """
        super().__init__()
        self.color = color

    def draw(self, animation: Animation) -> None:
        """
        単一色で塗りつぶし
        """
        for frame in animation.frames:
            draw = ImageDraw.Draw(frame)
            draw.rectangle((0, 0, frame.width, frame.height), fill=self.color)


class TextDrawer(Drawer):
    """
    文字を描画するクラス
    """

    def __init__(
        self,
        text: str,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
        align: str = "center",
        anchor: str = "mm",
        spacing: int = 4,
        stroke_width: int = 0,
        font_color: str = "#808080",
        font_size: float = 20,
        font_path: str = "fonts/IPAfont00303/ipag.ttf",
        enable_fit_text_to_frame: bool = False,
    ) -> None:
        """
        コンストラクタ
        """
        super().__init__()

        # テキスト
        self.text = text

        # 位置指定
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.align = align
        self.anchor = anchor
        self.spacing = spacing

        # font
        self.stroke_width = stroke_width
        self.font_color = font_color
        self.font_size = font_size
        self.font_path = font_path
        self._update_font()

        # fit font size
        self.enable_fit_text_to_frame = enable_fit_text_to_frame

    def draw(self, animation: Animation) -> None:
        """
        文字を描画
        """

        for frame_index, frame in enumerate(animation.frames):

            self.draw_text_simple(frame)

    def draw_text_simple(self, frame: Image) -> None:
        """
        フレームに文字を描画する
        """

        # ImageDraw を取得
        draw = ImageDraw.Draw(frame)

        # フォントサイズを調整
        if self.enable_fit_text_to_frame:
            self.fit_text_to_frame(frame)

        # 座標を計算
        x = (frame.width) / 2 + self.x_offset
        y = (frame.height) / 2 + self.y_offset

        # テキストを描画
        draw.multiline_text(
            (x, y),
            self.text,
            font=self.font,
            fill=self.font_color,
            anchor=self.anchor,
            stroke_width=self.stroke_width,
            spacing=self.spacing,
            align=self.align,
        )

    def getbbox(self, draw: ImageDraw, font: ImageFont = None) -> Tuple[int]:
        """
        文字列を描画する際の幅と高さを取得
        """

        if font is None:
            font = self.font

        # テキストのサイズを取得
        left, top, text_width, text_height = draw.multiline_textbbox(
            (0, 0),
            self.text,
            font=font,
            spacing=self.spacing,
            anchor=self.anchor,
            stroke_width=self.stroke_width,
        )

        return (text_width - left), (text_height - top)

    def fit_text_to_frame(
        self,
        frame: Image,
        temp_font_size=100.0,
    ) -> None:
        """
        フレームサイズ一杯にフォントサイズを調整
        """

        # 計測用の仮のフォントで幅と高さを計算
        temp_font = ImageFont.truetype(self.font_path, temp_font_size)
        text_width, text_height = self.getbbox(
            ImageDraw.Draw(frame), font=temp_font
        )

        # 倍率を計算
        ratio = max(text_width / frame.width, text_height / frame.height)

        # フィットするフォントサイズを設定
        self.font_size = temp_font_size / ratio

    def _update_font(self) -> None:
        self.font = ImageFont.truetype(self.font_path, self.font_size)


class RandomParticleDrawer(Drawer):
    """
    ランダムな粒子を描画する
    """

    def __init__(
        self,
        particle_count: int = 20,
        max_particle_size: int = 10,
        color_low: int = 192,
        color_high: int = 255,
    ):
        """
        コンストラクタ
        """
        super().__init__()
        self.particle_count = particle_count
        self.max_particle_size = max_particle_size
        self.color_low = color_low
        self.color_high = color_high

    def draw(self, animation: Animation) -> None:
        """
        ランダムな場所にランダムなサイズの粒子を表示する
        """

        # 下限値
        low = np.array(
            [0, 0, 1, self.color_low, self.color_low, self.color_low]
        )

        # 上限値
        high = np.array(
            [
                animation.frame_width,
                animation.frame_height,
                self.max_particle_size,
                self.color_high,
                self.color_high,
                self.color_high,
            ]
        )

        # フレームごとに処理
        for frame in animation.frames:

            # ランダム値を生成
            params = np.random.randint(
                low[:, np.newaxis],
                high[:, np.newaxis],
                size=(6, self.particle_count),
                dtype=int,
            ).T

            # フレームから ImageDraw を取得
            draw = ImageDraw.Draw(frame)
            for param in params:

                # 座標計算など
                size = param[2]
                x = param[0] - size // 2
                y = param[1] - size // 2
                color = (param[3], param[4], param[5])

                # 描画
                draw.ellipse((x, y, x + size, y + size), fill=color)

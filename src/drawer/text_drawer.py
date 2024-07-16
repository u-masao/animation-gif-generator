"""
このモジュールは指定の文字列を描画した画像を作成します。
"""

from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src import Animation
from src.drawer.drawer import Drawer


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
        bg_color: Optional[Tuple[int]] = None,
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
        self.bg_color = bg_color

        # fit font size
        self.enable_fit_text_to_frame = enable_fit_text_to_frame

    def draw(self, animation: Animation) -> None:
        """
        文字を描画
        """

        if self.bg_color is None:
            self.bg_color = animation.bg_color

        for frame_index, frame in enumerate(animation.frames):
            self.draw_text_simple(frame)

    def draw_text_simple(
        self,
        frame: Image,
        x_offset: Optional[float] = None,
        y_offset: Optional[float] = None,
    ) -> None:
        """
        フレームに文字を描画する
        """

        # offset を計算
        if x_offset is None:
            x_offset = self.x_offset
        if y_offset is None:
            y_offset = self.y_offset

        # フォントサイズを調整
        if self.enable_fit_text_to_frame:
            # フォントサイズを調整してフレームいっぱいに伸縮した文字を描画
            self.draw_text_fit_and_strech(frame, x_offset, y_offset)
            return

        # 座標を計算
        x, y = (frame.width) / 2 + x_offset, (frame.height) / 2 + y_offset

        # ImageDraw を取得
        draw = ImageDraw.Draw(frame)

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

    def draw_text_fit_and_strech(
        self, frame: Image, x_offset: float, y_offset: float
    ):

        # 仮のフォントサイズで文字列の描画サイズを取得
        text_width, text_height = self.get_text_size()

        # アスペクト比でフレームサイズを修正
        aspect_ratio = text_width / text_height
        frame_width, frame_height = frame.width, frame.height
        if aspect_ratio > 1:
            frame_width = int(frame_width * aspect_ratio)
        else:
            frame_height = int(frame_height / aspect_ratio)

        # フォントサイズを変更
        self.fit_text_to_frame(frame, mode="min")

        resized_frame = self._make_resized_frame(
            frame,
            frame_width,
            frame_height,
            mode="draw",
        )
        resized_frame_mask = self._make_resized_frame(
            frame,
            frame_width,
            frame_height,
            mode="mask",
        )
        frame.paste(
            resized_frame,
            (int(x_offset), int(y_offset)),
            mask=resized_frame_mask,
        )

    def _make_resized_frame(
        self,
        frame: Image,
        frame_width: int,
        frame_height: int,
        mode: str = "draw",
    ):

        # モードにより色を変更
        if mode == "draw":
            bg_color = self.bg_color
            color = self.font_color
        elif mode == "mask":
            bg_color = (0, 255, 0, 255)
            color = (255, 255, 255, 255)
        else:
            ValueError(f"その mode には対応していません: {mode}")

        # テキスト描画用の Image を作成
        text_frame = Image.new("RGBA", (frame_width, frame_height))

        # ImageDraw を取得
        text_draw = ImageDraw.Draw(text_frame)

        # 背景を描画
        text_draw.rectangle(
            (0, 0, text_frame.width, text_frame.height), fill=bg_color
        )

        # 文字のサイズを取得
        text_width, text_height = self.getbbox(ImageDraw.Draw(text_frame))

        # 文字を描画
        text_draw.multiline_text(
            (text_frame.width / 2, text_frame.height / 2),
            self.text,
            font=self.font,
            fill=color,
            anchor="mm",
            stroke_width=self.stroke_width,
            spacing=self.spacing,
            align=self.align,
        )

        # リサイズ
        resized_frame = text_frame.resize((frame.width, frame.height))

        # マスクモード時は R チャンネルを Image で返す
        if mode == "mask":
            return resized_frame.split()[0]

        # リサイズ済み Image を返す
        return resized_frame

    def getbbox(self, draw: ImageDraw, font: ImageFont = None) -> Tuple[int]:
        """
        文字列を描画する際の幅と高さを取得
        """

        # フォントを設定
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

    def get_text_size(
        self,
        temp_font_size: float = 100.0,
        temp_image_size: int = 10000,
    ):
        """
        計測用の Image と仮のフォントサイズでテキストのサイズを計測
        """

        # 計測用の仮のフォントで幅と高さを計算
        temp_frame = Image.new("RGBA", (temp_image_size, temp_image_size))
        temp_font = ImageFont.truetype(self.font_path, temp_font_size)
        text_width, text_height = self.getbbox(
            ImageDraw.Draw(temp_frame), font=temp_font
        )

        return text_width, text_height

    def fit_text_to_frame(
        self,
        frame: Image,
        mode: str = "max",
        temp_font_size: float = 100.0,
    ) -> None:
        """
        フレームサイズ一杯にフォントサイズを調整
        """

        # 仮のフォントで文字の幅と高さを計算
        text_width, text_height = self.get_text_size(
            temp_font_size=temp_font_size
        )

        # フィット方法により比率を計算
        if mode == "max":
            ratio = max(text_width / frame.width, text_height / frame.height)
        elif mode == "min":
            ratio = min(text_width / frame.width, text_height / frame.height)
        else:
            ValueError(f"その mode はサポートしていません: {mode}")

        # フィットするフォントサイズを設定
        self.font_size = temp_font_size / ratio
        self._update_font()

    def _update_font(self) -> None:
        """
        フォントを変更
        """
        self.font = ImageFont.truetype(self.font_path, self.font_size)


class CircleMoveTextDrawer(TextDrawer):

    def __init__(
        self,
        *args,
        radius: float = 32.0,
        **kwargs,
    ) -> None:
        """
        コンストラクタ。移動半径を指定可能。
        """
        super().__init__(*args, **kwargs)
        self.radius: float = radius

    def draw(self, animation: Animation) -> None:
        """
        文字を描画
        """

        # 背景色を設定
        if self.bg_color is None:
            self.bg_color = animation.bg_color

        # フレームごとに処理
        for frame_index, frame in enumerate(animation.frames):

            # frame timestamp を作成
            frame_ts = frame_index / len(animation.frames)

            # 描画位置を決める
            x_offset = float(self.radius * np.sin(-2 * np.pi * frame_ts))
            y_offset = float(self.radius * np.cos(-2 * np.pi * frame_ts))

            # 描画
            self.draw_text_simple(frame, x_offset=x_offset, y_offset=y_offset)

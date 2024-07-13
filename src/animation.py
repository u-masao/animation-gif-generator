"""
このモジュールは指定の文字列を描画した画像を作成します。
Streamlit で動作します。
"""

from typing import Tuple

import imageio
from PIL import Image


class Animation:
    """
    このクラスはアニメーションを管理します。
    複数のフレームを初期化して保持します。
    GIF 形式などのファイルに出力するバイトストリームを作成します。
    """

    def __init__(
        self,
        frame_width: int = 128,
        frame_height: int = 128,
        frame_count: int = 1,
        color: Tuple[int] = (255, 255, 255, 0),
    ):
        """
        コンストラクタ
        フレーム数、フレームサイズ、色を指定して、各 frame を初期化します
        """

        # 入力バリデーション
        if not isinstance(frame_count, int):
            raise ValueError("frame_count を int 型にしてください")
        if frame_count < 1:
            raise ValueError("frame_count を 1 以上にしてください")

        # 変数初期化
        self.frames = []
        self.frame_count = 0
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.color = color
        self.drawers = []

        # make frames
        for _ in range(frame_count):
            self.add_frame()

    def _update_frame_count(self):
        """
        frame_count 変数を更新
        """
        self.frame_count = len(self.frames)

    def add_frame(self):
        """
        フレームを追加
        """
        self.frames.append(
            Image.new(
                "RGBA", (self.frame_width, self.frame_height), color=self.color
            )
        )
        self._update_frame_count()

    def add_drawer(self, drawer):
        self.drawers.append(drawer)
        return self

    def add_drawers(self, drawers):
        for drawer in drawers:
            self.add_drawer(drawer)
        return self

    def render(self, format: str = "GIF", duration: int = 1000, loop: int = 0):
        """
        レンダリングして画像データを出力
        """
        for drawer in self.drawers:
            drawer.draw(self)

        return imageio.mimsave(
            imageio.RETURN_BYTES,
            self.frames,
            format="GIF",
            duration=duration,
            loop=loop,
        )


def main():

    from src.drawer import FillDrawer, RandomParticleDrawer, TextDrawer

    text = "いい\n天気"
    frame_count = 5
    animation = Animation(frame_count=frame_count)
    animation.add_drawers(
        [
            FillDrawer(),
            RandomParticleDrawer(),
            TextDrawer(text, enable_fit_text_to_frame=True),
        ]
    )
    open("test_outputs/demo.gif", "wb").write(animation.render())


if __name__ == "__main__":
    main()

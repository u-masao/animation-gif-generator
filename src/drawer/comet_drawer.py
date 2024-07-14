"""
このモジュールは彗星を描画する Drawer です
"""

import numpy as np
from PIL import ImageDraw

from src.animation import Animation
from src.drawer.drawer import Drawer


class CometDrawer(Drawer):
    """
    彗星を描画する。
    """

    def __init__(
        self,
    ):
        """
        コンストラクタ
        """
        super().__init__()

    def draw(self, animation: Animation) -> None:
        """
        ランダムな場所にランダムなサイズの粒子を表示する
        """

        # フレームごとに処理
        for frame_index, frame in enumerate(animation.frames):

            # フレームから ImageDraw を取得
            draw = ImageDraw.Draw(frame)
            point = np.random.randn(1)
            draw.circle(
                (frame.width / 2, frame.height / 2),
                np.abs(point[0]) * 20,
                fill=(128, 128, 128, 255),
            )

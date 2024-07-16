"""
このモジュールは指定の文字列を描画した画像を作成します。
"""

from abc import ABC, abstractmethod
from typing import Tuple

from PIL import ImageDraw

from src import Animation


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

"""
このモジュールは彗星を描画する Drawer です


- 彗星は核を持つ(nucleus)
  - 核は初期位置、速度、を持ち、等速運動する
- 核はコマを持つ
  - コマは核の周囲を明るくし、核と共に移動する(描画のみで対応)
- 彗星は粒子を放出する(Particle)
  - 粒子は初期位置、速度、加速度、明るさ、明るさの減衰率を持つ
  - 粒子は核から確率的に生成される
  - 粒子は核の進行方向の逆向きに進む
"""

from typing import List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw

from src.animation import Animation
from src.drawer.drawer import Drawer


class DrawableParticle:
    def __init__(
        self,
        size: float = 3.0,
        position: List[float] = [0.0, 0.0],
        velocity: List[float] = [0.1, 0.1],
        acceralation: List[float] = [0.0, 0.0],
        brightness: float = 1.0,
        brightness_change_ratio: float = 0.95,
        color: Tuple[int] = (255, 255, 255, 255),
        bg_color: Tuple[int] = (32, 32, 32, 255),
        angle: Optional[float] = None,
        angular_velocity: Optional[float] = None,
        star_tip_count: int = 4,
        shape: str = "star",
    ):
        self.size = size
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.acceralation = np.array(acceralation)
        self.brightness = brightness
        self.brightness_change_ratio = brightness_change_ratio
        self.color = color
        self.bg_color = bg_color
        self.angle = (
            2.0 * np.pi * np.random.randn(1) if angle is None else angle
        )
        self.angular_velocity = (
            2.0 * np.pi * np.random.randn(1)
            if angular_velocity is None
            else angular_velocity
        )
        self.star_tip_count = star_tip_count
        self.shape = shape

    def update(self, delta_time: float):
        self.velocity += self.acceralation * delta_time
        self.position += self.velocity * delta_time
        self.angle += self.angular_velocity * delta_time
        self.brightness *= self.brightness_change_ratio

    def calc_position_in_frame(self, frame: Image):
        return self.position[0:2] * np.array([frame.width, frame.height])

    @staticmethod
    def make_star_polygon(
        center_x: int,
        center_y: int,
        tip_count: int = 5,
        radius: float = 30.0,
        angle: float = np.pi / 2.0,
        inside_corner_ratio: float = 0.4,
    ):

        points = []

        for i in range(tip_count * 2):
            r = radius if i % 2 == 0 else radius * inside_corner_ratio
            x = center_x + r * np.cos(angle)
            y = center_y + r * np.sin(angle)
            points.append((x, y))
            angle += np.pi / tip_count

        return points

    def calc_draw_color(self):
        fg_color = np.array(self.color)
        bg_color = np.array(self.bg_color)

        draw_color = (fg_color - bg_color) * self.brightness + bg_color
        draw_color = [int(x) for x in draw_color]
        draw_color[3] = 255

        return tuple(draw_color)

    def draw_particle(
        self,
        frame: Image,
    ):
        draw = ImageDraw.Draw(frame)
        position_in_frame = self.calc_position_in_frame(frame)
        color = self.calc_draw_color()

        if self.shape == "star":
            # 星型のポリゴンを計算
            polygon_data = DrawableParticle.make_star_polygon(
                center_x=position_in_frame[0],
                center_y=position_in_frame[1],
                tip_count=self.star_tip_count,
                radius=self.size,
                angle=self.angle,
            )

            # ポリゴンを描画
            draw.polygon(polygon_data, fill=color, outline=color)

        elif self.shape == "circle":
            # 円を描画
            draw.circle(
                position_in_frame,
                self.size,
                fill=color,
            )
        else:
            ValueError(f"その shape はサポートしていません。: {self.shape}")


class CometDust(DrawableParticle):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    def draw(self, frame: Image):
        super().draw_particle(frame)


class Nucleus(DrawableParticle):
    def __init__(
        self,
        size: float = 10.0,
        position: List[float] = [0.0, 0.5],
        velocity: List[float] = [0.1, 0.0],
        dust_genarate_prob: float = 10.0,
        star_tip_count: int = 5,
        brightness_change_ratio: float = 1.0,
        *args,
        **kwargs,
    ):
        super().__init__(
            size=size,
            position=position,
            velocity=velocity,
            star_tip_count=star_tip_count,
            brightness_change_ratio=brightness_change_ratio,
            *args,
            **kwargs,
        )
        self.dust_genarate_prob = dust_genarate_prob

    def update(self, delta_time: float) -> List[CometDust]:
        """
        更新メソッド。時間を進めて塵を生成する。
        """
        pre_position = self.position.copy()
        super().update(delta_time)

        # ポワソン分布に基づいた乱数で作成する塵の数を決める
        dust_count = int(
            np.random.poisson(self.dust_genarate_prob * delta_time, 1)
        )

        # 塵を生成する
        comet_dusts = []
        for _ in range(dust_count):
            comet_dusts.append(self.make_comet_dust(pre_position))

        # 塵を返す
        return comet_dusts

    def make_comet_dust(self, pre_position: np.ndarray):
        """
        塵を作成する
        """

        # 初期位置を移動軌跡上で一様なランダムで生成
        dust_position = (self.position - pre_position) * np.random.rand(
            1
        ) + pre_position

        # 速度の方向を生成
        dust_velocity_theta = 2.0 * np.pi * np.random.randn(1)

        # 速度(スカラー)を生成
        dust_velocity_scalar = np.random.randn(1) * 0.02

        # 2次元の速度ベクトルを生成
        dust_velocity = (
            np.array(
                [np.sin(dust_velocity_theta), np.cos(dust_velocity_theta)]
            ).flatten()
            * dust_velocity_scalar  # noqa: W503
        )

        # CometDust インスタンスを返す
        return CometDust(position=dust_position, velocity=dust_velocity)

    def draw(self, frame: Image):
        super().draw_particle(frame)


class CometDrawer(Drawer):
    """
    彗星を描画する。
    """

    def __init__(
        self,
        delta_time: float = 1.0,
    ):
        """
        コンストラクタ
        """
        super().__init__()
        self.nucleus = Nucleus()
        self.dusts = []
        self.delta_time = delta_time

    def draw(self, animation: Animation) -> None:
        """
        ランダムな場所にランダムなサイズの粒子を表示する
        """

        # フレームごとに処理
        for frame_index, frame in enumerate(animation.frames):

            # CometDust を描画して更新
            for dust in self.dusts:
                dust.draw(frame)
                dust.update(self.delta_time)

            # Nucleus を描画
            self.nucleus.draw(frame)

            # Nucleus を更新して新しい CometDust を追加
            self.dusts += self.nucleus.update(self.delta_time)

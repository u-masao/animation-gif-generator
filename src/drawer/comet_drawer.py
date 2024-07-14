"""
このモジュールは彗星を描画する Drawer です


- 彗星は核を持つ(nucleus)
  - 核は初期位置、速度、を持ち、等速運動する
- 彗星はコマを持つ(coma)
  - コマは核の周囲を明るくし、核と共に移動する(描画のみで対応)
- 彗星は粒子を放出する(Particle)
  - 粒子は初期位置、速度、加速度、明るさ、明るさの減衰率を持つ
  - 粒子は核から確率的に生成される
  - 粒子は核の進行方向の逆向きに進む
"""

from dataclasses import dataclass
from typing import List

import numpy as np
from PIL import Image, ImageDraw

from src.animation import Animation
from src.drawer.drawer import Drawer


@dataclass
class CometDust:
    size: float = 5.0
    position: np.ndarray = np.array([0.0, 0.0])
    velocity: np.ndarray = np.array([0.1, 0.1])
    acceralation: np.ndarray = np.array([0.0, 0.0])
    brightness: float = 1.0
    brightness_change_ratio: float = 1.0

    def update(self, dt):
        self.velocity += self.acceralation * dt
        self.position += self.velocity * dt
        self.brightness *= self.brightness_change_ratio

    def draw(self, image: Image):
        draw = ImageDraw.Draw(image)
        x, y = self.position
        color = tuple([int(self.brightness * 255)] * 3 + [255])
        draw.ellipse(
            (
                x * image.width - self.size / 2,
                y * image.height - self.size / 2,
                x * image.width + self.size / 2,
                y * image.height + self.size / 2,
            ),
            fill=color,
        )


@dataclass
class Nucleus:
    size: float = 10.0
    position: np.ndarray = np.array([0.0, 0.5])
    velocity: np.ndarray = np.array([0.1, 0.0])
    acceralation: np.ndarray = np.array([0.0, 0.0])
    brightness: float = 1.0
    brightness_change_ratio: float = 1.0
    dust_lambda: float = 5.0

    def update(self, dt) -> List[CometDust]:
        pre_position = self.position.copy()
        self.velocity += self.acceralation * dt
        self.position += self.velocity * dt
        self.brightness *= self.brightness_change_ratio

        # make comet dust
        dust_count = int(np.random.poisson(self.dust_lambda * dt, 1))
        comet_dusts = []
        for _ in range(dust_count):
            comet_dusts.append(self.make_comet_dust(pre_position))

        return comet_dusts

    def make_comet_dust(self, pre_position):
        dust_velocity_theta = 2 * np.pi * np.random.randn(1)
        dust_velocity_scalar = np.random.randn(1) * 0.1
        dust_velocity = (
            np.array(
                [np.sin(dust_velocity_theta), np.cos(dust_velocity_theta)]
            ).flatten()
            * dust_velocity_scalar  # noqa: W503
        )

        dust_position = (self.position - pre_position) * np.random.rand(
            1
        ) + pre_position
        return CometDust(position=dust_position, velocity=dust_velocity)

    def draw(self, image: Image):
        draw = ImageDraw.Draw(image)
        x, y = self.position
        color = tuple([int(self.brightness * 255)] * 3 + [255])
        draw.ellipse(
            (
                x * image.width - self.size / 2,
                y * image.height - self.size / 2,
                x * image.width + self.size / 2,
                y * image.height + self.size / 2,
            ),
            fill=color,
        )


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
        self.nucleus = Nucleus()
        self.dusts = []

    def draw(self, animation: Animation) -> None:
        """
        ランダムな場所にランダムなサイズの粒子を表示する
        """

        dt = 1.0

        # フレームごとに処理
        for frame_index, frame in enumerate(animation.frames):
            # フレームから ImageDraw を取得
            for dust in self.dusts:
                print("dust: ", dust)
                dust.draw(frame)
                dust.update(dt)
            self.nucleus.draw(frame)
            new_dusts = self.nucleus.update(dt)
            self.dusts += new_dusts

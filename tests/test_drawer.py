from pathlib import Path

import pytest

from src import (
    Animation,
    CircleMoveTextDrawer,
    CometDrawer,
    Drawer,
    FillDrawer,
    ParticleDrawer,
    RandomParticleDrawer,
    TextDrawer,
)

test_output_dir = Path("test_outputs")


@pytest.fixture(scope="session", autouse=True)
def make_output_dir():
    test_output_dir.mkdir(parents=True, exist_ok=True)


# Drawer 抽象クラスのテスト（抽象メソッド呼び出しでエラーが発生することを確認）
def test_abstract_drawer():
    with pytest.raises(TypeError):
        drawer = Drawer()
        print(drawer)


# FillDrawer のテスト
def test_fill_drawer():
    # テスト用データ
    color = (255, 0, 0)  # 赤色
    color_alpha = color + (255,)  # アルファ値を追加

    # モックアニメーションの作成
    animation = Animation(frame_count=5)

    # FillDrawer のインスタンス化と描画
    drawer = FillDrawer(color)
    drawer.draw(animation)

    # 結果の検証
    for frame_index, frame in enumerate(animation.frames):
        # 左上隅の色を確認
        assert frame.getpixel((0, 0)) == color_alpha
        # 右下隅の色を確認
        assert (
            frame.getpixel((frame.width - 1, frame.height - 1)) == color_alpha
        )

    # 描画されたフレームを保存して目視確認する例（必要に応じて）
    open(test_output_dir / "test_drawer_fill_red.gif", "wb").write(
        animation.render()
    )


# RandomParticleDrawer のテスト
def test_random_particle_drawer():
    # テスト用データ
    particle_count = 4
    max_particle_size = 20
    frame_count = 20
    bg_color = (32, 32, 32)

    # アニメーションの作成
    animation = Animation(frame_count=frame_count)
    FillDrawer(bg_color).draw(animation)

    # RandomParticleDrawer のインスタンス化と描画
    drawer = RandomParticleDrawer(
        particle_count=particle_count,
        max_particle_size=max_particle_size,
    )

    # 粒子を描画
    drawer.draw(animation)

    # 描画されたフレームを保存して目視確認する例（必要に応じて）
    open(
        test_output_dir / "test_drawer_random_particle_4frame.gif", "wb"
    ).write(animation.render())


def test_drawer_text():

    # 条件設定
    text = "テスト\nテキスト"
    font_path = "fonts/IPAfont00303/ipag.ttf"
    bg_color = (32, 32, 32)

    # アニメーション作成
    animation = Animation()

    # 背景描画
    FillDrawer(bg_color).draw(animation)

    # テキスト描画
    TextDrawer(text, font_path=font_path).draw(animation)

    # Assertions
    open(test_output_dir / "test_drawer_text.gif", "wb").write(
        animation.render()
    )


def test_drawer_circle_move_text():

    # 条件設定
    text = "テスト\nテキスト"
    font_path = "fonts/IPAfont00303/ipag.ttf"
    bg_color = (32, 32, 32)

    # アニメーション作成
    animation = Animation(frame_count=10)

    # 背景描画
    FillDrawer(bg_color).draw(animation)

    # テキスト描画
    CircleMoveTextDrawer(text, radius=10, font_path=font_path).draw(animation)

    # Assertions
    open(test_output_dir / "test_drawer_circle_move_text.gif", "wb").write(
        animation.render(duration=100)
    )


def test_particle_drawer():

    # アニメーション作成
    animation = Animation(frame_count=36)

    # 背景描画
    FillDrawer().draw(animation)

    # 星を描画
    ParticleDrawer().draw(animation)

    # Assertions
    open(test_output_dir / "test_particle_drawer_default.gif", "wb").write(
        animation.render(duration=50)
    )


def test_particle_drawer_circle():

    # 変数を設定
    font_path = "fonts/IPAfont00303/ipag.ttf"

    # アニメーション作成
    animation = Animation(frame_count=10)

    # 背景描画
    FillDrawer().draw(animation)

    # 円を描画
    ParticleDrawer(shape="circle").draw(animation)

    # テキスト描画
    CircleMoveTextDrawer(
        "あざ\nます",
        radius=10,
        enable_fit_text_to_frame=True,
        font_color=(255, 0, 0, 255),
        font_path=font_path,
    ).draw(animation)

    # Assertions
    open(test_output_dir / "test_particle_drawer_circle.gif", "wb").write(
        animation.render(duration=100)
    )


def test_comet_drawer():

    # アニメーション作成
    animation = Animation(frame_count=20)

    # 背景描画
    FillDrawer().draw(animation)

    # 円を描画
    CometDrawer().draw(animation)

    # Assertions
    open(test_output_dir / "test_comet_drawer.gif", "wb").write(
        animation.render(duration=200)
    )

from pathlib import Path

import pytest
from PIL import ImageDraw, ImageFont

from animation import Animation

test_output_dir = Path("test_outputs")


@pytest.fixture(scope="session", autouse=True)
def make_output_dir():
    test_output_dir.mkdir(parents=True, exist_ok=True)


def test_animation_init():
    # 正常系のテスト
    animation = Animation(frame_count=5)
    assert len(animation.frames) == 5
    assert animation.frame_width == 128
    assert animation.frame_height == 128

    # 異常系のテスト
    with pytest.raises(ValueError):
        Animation(frame_count="invalid")  # frame_count が int 型でない
    with pytest.raises(ValueError):
        Animation(frame_count=0)  # frame_count が 1 未満


def test_add_frame():
    animation = Animation(frame_count=2)
    animation.add_frame()
    assert len(animation.frames) == 3


def test_render():
    animation = Animation(frame_count=3)
    gif_bytes = animation.render()
    assert isinstance(gif_bytes, bytes)
    assert len(gif_bytes) > 0


# 追加のテスト: 各フレームに文字列が描画されることの確認
def test_frame_content():
    text = "Test Text"
    animation = Animation(frame_count=1)
    frame = animation.frames[0]

    draw = ImageDraw.Draw(frame)
    font = ImageFont.load_default()
    _, _, text_width, text_height = font.getbbox(text)

    draw.text(
        ((frame.width - text_width) / 2, (frame.height - text_height) / 2),
        text,
        font=font,
        fill=(0, 0, 0),  # 黒で塗りつぶし
    )

    # 描画されたフレームを保存して目視確認する例（必要に応じて）
    frame.save(test_output_dir / "test_frame.gif")


# 追加のテスト: アニメーション
def test_animation():
    text = "Test Text"
    animation = Animation(frame_count=4)
    for frame_index, frame in enumerate(animation.frames):

        draw = ImageDraw.Draw(frame)
        font = ImageFont.load_default()
        _, _, text_width, text_height = font.getbbox(text)

        draw.text(
            (
                frame_index * 10 + (frame.width - text_width) / 2,
                frame_index * 10 + (frame.height - text_height) / 2,
            ),
            text,
            font=font,
            fill=(0, frame_index * 64, 0),  # 黒で塗りつぶし
        )

    # 描画されたフレームを保存して目視確認する例（必要に応じて）
    open(test_output_dir / "test_animation.gif", "wb").write(
        animation.render()
    )

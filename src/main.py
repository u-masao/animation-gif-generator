import math

import imageio
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# import random


def draw_text_with_wobble(
    text: str,
    wobble_amplitude: float,
    frame_index: int,
    total_frames: int,
    font_size: int = 10,
    bg_color: str = "gray",
    font_color: str = "green",
    image_size: int = 128,
    stroke_width: int = 1,
    font_path: str = "fonts/IPAfont00303/ipag.ttf",
):
    img = Image.new("RGBA", (image_size, image_size), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, img.width, img.height), fill=bg_color)

    # 振動効果の計算 (文字が画像からはみ出ないように調整)
    # x_offset = min(random.gauss(mu=0.0, sigma=wobble_amplitude), img.width)
    # y_offset = min(random.gauss(mu=0.0, sigma=wobble_amplitude), img.height)
    x_offset = wobble_amplitude * math.sin(
        math.pi * 2 * frame_index / total_frames
    )
    y_offset = wobble_amplitude * math.cos(
        math.pi * 2 * frame_index / total_frames
    )

    # font_size = 100
    font = ImageFont.truetype(font_path, font_size)
    left, top, right, bottom = font.getbbox(text, stroke_width=stroke_width)
    text_width = right - left
    text_height = bottom - top
    # ratio = max(text_width / img.width, text_height/ img.height)

    ratio = 1
    st.sidebar.write((ratio, text_width, text_height))
    # st.sidebar.write(font.getmetrics())
    font_size /= ratio

    font = ImageFont.truetype(font_path, font_size)
    left, top, right, bottom = font.getbbox(text)
    text_width = right - left
    text_height = bottom - top

    x = (img.width) / 2 + x_offset
    y = (img.height) / 2 + y_offset

    draw.text(
        (x, y),
        text.replace("\\n", "\n"),
        font=font,
        fill=font_color,
        anchor="mm",
        stroke_width=stroke_width,
    )
    return img


def main():

    st.title("文字 GIF メーカー")
    text_input = st.text_input(
        "文字列を入力してください:", value="もはや\\nこれまで"
    )
    font_size = st.slider(
        "フォントサイズ:",
        min_value=20,
        max_value=200,
        value=50,
    )
    stroke_width = st.slider("線の太さ:", min_value=0, max_value=10, value=1)
    fps = st.slider("fps:", min_value=5, max_value=10, value=1)
    total_frames = st.slider(
        "total_frams:", min_value=1, max_value=20, value=1
    )
    wobble_amplitude = st.slider(
        "振動の大きさ:", min_value=0, max_value=50, value=3
    )
    bg_color = st.color_picker("background", "#888")
    font_color = st.color_picker("font", "#00FF00")

    # GIF生成
    frames = []
    for frame_index in range(total_frames):
        frame = draw_text_with_wobble(
            text_input,
            wobble_amplitude,
            frame_index,
            total_frames,
            font_size=font_size,
            bg_color=bg_color,
            font_color=font_color,
            stroke_width=stroke_width,
        )
        frames.append(frame)

    # GIF表示
    gif_bytes = imageio.mimsave(
        imageio.RETURN_BYTES, frames, format="GIF", fps=fps, loop=0
    )
    st.sidebar.image(gif_bytes, width=32)
    st.sidebar.image(gif_bytes)


if __name__ == "__main__":
    main()

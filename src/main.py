"""
このモジュールは指定の文字列を描画した画像を作成します。
Streamlit で動作します。
"""

import sys
from pathlib import Path

import streamlit as st

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src import (
    Animation,
    CircleMoveTextDrawer,
    CometDrawer,
    FillDrawer,
    ParticleDrawer,
    RandomParticleDrawer,
)


def create_main_panel(main_panel, gif_bytes, text_input):
    """
    メインパネルの中身を配置
    """

    # GIF データ表示
    main_panel.image(gif_bytes)

    # ダウンロード
    download_filename = text_input.replace("\n", "") + ".gif"
    main_panel.download_button(
        "画像をダウンロード", gif_bytes, file_name=download_filename
    )


def create_control_panel(control_panel):
    """
    コントロールパネルの中身を配置
    """
    text_input = control_panel.text_area(
        "画像に入れたい文字:", value="あざ\nます"
    ).strip()

    with control_panel.container(border=True):
        draw_comet = st.checkbox("彗星を表示する", value=True)

    with control_panel.container(border=True):
        cols = st.columns(2)
        font_color = cols[0].color_picker("文字の色", "#E204F7")
        bg_transparent = st.checkbox("背景を透明にする", value=False)
        bg_color = cols[1].color_picker(
            "背景の色", "#111111", disabled=bg_transparent
        )
        if bg_transparent:
            bg_color = "#00000000"

    with control_panel.container(border=True):
        cols = st.columns(3)
        if st.checkbox("文字を画像にフィットさせる", value=True):
            font_size_auto = True
        else:
            font_size_auto = False

        font_size = cols[0].slider(
            "フォントのサイズ:",
            min_value=10,
            max_value=300,
            value=70,
            disabled=font_size_auto,
        )
        stroke_width = cols[1].slider(
            "線の太さ:", min_value=0, max_value=4, value=1
        )
        spacing = cols[2].slider("行間幅:", min_value=0, max_value=10, value=4)

    with control_panel.container(border=True):
        cols = st.columns(3)
        radius = cols[0].slider(
            "移動半径:", min_value=0, max_value=64, value=8, step=4
        )
        fps = cols[1].slider(
            "フレームレート:", min_value=1, max_value=10, value=5
        )
        frame_count = cols[2].slider(
            "トータルフレーム数:", min_value=1, max_value=50, value=10
        )

    with control_panel.container(border=True):
        draw_particle = st.checkbox("パーティクルを表示する", value=False)

    return (
        text_input,
        font_color,
        bg_color,
        bg_transparent,
        font_size_auto,
        font_size,
        stroke_width,
        spacing,
        radius,
        fps,
        frame_count,
        draw_particle,
        draw_comet,
    )


def main():

    # タイトルを描画
    st.title("文字 GIF メーカー")

    # 分割
    main_panel, control_panel = st.columns([0.3, 0.7])

    # メインパネルを描画
    (
        text_input,
        font_color,
        bg_color,
        bg_transparent,
        font_size_auto,
        font_size,
        stroke_width,
        spacing,
        radius,
        fps,
        frame_count,
        draw_particle,
        draw_comet,
    ) = create_control_panel(control_panel)

    # Drawer を初期化
    drawers = []

    # 背景を描画
    drawers.append(FillDrawer(color=bg_color))

    # ランダム粒子を描画
    if draw_comet:
        drawers.append(CometDrawer())

    # ランダム粒子を描画
    if draw_particle:
        drawers.append(
            RandomParticleDrawer(max_particle_size=5, particle_count=20)
        )
        drawers.append(ParticleDrawer())

    # 移動する文字列を描画
    drawers.append(
        CircleMoveTextDrawer(
            text_input,
            enable_fit_text_to_frame=font_size_auto,
            radius=radius,
            font_color=font_color,
            font_size=font_size,
            stroke_width=stroke_width,
            spacing=spacing,
        )
    )

    # コマの更新間隔を設定
    duration_ms = 1000.0 / fps

    # Animation インスタンスを初期化
    animation = Animation(frame_count=frame_count)

    # drawer を追加
    animation.add_drawers(drawers)

    # レンダリング
    gif_bytes = animation.render(duration=duration_ms)

    # 画面出力
    create_main_panel(main_panel, gif_bytes, text_input)


if __name__ == "__main__":
    main()

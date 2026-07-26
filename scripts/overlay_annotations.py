#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
姜老师配图 · 中文批注叠字脚本
================================

为什么需要它：
    文生图模型（扩散模型）画中文文字天生不可靠，手写体尤易出假字/错字。
    本脚本把"生图"和"写字"拆成两步——生图阶段画面禁止出现任何文字，
    生图完成后用本脚本把批注确定性地叠加到图上。文字由你提供、像素级精确，
    100% 不会错字，且字体采用系统楷体（手写风）。

用法：
    python overlay_annotations.py \
        --image  input.png \
        --out    output.png \
        --annotations annotations.json \
        [--font "C:\\Windows\\Fonts\\simkai.ttf"] \
        [--default-size 54]

annotations.json 是一个数组，每项描述一个批注：
    [
      {
        "text": "一条直线",          # 批注文字（必填）
        "color": "red",             # red | orange | blue | black（默认 red）
        "x": 0.30,                  # 文字中心横坐标，归一化 0~1
        "y": 0.40,                  # 文字中心纵坐标，归一化 0~1
        "size": 54,                 # 字号（基于 1920 宽参考，自动按图宽缩放）
        "rotate": -6,               # 旋转角度（度），模拟手写抖动，默认 0
        "circle": true,             # 在文字外围画手写圈注，默认 false
        "underline": true,          # 文字下方画手写下划线，默认 false
        "arrow_from": [0.20, 0.55], # 画一条指向文字的箭头（归一化起点），可选
        "arrow_to":   [0.28, 0.42]  # 箭头终点（一般指向文字中心，可省略则用 x,y）
      }
    ]

也可以直接把 JSON 字符串传给 --annotations（用引号包住）。
坐标全部归一化，换分辨率也不怕。
"""

import argparse
import json
import sys
from PIL import Image, ImageDraw, ImageFont

# 姜老师配色纪律（与 style-dna.md 一致）
COLOR_MAP = {
    "red": (229, 72, 77),      # E5484D 强调
    "orange": (245, 158, 11),  # F59E0B 提示
    "blue": (37, 99, 235),     # 2563EB 信息
    "black": (26, 26, 26),     # 1A1A1A 主线条
}

DEFAULT_FONT = r"C:\Windows\Fonts\simkai.ttf"
REFERENCE_WIDTH = 1920  # 字号以此为参考宽度，按实际图宽缩放


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        # 找不到指定字体时退回默认位图字体（仅兜底，中文会显示为方框）
        return ImageFont.load_default()


def draw_rotated_text(img, text, center, font, fill, angle=0):
    """把一段文字渲染到独立透明图层，按需旋转，再以 center 为锚点贴回主图。"""
    mask = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(mask)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    layer = Image.new("RGBA", (tw + 40, th + 40), (0, 0, 0, 0))
    td = ImageDraw.Draw(layer)
    td.text((20 - bbox[0], 20 - bbox[1]), text, font=font, fill=fill)

    if angle:
        layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)

    cx, cy = center
    px = int(cx - layer.width / 2)
    py = int(cy - layer.height / 2)
    img.alpha_composite(layer, (px, py))


def draw_hand_circle(draw, center, half_w, half_h, fill):
    """用两段弧拼一个略有手绘感的圈注。"""
    x0, y0 = center[0] - half_w, center[1] - half_h
    x1, y1 = center[0] + half_w, center[1] + half_h
    draw.arc([x0, y0, x1, y1], start=10, end=200, fill=fill, width=3)
    draw.arc([x0, y0, x1, y1], start=200, end=370, fill=fill, width=3)


def draw_arrow(draw, p_from, p_to, fill):
    """画一条带箭头的手绘线。"""
    draw.line([p_from, p_to], fill=fill, width=3, joint="curve")
    import math
    dx, dy = p_to[0] - p_from[0], p_to[1] - p_from[1]
    ang = math.atan2(dy, dx)
    ah = 14  # 箭头长度
    left = (p_to[0] - ah * math.cos(ang - 0.4), p_to[1] - ah * math.sin(ang - 0.4))
    right = (p_to[0] - ah * math.cos(ang + 0.4), p_to[1] - ah * math.sin(ang + 0.4))
    draw.line([left, p_to], fill=fill, width=3)
    draw.line([right, p_to], fill=fill, width=3)


def main():
    ap = argparse.ArgumentParser(description="姜老师配图中文批注叠字脚本")
    ap.add_argument("--image", required=True, help="生图结果（无文字的干净画面）")
    ap.add_argument("--out", required=True, help="输出路径")
    ap.add_argument("--annotations", required=True, help="JSON 文件或 JSON 字符串")
    ap.add_argument("--font", default=DEFAULT_FONT, help="中文字体路径（默认 Windows 楷体）")
    ap.add_argument("--default-size", type=int, default=54, help="默认字号（基于 1920 宽）")
    args = ap.parse_args()

    # 解析批注：优先当文件读，失败则当内联 JSON 字符串
    try:
        with open(args.annotations, encoding="utf-8") as f:
            anns = json.load(f)
    except (OSError, json.JSONDecodeError):
        anns = json.loads(args.annotations)

    if not isinstance(anns, list):
        anns = [anns]

    img = Image.open(args.image).convert("RGBA")
    W, H = img.size
    scale = W / REFERENCE_WIDTH
    draw = ImageDraw.Draw(img)

    for a in anns:
        text = a.get("text", "")
        if not text:
            continue
        color_name = a.get("color", "red")
        fill = COLOR_MAP.get(color_name, COLOR_MAP["red"])

        cx = a.get("x", 0.5) * W
        cy = a.get("y", 0.5) * H
        size = int(a.get("size", args.default_size) * scale)
        angle = a.get("rotate", 0)

        # 可选：先画箭头（指向文字）
        arrow_from = a.get("arrow_from")
        arrow_to = a.get("arrow_to") or [cx / W, cy / H]
        if arrow_from:
            draw_arrow(
                draw,
                (arrow_from[0] * W, arrow_from[1] * H),
                (arrow_to[0] * W, arrow_to[1] * H),
                fill,
            )

        # 画文字
        font = load_font(args.font, size)
        draw_rotated_text(img, text, (cx, cy), font, fill, angle)

        # 可选：圈注（文字外围画手绘圈）
        if a.get("circle"):
            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            half_w = (tw / 2) * scale * 1.15 + 16
            half_h = (th / 2) * scale * 1.15 + 14
            draw_hand_circle(draw, (cx, cy), half_w, half_h, fill)

        # 可选：下划线
        if a.get("underline"):
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            y_base = cy + (bbox[3] - bbox[1]) / 2 * 0.9
            draw.line(
                [(cx - tw / 2, y_base), (cx + tw / 2, y_base)],
                fill=fill,
                width=3,
            )

    out = img.convert("RGB")
    out.save(args.out)
    print(f"OK: 已叠加 {len(anns)} 条批注 -> {args.out}")


if __name__ == "__main__":
    main()

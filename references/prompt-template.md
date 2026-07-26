# 单张生图提示词模板

## 使用规则

- **角色外形用英文写清楚**（稳定视觉），**中文批注不在图内生成**——生图阶段画面禁止出现任何文字/标签/批注，中文由 `scripts/overlay_annotations.py` 在生图后确定性叠加。
- 每次生图都从当前文章重新构思隐喻，不照抄案例。
- 比例固定 16:9 横版。

## 模板骨架

```
16:9 horizontal Chinese article illustration, pure white background, clean hand-drawn black line art with slight sketch wobble, lots of white space, NO borders, NO grid.

[ROLE — 固定英文描述（姜老师）]
Jiang Laoshi is a handsome Chinese male swimming coach and professional swimming-technique demonstration model. He has an athletic, well-built swimmer's physique — broad shoulders, defined arms, strong core — and a calm, confident, approachable expression. He wears a **white silicone swim cap with Chinese text "四季飞浪游泳培训" printed on it**, **black swimming goggles**, and **dark (navy/black) swim trunks**. He demonstrates swimming techniques with precise, textbook form, like an experienced coach giving a lesson.
（默认姜老师；若用户要求女性 IP，把本段整体替换为 xiaolan-ip.md 第八章丽丽的英文描述——**黄帽/黑镜/浅蓝衣**，识别点见 style-dna 配色表）

[ACTION — 本次具体动作，来自 xiaolan-ip.md 动作库]
Jiang Laoshi is <doing a specific swimming technique / training demonstration>, shown mid-motion with clear, precise form, as the central subject actively performing the action (not standing decoration).

[SCENE — 极简场景]
Minimal pool-edge or lane context suggested by a few light line hints; water ripples minimal.

[ANNOTATION — 禁止图内文字]
NO text, NO labels, NO handwritten annotations, NO Chinese characters in the image. All Chinese annotations will be added post-generation via overlay script.

[STYLE LOCK — 风格锁]
Hand-drawn instructional illustration like a swim coach's explainer sketch. Black line art only for the body, blue cap, black goggles, dark trunks. No PPT charts, no commercial illustration shading, no gradients, no cute cartoon, no title text in corner, NO text of any kind in image.
```

## 填写示例（ACTION 写进 prompt；批注词交给叠字脚本，不写进 prompt）

主题：讲"专注力就是减少多余动作"
- ACTION: Jiang Laoshi performs a tight streamline glide, arms pressed overhead, body in one straight line, eyes forward through goggles.
- 批注词（写入 annotations.json）：红"一条直线"、蓝"多余动作=阻力"

主题：讲"反馈闭环"
- ACTION: Jiang Laoshi demonstrates a stroke while a trainee mirrors him; a stopwatch/scoreboard sits beside, Jiang Laoshi points to it.
- 批注词（写入 annotations.json）：橙"示范"、蓝"看表反馈"、红"再调整"

## 常见替换词（ACTION 用）

- 自由泳高肘划水：high-elbow freestyle pull, arm entering with high elbow
- 蛙泳蹬腿：breaststroke kick, snap-and-glide
- 流线型：tight streamline glide, arms overhead
- 出发跳水：track-start dive off the block, coiled and ready
- 翻滚转身：flip turn at the wall, tucked
- 换气：side breathing, head turned to inhale
- 打腿：flutter kick with kickboard, whipping motion

## 禁忌提示（写进每条 prompt 末尾）

NO PPT, NO flowchart, NO commercial shading, NO gradient, NO cute chibi, NO corner title, NO black silhouette, NO female/child version, pure white background only.

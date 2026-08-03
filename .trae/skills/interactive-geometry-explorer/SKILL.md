# 交互式动态几何 Skill

## 适用场景

当用户需要"拖动探索"几何关系时使用：拖动顶点观察面积/周长/角度变化、割补变换演示、公式验证、跑道动态计算等。

与静态画图 Skill（primary-geometry-diagram-solver）的区别：
- 静态画图：画固定图，给答案，适合解题。
- 交互式动态（本 Skill）：可拖动、实时测量、探索关系，适合理解和验证公式。

## 核心理念

1. **可拖动**：关键顶点可拖动，图形随拖动实时变化。
2. **实时测量**：长度、角度、面积、周长随拖动实时更新。
3. **公式验证**：公式中代入实时数值，让学生看到公式"活"起来。
4. **约束保持**：通过依赖点（derived points）保持图形性质（如长方形始终是长方形）。

## 交互式构造 JSON 规范

```json
{
  "title": "探索长方形面积",
  "description": "拖动顶点，观察面积和周长的变化",
  "grid": true,
  "snap": true,
  "snapSize": 0.5,
  "scale": 40,
  "origin": {"x": 0, "y": 0},
  "objects": [],
  "measurements": [],
  "formulas": [],
  "tips": "拖动 A 或 C，观察面积和周长如何变化"
}
```

## 对象类型

### point（点）
```json
{"type": "point", "id": "A", "x": 2, "y": 1, "label": "A", "free": true, "color": "#7c3aed"}
```
- `free: true` — 可拖动；`free: false` — 由 `depends` 函数计算位置。
- `depends` — 函数 `(scene) => [x, y]`，根据其他点计算本点坐标。

依赖点示例（长方形：B 和 D 由 A、C 推导）：
```json
{"type": "point", "id": "B", "free": false, "label": "B", "depends": "rectangle_BR"},
{"type": "point", "id": "D", "free": false, "label": "D", "depends": "rectangle_DL"}
```

### segment（线段）
```json
{"type": "segment", "p1": "A", "p2": "B", "label": "长", "color": "#1f2937", "width": 2.5, "dashed": false}
```

### circle（圆）
```json
{"type": "circle", "center": "O", "radiusPoint": "R", "fill": "rgba(124,58,237,0.08)", "color": "#1f2937", "width": 2.5}
```
- `radiusPoint` — 圆上一点，半径 = distance(center, radiusPoint)。

### polygon（多边形）
```json
{"type": "polygon", "points": ["A","B","C","D"], "fill": "rgba(124,58,237,0.10)", "color": "#1f2937", "width": 2.5}
```

### angle（角度弧）
```json
{"type": "angle", "p1": "A", "vertex": "B", "p2": "C", "label": "90°", "color": "#ea580c", "arcRadius": 20}
```

### text（文字标注）
```json
{"type": "text", "x": 5, "y": 3, "text": "高", "color": "#2563eb", "size": 14}
```

### height（高线，特殊类型）
```json
{"type": "height", "vertex": "C", "base1": "A", "base2": "B", "label": "高", "color": "#2563eb", "dashed": true}
```
- 自动计算从 vertex 到 base1-base2 所在直线的垂足，画虚线高。

### track（跑道，特殊类型）
```json
{"type": "track", "A": "A", "B": "B", "C": "C", "D": "D", "color": "#1f2937", "width": 2.8}
```
- 根据 4 个顶点画体育场形跑道（两条直道 + 两个半圆弧）。

## 测量类型

### length（长度）
```json
{"type": "length", "p1": "A", "p2": "B", "label": "长", "unit": "m"}
```

### angle（角度）
```json
{"type": "angle", "p1": "A", "vertex": "B", "p2": "C", "label": "∠ABC", "unit": "°"}
```

### area（面积）
```json
{"type": "area", "polygon": ["A","B","C","D"], "label": "面积", "unit": "m²"}
```
- 使用鞋带公式计算任意多边形面积。

### perimeter（周长）
```json
{"type": "perimeter", "polygon": ["A","B","C","D"], "label": "周长", "unit": "m"}
```

### radius（半径）
```json
{"type": "radius", "center": "O", "point": "R", "label": "半径", "unit": "m"}
```

### custom（自定义）
```json
{"type": "custom", "label": "一圈长度", "calc": "track_lap"}
```
- `calc` 指向预定义的计算函数名。

## 公式显示

公式使用函数动态计算，格式为 `label = expr`：

```json
{"label": "面积", "calc": "rect_area_formula"}
```

预定义公式函数：
- `rect_area_formula` — `长 × 宽 = {长} × {宽} = {面积}`
- `rect_perim_formula` — `(长 + 宽) × 2 = ({长} + {宽}) × 2 = {周长}`
- `tri_area_formula` — `底 × 高 ÷ 2 = {底} × {高} ÷ 2 = {面积}`
- `circle_area_formula` — `π × r² = 3.14 × {r}² = {面积}`
- `circle_circum_formula` — `2 × π × r = 2 × 3.14 × {r} = {周长}`
- `trap_area_formula` — `(上底 + 下底) × 高 ÷ 2 = ({上底} + {下底}) × {高} ÷ 2 = {面积}`
- `track_lap_formula` — `长×2 + π×宽 = {长}×2 + 3.14×{宽} = {一圈}`

## 渲染规则

### 颜色
- 背景：`#0f172a`
- 网格线：`rgba(100, 116, 139, 0.12)`
- 坐标轴：`rgba(100, 116, 139, 0.25)`
- 可拖动点：`#7c3aed`（紫色），高亮
- 不可拖动点：`#64748b`（灰色）
- 主线条：`#e2e8f0`（浅色，深色背景下清晰）
- 辅助线/高线：`#2563eb`（蓝色），虚线
- 长度标注：`#059669`（绿色）
- 角度标注：`#ea580c`（橙色）
- 面积填充：`rgba(124, 58, 237, 0.10)`（浅紫透明）

### 尺寸
- 线条宽度 ≥ `2.5px`
- 点半径 ≥ `5px`（拖动时 `7px`）
- 文字 ≥ `14px`
- 触摸热区半径 ≥ `20px`（以点为中心的不可见判定圆）

### 坐标系
- 数学坐标系：y 轴向上为正。
- 屏幕变换：`screenX = originX + mathX × scale`，`screenY = originY - mathY × scale`。
- 网格步长 = `scale`（1 个数学单位对应 scale 像素）。

## 交互规则

### 拖动
- 使用 Pointer Events API 统一处理鼠标和触摸。
- 拖动时：更新点坐标 → 重算依赖点 → 重新渲染 → 更新测量面板。
- 吸附：开启时拖动到 `snapSize` 的整数倍。

### 视觉反馈
- 悬停在可拖动点上：点放大 + 鼠标变为 `grab`。
- 拖动中：点放大 + 鼠标变为 `grabbing` + 显示坐标提示。
- 不可拖动点：鼠标为 `default`。

### 防误触
- 触摸拖动时阻止页面滚动（`e.preventDefault()`）。
- 点的判定半径 = `max(点半径, 20px)`。

## 教学场景

### 场景1：面积探索
- 长方形：拖动对角顶点，观察面积 = 长 × 宽。
- 三角形：拖动顶点，观察面积 = 底 × 高 ÷ 2，高线实时显示。
- 平行四边形：拖动顶点，观察面积 = 底 × 高（不是斜边 × 斜边）。
- 梯形：拖动顶点，观察面积 = (上底 + 下底) × 高 ÷ 2。
- 圆：拖动半径点，观察面积 = πr²，周长 = 2πr。

### 场景2：割补变换
- 平行四边形 → 长方形：高线分割，左侧三角形平移到右侧。
- 两个三角形 → 平行四边形：翻转拼接。
- 两个梯形 → 平行四边形：翻转拼接。

### 场景3：跑道问题
- 拖动改变长和宽，一圈长度 = 长×2 + π×宽 实时更新。
- 可视化两个半圆合成为一个整圆的过程。

### 场景4：公式验证
- 拖动改变尺寸，公式中数值实时替换，验证公式正确性。
- 例如：拖动三角形顶点，始终看到 面积 = 底 × 高 ÷ 2 成立。

## 移动端适配规则

- 画布响应式：宽度 100%，高度根据视口动态计算。
- 触摸事件：使用 `touch-action: none` 防止默认手势干扰。
- 点的触摸热区 ≥ `20px` 半径。
- 文字 ≥ `14px`，线条 ≥ `2.5px`。
- 测量面板在画布下方，可滚动查看。
- 支持横屏和竖屏。

## 集成到 graph.html 的规则

1. 交互引擎作为独立模块嵌入（`<script>` 块或独立 JS 文件）。
2. 在聊天快捷栏新增「🎮 交互探索」按钮，切换到交互模式。
3. 交互模式下：
   - 用户输入题目 → AI 生成交互式构造 JSON → 引擎渲染可拖动图形。
   - 画布替换或叠加在消息区域。
   - 测量面板显示在画布下方。
4. 保留静态画图模式作为回退（交互引擎加载失败时）。
5. 交互模式与几何模式（primary-geometry-diagram-solver）共存：
   - 几何模式：静态画图解题。
   - 交互模式：动态探索验证。
6. 交互构造 JSON 通过 AI 返回的 ` ```json ` 代码块解析，格式同本规范。

## 常见错误提醒

- 依赖点必须在引用它的对象之前定义。
- 多边形顶点顺序必须一致（顺时针或逆时针），否则面积计算错误。
- 圆的 radiusPoint 不能与 center 重合，否则半径为 0。
- 跑道的 4 个顶点必须构成矩形（A、C 对角自由，B、D 依赖）。
- 高线的 vertex 必须在 base1-base2 所在直线的上方或下方，不能在线上。
- 拖动时不能把点拖出画布范围。

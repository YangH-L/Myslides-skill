# 详细排版参数、双字体槽模板与跨页深色色板手册 (`style-parameters.md`)

本手册提供 `Myslides-skill` 在 `16:9` 学术幻灯片构建、科研绘图与讲者备注撰写中的精确几何参数与可直接复用的代码片段。

---

## 一、标准画布与版面几何参数（`1280 × 720 px` / `13.333" × 7.500"`）

换算基准：`1 px = 9,525 EMU = 0.75 pt`（`96 DPI` 逻辑像素对应 `72 DPI` 字号磅值）。

| 版面区域 | 推荐坐标与尺寸 (`px`) | 字号与字重 | 颜色与对齐规范 |
|---|---|---|---|
| **安全边距** | 左 `x = 56`，右 `x = 1224`（内容净宽 `1168`） | — | 全片统一左右对齐基准线 |
| **内页单行主标题** | `x = 56, y = 46–50, w = 1080, h = 46` | `22–24 pt` 加粗 | 深海蓝 `#0B2E4F`，左对齐，无句号，不设灰字副标 |
| **右上页码** | `x = 1144, y = 52, w = 80, h = 28` | `13–14 pt` 常规/加粗 | 深炭钢灰 `#374151`，右对齐，`Times New Roman` |
| **标题下分割线** | `x1 = 56, y1 = 94, x2 = 1224, y2 = 94` | 线宽 `1.5–1.8 pt` | 深海蓝 `#0B2E4F` |
| **主内容可用区** | `x = 56..1224, y = 112..586`（净高 `474`） | 分节标题 `14–15.5 pt` 加粗；正文 `12–13.5 pt` | 标题 `#0B2E4F`；正文 `#111827` / `#000000`；重点 `#C00000` 加粗（最关键 1–2 处放大 `+1~+2 pt`） |
| **底部结论上细线** | `x1 = 56, y1 = 598, x2 = 1224, y2 = 598` | 线宽 `0.75–1.0 pt` | 中深钢灰 `#475569` 或 `#94A3B8`（仅装饰细线） |
| **底部无前缀居中结论** | `x = 68, y = 612–618, w = 1144, h = 24–28` | `13–16 pt` 加粗 | **不写任何前缀，不加左侧彩条**；整行 `CENTER` 水平居中，无句号 |
| **页脚细线与页脚** | 细线 `y = 662`；文字 `y = 674, h = 24` | `11–12 pt` | 左放年月 `2026.11`，右放 `02 / 10`，色值 `#374151`（禁浅灰），`Times New Roman` |

---

## 二、`python-pptx` 双字体槽强制绑定与无前缀居中结论代码模板

```python
from lxml import etree
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

EMU_PER_PX = 9525

def px(val: float) -> Emu:
    return Emu(int(round(val * EMU_PER_PX)))

def bind_dual_fonts(
    run,
    size_pt: float,
    color_hex: str = "111827",
    bold: bool = False,
    italic: bool = False,
    ea_font: str = "SimHei",
    latin_font: str = "Times New Roman",
) -> None:
    """强制分离西文/数字槽 (Times New Roman) 与中文槽 (黑体/宋体/仿宋)。"""
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    h = color_hex.lstrip("#")
    run.font.color.rgb = RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    rPr = run._r.get_or_add_rPr()
    rPr.set("lang", "zh-CN")
    rPr.set("altLang", "en-US")
    for tag, face in (("a:latin", latin_font), ("a:cs", latin_font), ("a:ea", ea_font)):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", face)

def add_centered_takeaway(slide, segments, y_px: float = 614.0, base_pt: float = 14.0):
    """
    添加无前缀、无左侧竖条、整行水平居中的底部结论栏。
    segments 示例:
      [("提出面向动态图流的增量近似算法，吞吐量", False, False),
       ("提升 12.4×", True, True),
       (" 且内存开销", False, False),
       ("降低 63.5%", True, False)]
    其中三元组为 (文本, 是否标红重点, 是否额外放大 +1.5pt)。
    """
    tb = slide.shapes.add_textbox(px(68), px(y_px), px(1144), px(26))
    tf = tb.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    for text, is_red, boost_size in segments:
        clean_text = text.rstrip("。")
        r = p.add_run()
        r.text = clean_text
        pt = base_pt + (1.5 if boost_size else 0.0)
        bind_dual_fonts(r, size_pt=pt, color_hex="C00000" if is_red else "111827", bold=True)
    return tb
```

---

## 三、跨页科研图表 7 套大屏高对比深色色板（零浅灰）

所有图表坐标轴线、刻度线与文字统一使用浓黑 `#111827`（或纯黑 `#000000`），严禁使用 `#B8B8B8`、`#9CA3AF`、`#667085` 等浅灰色。连续页面按以下色板轮换以增强跨页辨识度：

| 序号 | 色系名称 (`palette_key`) | 主方法色 (`primary`) | 次要/扩展色 (`secondary`) | 对照基线深色 (`baseline`) | 重点标红色 (`highlight`) |
|---|---|---|---|---|---|
| 1 | `deep_navy`（深海蓝） | `#0F3D75` | `#2B5B84` | `#374151` | `#C00000` |
| 2 | `deep_teal`（深青蓝） | `#0F5257` | `#0E7490` | `#334155` | `#C00000` |
| 3 | `deep_indigo`（深靛蓝） | `#1E3A8A` | `#2563EB` | `#374151` | `#C00000` |
| 4 | `deep_forest`（深墨绿） | `#14532D` | `#166534` | `#334155` | `#C00000` |
| 5 | `deep_violet`（深紫蓝） | `#312E81` | `#4338CA` | `#374151` | `#C00000` |
| 6 | `prussian_amber`（普鲁士蓝+深琥珀棕） | `#0B2E4F` | `#9A3412` | `#334155` | `#C00000` |
| 7 | `deep_cobalt`（深钴蓝） | `#1E40AF` | `#3B5998` | `#334151` | `#C00000` |

---

## 四、讲者备注标准模板（习惯 8：口播置顶 + 阿拉伯数字直读 + 分隔线 + 白话拆解与括号来源置底）

写入 `slide.notes_slide.notes_text_frame` 及配套 `notes/total.md` 时，严格遵循以下两项规则：
1. **上下顺序**：`【一、现场汇报口播参考】` 置顶 → 分隔线 `---` → `【二、本页白话拆解（供会前自己看懂）】` → 末尾 `（图表与数据来源：...）`，确保演示者视图首屏直接呈现口播词。
2. **阿拉伯数字直读**：口播词与白话拆解中的数值、百分数、小数、倍数、样本量、金额与时长**统一使用阿拉伯数字与 `%`**（如 `1,200 组`、`12.4 倍`、`63.5%`、`300 万元`、`4.5 分钟`），**不转写为“一千二百组”“十二点四倍”“百分之六十三点五”等汉字**（“第一”“一阶段”“三线表”等固有词汇正常保留汉字）。

```markdown
【一、现场汇报口播参考】
针对大规模动态图流上全量重算开销过高的问题，我们提出了基于局部度数上界的增量近似维护方法。在 4 个公开图基准共 1,200 组查询实测中，平均吞吐量提升 12.4 倍，内存占用降低 63.5%，且近似比严格保持在理论界以内。下一步将在 10 亿边规模分布式流引擎上补充延迟尾部测试。

---

【二、本页白话拆解（供会前自己看懂）】
1. 痛点直觉：以前每来一批新边就要把整个子图重跑一遍，线上延迟超过 5 秒根本没法用；我们发现 90% 的新边根本不会跨过局部密度阈值，直接用廉价上界筛掉就能省掉绝大部分重算。
2. 关键数字口径：吞吐量提升 12.4× 是在 n = 1,200 组随机查询上的几何平均值；内存降低 63.5% 是峰值常驻内存对比全量快照索引的结果。
3. 适用边界备询：当前理论近似界建立在无向非负权图假设上；若存在高频批量删边与负权边，需回退至周期性局部重构。

（图表与数据来源：动态图流增量维护实验记录，2026.11；公开基准数据集 Cora、PubMed、ogbn-arxiv 与 Reddit-Stream，查询样本量 n = 1,200，单机 16 核 CPU 实测）
```

---

## 五、用户手改 `.pptx` 原位增量修改操作守则

1. **先做物理备份**：修改前先将用户手改文件复制为 `<原文件名>_个人原稿备份.pptx` 并校验 SHA-256。
2. **只动指定对象**：用 `python-pptx` 直接加载用户文件，换图时读取原图 `left, top, width, height` 按比例居中嵌入新图并清理未引用旧媒体；改字时仅替换目标 `<a:r>` 内的 `<a:t>` 字符串，绝不重建文本框或覆盖用户调整过的字号、标红与隐藏页属性（`show="0"`）。
3. **差异审计**：保存后对比修改前后每页文本框列表，确认除明确要求微调的词句外其余文本框 100% 零变动。

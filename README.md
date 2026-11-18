# Myslides-skill — 个人学术汇报幻灯片、高对比科研配图与讲者备注规范

`Myslides-skill` 是一套面向 **学术汇报、阶段考核、项目验收、学位答辩与组会报告**（支持 PPTX / SVG / PDF / Gamma 及科研报告）的个人风格规范与自动化质检技能包，同时兼容 **OpenAI Codex**、**Claude Code** 与 **Google Antigravity** 三端智能体环境。

---

## 核心九条规范速览

1. **提纲无句号**：幻灯片上屏内容是凝练提纲而非长文，句末尽可能不加 `。`（句内 `，`、`；`、`、`、`：` 正常使用）。
2. **底部无前缀居中结论栏**：内页底部不写 `本页核心结论：` 等前缀，只放结论正文，整行**水平居中对齐**（无左侧竖条、无圆角灰底框）。
3. **去 AI 化学术用语与团队分寸**：禁说 `探针`（改称 `检验/测试/检测/实验`），禁说 `人工金标准/金标`（改称 `人工标注`，公开集自带真值称 `标准答案/基准标注`），全面禁用 `锁稿/全绿验收/架构翻转/跃升/倒挂/底座/排雷/闭环/同尺桥接/论文矩阵/锚定/咬合/假世界` 等生造词；在团队共享系统上汇报个人阶段工作时统一定位为 `增量式优化 / 模块优化`，绝不擅自冠名 `2.0 升级`。
4. **中英字体严格双槽分离**：所有西文、数字与统计符号一律设为 **`Times New Roman`**；中文按正式材料层级统一使用 **`黑体` / `宋体` / `仿宋`**（同片同级严格一致）。
5. **图表零来源底注、正式学术命名与跨页色板区分**：图内绝不放 `来源：...` 或 `注：...`；轴名、表头、图例与数值标签 100% 使用正式学术用语（禁 `越高越好/零假阳性/仅看可见行为` 等白话）；不同页轮换使用 7 套高对比深色科研色板。
6. **大会议室大屏高对比度配色**：严禁使用浅灰（`#B8B8B8`、`#9CA3AF`、`#667085` 等）；文字、轴线与基线柱统一采用浓黑（`#111827`）、深海蓝（`#0B2E4F`）与深炭钢灰（`#374151`）。
7. **重点标红加粗与关键指标 `+1~+2pt` 提级**：正文基底保持单一深色，每页精选核心突破使用学术红（`#C00000` / `#FF0000`）加粗，最关键 1–2 处指标字号放大 `+1pt ~ +2pt`。
8. **置顶口播（阿拉伯数字直读）+ 置底白话拆解与括号来源备注**：每页讲者备注按 **`【一、现场汇报口播参考】`（置顶，演示者视图首屏直看无需删改；口播中的数值、百分数、倍数、金额与时长直接使用阿拉伯数字与 `%`，如 `96.5%`、`12.4 倍`、`4.5 分钟`，不转写为“百分之九十六点五”等汉字）+ 分隔线 `---` + `【二、本页白话拆解（供会前自己看懂）】` + `（图表与数据来源：...）`** 编写。
9. **末页固定“感谢聆听”收尾页**：末页固定增设与封面视觉体系首尾呼应的庄重 `感谢聆听` 页；用户已手动修订过的 `.pptx` 必须先备份再原位增量编辑，严禁全量覆盖。

---

## 仓库目录结构

```text
Myslides-skill/
├── SKILL.md                        # 智能体加载的 9 条核心规范与工作流指令
├── README.md                       # 仓库说明、三端安装与 GitHub 推送指南
├── LICENSE                         # MIT 开源许可证
├── .gitignore                      # Python 缓存与 Office 临时锁文件忽略规则
├── agents/
│   └── openai.yaml                 # OpenAI Codex 技能界面与策略元数据
├── assets/
│   └── myslides-icon.svg           # 技能矢量图标（深海蓝 #0B2E4F + 学术红 #C00000）
├── scripts/
│   ├── audit_slides.py             # PPTX 与讲者备注 6 项规范自动质检 CLI 脚本
│   └── mpl_academic_style.py       # Matplotlib 双字体栈、7 套深色色板与正式用语自检库
└── references/
    └── style-parameters.md         # 1280×720 坐标表、python-pptx 代码模板与备注样板
```

---

## 三端一键安装说明

### 1. OpenAI Codex
将 `Myslides-skill` 放入用户级或项目级技能目录，即可在对话中通过 `$myslides-skill` 显式调用或按任务自动触发：
```bash
# macOS / Linux
cp -r Myslides-skill ~/.codex/skills/Myslides-skill

# Windows PowerShell
Copy-Item -Recurse -Force .\Myslides-skill "$HOME\.codex\skills\Myslides-skill"
```

### 2. Google Antigravity
复制到全局配置技能目录或工作区 `.agents/skills/` 目录：
```bash
# macOS / Linux
cp -r Myslides-skill ~/.gemini/config/skills/Myslides-skill

# Windows PowerShell
Copy-Item -Recurse -Force .\Myslides-skill "$HOME\.gemini\config\skills\Myslides-skill"
```

### 3. Claude Code
复制到全局 `~/.claude/skills/` 或项目 `.claude/skills/` 目录：
```bash
# macOS / Linux
cp -r Myslides-skill ~/.claude/skills/Myslides-skill

# Windows PowerShell
Copy-Item -Recurse -Force .\Myslides-skill "$HOME\.claude\skills\Myslides-skill"
```

---

## 自动化质检与绘图脚本用法

```bash
# 1. 运行内置自检测试
python scripts/audit_slides.py --self-test
python scripts/mpl_academic_style.py

# 2. 对任意 PPTX 幻灯片与备注执行 6 项规范自动审查
python scripts/audit_slides.py path/to/deck.pptx --notes-md path/to/notes/total.md
```

---

## 推送至 GitHub 快捷指引

在 `Myslides-skill` 根目录下执行以下命令即可初始化仓库并推送至你的 GitHub 远端：

```bash
cd Myslides-skill
git init -b main
git add .
git commit -m "feat: initialize Myslides-skill academic presentation guidelines"
git remote add origin https://github.com/<your-username>/Myslides-skill.git
git push -u origin main
```

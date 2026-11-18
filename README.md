# Myslides-skill — 个人学术汇报幻灯片、高对比科研配图与讲者备注规范

`Myslides-skill` 是一套面向 **学术汇报、阶段考核、项目验收、学位答辩与组会报告**（支持 PPTX / SVG / PDF / Gamma 及科研报告）的个人风格规范与自动化质检技能包，同时兼容 **OpenAI Codex**、**Claude Code** 与 **Google Antigravity** 三端智能体环境。

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

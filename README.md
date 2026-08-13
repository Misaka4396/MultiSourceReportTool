# MultiSourceReportTool — 多源报告汇总推送工具

[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)]()
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![UI: PyQt5](https://img.shields.io/badge/UI-PyQt5-green.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**多源报告汇总推送工具** — Windows 桌面应用，一站式聚合 **7 大类信息源** 的报告与数据，
自动生成 **TXT / PDF 学术风格报告**。内置日报本地生成服务、文章抓取模块（trafilatura + 维基 API）、Windows XP 复古主题与自定义背景。

> ⚠️ 本项目仅供学习研究使用，抓取行为请遵守各站点 robots 协议与相关法律法规。

---

## 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [修改日志](#修改日志)
- [License](#license)

---

## 功能特性

### 七大信息源模块

| 模块 | 数据来源 | 核心能力 |
|------|----------|----------|
| 顶级咨询公司报告 | McKinsey, BCG, Roland Berger, Accenture | 公司多选、关键词 AND/OR、中英文切换、日期范围 |
| 券商研报 | 东方财富网 | 行业筛选、投资评级过滤、产业链图谱 |
| 海关编码查询 | UN Comtrade 口径 | HS 编码/关键词/国家/贸易类型/时间范围、前十贸易伙伴 |
| 灰色文献抓取 | World Bank, RAND, OECD 等 | 域名选择 + 自定义域名、文件类型过滤 |
| 预印本检索 | arXiv, SSRN | 学科分类、时间预设、来源平台选择 |
| Sci-Hub 下载器 | Crossref API (DOI 元数据) | 批量 DOI 输入、镜像站导航 |
| LibGen 电子书 | Library Genesis | 书名/作者/ISBN 多模式搜索、语言/格式过滤 |

### 双重报告生成模式

- **抓取并生成报告**（默认）：联网实时抓取 → 自动生成 TXT + PDF 报告
- **直接生成报告**：一键使用内置示例数据，跳过网络请求，即时产出报告

### 学术风格 PDF 报告

- 封面页（标题 / 副标题 / 生成日期 / 装饰线）
- 自动目录（章节编号 §1 §2... + 点状引导线 + 页码）
- 图文章节渲染，中文字体自动适配
- 参考文献列表，单栏 / 双栏排版切换

### 其他

- **自定义背景**：顶部栏「背景」→ 本地图片 → 自动拉伸铺满 → 窗口缩放自适应
- **日报本地生成服务**：设置每日生成时间（默认 09:00）+ 多选信息源模块 + 输出目录 → 每天到点后台自动抓取并生成 `daily_report_YYYYMMDD.txt/.pdf`，每日自动去重，界面实时显示生成状态与文件路径，支持「立即生成一次」
- **Windows XP (Luna) 复古主题**：经典蓝色渐变标题栏、XP 式圆角渐变按钮、米色面板、Tahoma/宋体字体体系

### 文章抓取模块（v1.2.1 新增）

命令行抓取任意文章网页 → 提取正文 → Markdown / PDF 日报：

```bash
# 抓取单篇文章（输出 out/<站点>_<日期>_<标题>.md）
E:\Anaconda3-2026\python.exe -m article_grab.grabber https://example.com/article

# 批量 + 生成 PDF 日报
E:\Anaconda3-2026\python.exe -m article_grab.grabber --file urls.txt --pdf
```

- **正文提取**：trafilatura 自动剥离导航/广告/页脚，提取标题/作者/日期/站点
- **维基百科**：词条页自动走官方 REST API（页面 HTML 反爬 403 时依然可用，支持 7 种语言）
- **PDF 日报**：封面/目录/分节，中文字体自动适配，防文字挤压（0 重叠 0 溢出）

## 快速开始

### 方式一：直接运行 EXE

下载 `dist/MultiSourceReportTool.exe`，双击运行（无需安装 Python）。

### 方式二：源码运行

```bash
pip install -r requirements.txt
python main.py
```

### 方式三：自行打包

```bash
build.bat
# 或
pyinstaller --onefile --windowed --name "MultiSourceReportTool" --icon "resources/app_icon.ico" --add-data "resources;resources" main.py
```

## 项目结构

```
MultiSourceReportTool/
├── main.py                  # 应用入口
├── build.bat                # PyInstaller 打包脚本
├── generate_icon.py         # 图标生成脚本
├── resources/
│   └── app_icon.ico         # 应用图标
├── ui/
│   ├── main_window.py       # 主窗口（导航/路由/背景）
│   ├── styles.py            # 全局 QSS 样式（XP 主题）
│   ├── daily_service.py     # 日报本地生成服务
│   └── pages/               # 7 个信息源页面
├── article_grab/            # 文章抓取模块（v1.2.1）
│   ├── grabber.py           # 正文提取（httpx + trafilatura + 维基 API）
│   ├── pdf_daily.py         # PDF 日报生成（防挤压排版）
│   └── __init__.py
├── fetchers/                # 7 个数据抓取器
├── report/
│   ├── txt_writer.py        # TXT 报告生成
│   └── pdf_writer.py        # PDF 学术风格报告 (fpdf2)
├── tests/                   # pytest 测试套件（26 用例）
├── pyproject.toml           # ruff/black/mypy/pytest 配置
├── .github/workflows/       # GitHub Actions CI
└── .pre-commit-config.yaml
```

## 修改日志

详见 [CHANGELOG.md](CHANGELOG.md)。

## License

MIT License — 详见 [LICENSE](LICENSE)
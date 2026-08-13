# MultiSourceReportTool 修改日志

本项目使用 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式。

## [v1.2.1] - 2026-08-13

### 新增
- feat: 文章抓取模块（`article_grab/`）— trafilatura + httpx 正文提取（标题/作者/日期/站点/正文），请求重试 + 真实浏览器头，文件名净化（防路径穿越）
- feat: **维基百科 API 适配器** — 词条页 HTML 反爬 403 时自动走官方 REST API（支持 zh/en/ja/fr/de/ru/es 7 语言）
- feat: 文章抓取 PDF 日报（`article_grab/grabber.py --pdf`）— 封面/目录/分节，中文字体自动适配，防文字挤压排版（中英分段换行 + 超长 URL 逐字符硬断）
- test: 26 个 pytest 用例（单元 + 集成，含 PDF 重叠/溢出逐词检测、维基 API 适配器、HTTP mock 替身）

### 工程化
- build: `pyproject.toml`（ruff/black/mypy strict/pytest + setuptools 显式模块声明）
- build: `.pre-commit-config.yaml` 提交前自动检查
- build: `.github/workflows/ci.yml` — GitHub Actions（Python 3.10/3.13 矩阵：lint→format→mypy→test+cov≥80%）

### 修复
- fix: trafilatura 2.2 API 变更（`extract_metadata` 参数 `url`→`default_url`）
- fix: 正文丢失 — 按「原文链接」内容匹配回填元数据
- fix: PDF 换行符缺字形 — 按段落渲染正文
- fix: 裸 `except Exception: pass` 吞异常 — 引入 logging + 收窄异常类型
- fix: 中文字体跨平台查找（Windows/Linux/macOS 候选），CI 安装 fonts-noto-cjk

## [v1.2.0] - 2026-08-13

### 新增
- feat: 日报本地生成服务（`ui/daily_service.py`）— 可配置每日生成时间（默认 09:00）、多选信息源模块、输出目录；到点后台自动抓取并生成 `daily_report_YYYYMMDD.txt/.pdf`；每日自动去重，界面含服务状态面板（上次生成时间 / 状态 / 文件路径），支持「立即生成一次」
- feat: 日报 PDF 专用生成器 `generate_daily_pdf_report` — 按模块分节渲染 + 表格排版（长单元格自动换行、行高自适应）

### 变更
- style: 全界面改为 Windows XP (Luna) 复古主题 — 经典蓝色渐变标题栏、XP 式圆角渐变按钮（蓝绿高光/按下凹陷）、米色面板 #ECE9D8、Tahoma/宋体字体体系、XP 风格滚动条/复选/单选/输入框
- refactor: `ui/main_window.py` 原「定时任务设置」对话框升级为「日报本地生成服务」面板

### 修复
- fix: PDF 报告文字互相挤压/溢出 — `report/pdf_writer.py` 重写排版引擎：中英文分段智能换行、超长无空格 URL 逐字符硬断行、标题截断、显式坐标写入替代 multi_cell 坐标冲突、分页时样式重应用；极端长文本实测 0 重叠 0 溢出

## [v1.1.0] - 2026-08-06

### 文档规范化
- 覆写 README.md：统一项目徽章、功能特性表（7 信息源 + 报告生成）、快速开始、项目结构
- 新增 CHANGELOG.md 修改日志
- 新增 LICENSE (MIT, Misaka4396)

## [v1.0.0] - 2026-08-04

### 初始版本
- feat: 7 模块完整 UI — 约束筛选 + 异步抓取 + 报告生成
- feat: 自定义背景图片 + 二次元风格应用图标
- docs: README — 项目文档与完整更新日志
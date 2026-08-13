# MultiSourceReportTool 修改日志

本项目使用 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式。

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
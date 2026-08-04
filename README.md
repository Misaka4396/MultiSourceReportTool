# 多源报告汇总推送工具

**Multi-Source Report Aggregation Tool** — Windows 桌面应用，一站式聚合来自 7 大类信息源的报告与数据，自动生成 TXT/PDF 学术风格报告。

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![UI](https://img.shields.io/badge/UI-PyQt5-green)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 主要功能

### 七大信息源模块

| 模块 | 数据来源 | 核心能力 |
|------|----------|----------|
| 顶级咨询公司报告 | McKinsey, BCG, Roland Berger, Accenture | 公司多选、关键词 AND/OR 逻辑、中英文切换、日期范围 |
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
- 参考文献列表
- 单栏 / 双栏排版切换

### 自定义背景

顶部栏「背景」按钮 → 选择本地图片 → 自动拉伸铺满内容区背景 → 窗口缩放自适应

### 定时任务

侧边栏底部「定时任务」按钮 → 选择执行模块 + 间隔时间 + 输出目录 → 定时自动抓取

---

## 运行方式

### 方式一：直接运行 EXE

下载 `dist/MultiSourceReportTool.exe`，双击运行（无需安装 Python）。

### 方式二：源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python main.py
```

### 方式三：自行打包

```bash
# 一键打包
build.bat

# 或手动执行
pyinstaller --onefile --windowed --name "MultiSourceReportTool" --icon "resources/app_icon.ico" --add-data "resources;resources" main.py
```

---

## 项目结构

```
report1/
├── main.py                  # 应用入口
├── build.bat                # PyInstaller 打包脚本
├── requirements.txt         # Python 依赖
├── generate_icon.py         # 图标生成脚本
├── resources/
│   └── app_icon.ico         # 二次元风格应用图标
├── ui/
│   ├── main_window.py       # 主窗口（导航栏/页面路由/背景设置）
│   ├── styles.py            # 全局 QSS 样式表
│   └── pages/
│       ├── base_page.py     # 页面基类（字段选择/格式/输出/报告生成）
│       ├── consulting_page.py
│       ├── brokerage_page.py
│       ├── hs_code_page.py
│       ├── grey_lit_page.py
│       ├── preprint_page.py
│       ├── scihub_page.py
│       └── libgen_page.py
├── fetchers/
│   ├── base.py              # HTTP 请求基类（UA 伪装/HTML 解析）
│   ├── consulting.py        # 咨询公司报告抓取
│   ├── brokerage.py         # 券商研报抓取
│   ├── hs_code.py           # 海关编码数据
│   ├── grey_lit.py          # 灰色文献搜索
│   ├── preprint.py          # 预印本检索
│   ├── scihub.py            # Sci-Hub DOI 查询
│   └── libgen.py            # LibGen 电子书搜索
└── report/
    ├── txt_writer.py        # TXT 格式化报告生成
    └── pdf_writer.py        # PDF 学术风格报告生成 (fpdf2)
```

---

## 更新记录

### v1.0.0 — 初始版本

**核心框架**
- PyQt5 主窗口框架，左侧导航栏 + StackedWidget 页面路由
- 全局 QSS 现代浅色主题，微软雅黑字体
- 高 DPI 支持
- 状态栏实时时钟

**7 大数据源抓取**
- 咨询公司报告（McKinsey / BCG / Roland Berger / Accenture）
- 券商研报（东方财富网）
- 海关编码贸易数据（UN Comtrade）
- 灰色文献（World Bank / RAND / OECD）
- 预印本检索（arXiv / SSRN）
- Sci-Hub DOI 元数据查询（Crossref API）
- Library Genesis 电子书搜索

**报告生成引擎**
- TXT 格式化纯文本报告（分隔线排版、自动编号）
- PDF 学术风格报告（封面 + 目录 + 章节 + 参考文献）
- 中文字体自动检测（微软雅黑 / 宋体 / 黑体）
- 单栏 / 双栏排版切换

**交互优化**
- 后台线程异步抓取，UI 不阻塞
- 状态栏实时进度反馈
- 每个模块独立约束条件（关键词逻辑、日期范围、行业筛选等）
- 输出格式/字段/目录可配置
- 定时任务调度对话框

**直接生成报告**
- 所有模块支持「抓取并生成报告」+「直接生成报告（示例数据）」双模式
- 分裂按钮（QToolButton MenuButtonPopup）交互
- 下拉菜单黑底白字风格

**个性化**
- 自定义背景图片（本地图片 → 拉伸填充 → 窗口缩放自适应）
- 二次元风格应用图标（粉紫渐变 + 萌系文档拟人 + 星芒装饰，7 尺寸嵌入）

**数据容错**
- 实时抓取失败时自动回退内置 MOCK 示例数据
- 所有抓取器基于 BaseFetcher 统一基类（UA 伪装 + HTML 解析 + 异常保护）

---

## 技术栈

| 层级 | 技术 |
|------|------|
| UI 框架 | PyQt5 (Qt 5.15+) |
| HTTP 请求 | requests 2.28+ |
| HTML 解析 | BeautifulSoup4 + lxml |
| PDF 生成 | fpdf2 2.7+ |
| 打包部署 | PyInstaller 6.x (--onefile --windowed) |

---

## 开发说明

- 所有 `.py` 文件使用 UTF-8 编码
- 抓取器统一继承 `BaseFetcher`，实现 `fetch()` 方法返回 `(data, is_mock)`
- UI 页面统一继承 `BasePage`，覆写 `get_sample_data()` 支持直接生成
- 图标通过 `python generate_icon.py` 重新生成

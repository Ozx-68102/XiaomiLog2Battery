## 简介 Simply Introduction
通过小米手机日志去分析手机的电池容量。<br />
A program which analyzes battery capacity from logs of Xiaomi smartphones.

## 注意事项 Precautions
通过本项目分析得出的电池容量可能与官方售后检测结果有差异，一切请以官方检测的数据为准。<br />
Please note that the battery capacity analyzed by this project may differ from official after-sales inspection results. All data shall be subject to official test results.

## 信息 Information
Python 版本要求：**3.13**<br />
主程序启动入口：`run.py`，Web 界面语言：仅支持**英语**。<br />
运行步骤：<br />
1. 前置：确保已安装 Python 3.13（建议从 [Python 官网](https://www.python.org/) 下载）；<br />
2. 依赖安装：运行 `Modules/Core/PackageCheckers.py`，程序会自动检测并安装所有必需的第三方库（无需手动执行 `pip install`）；<br />
3. 启动服务：运行 `run.py`，程序会自动启动本地 Web 服务（默认地址：http://localhost:8050/ ），并打开浏览器跳转到分析面板；<br />
4. 分析日志：在 Web 面板的上传区域，直接拖拽小米日志`zip`文件（如 `bugreport-2024-10-01-001217.zip`），系统会自动完成“解压->解析->数据存储->图表生成”，最终在页面显示结果。<br />

调试建议：推荐使用 `PyCharm 2024.1.7` 及以上版本打开项目，便于代码调试。<br />

Python Version Requirement: **3.13**<br />
Main Program Entry: `run.py`, Web Interface Language: **English only**.<br />
Usage Steps:<br />
1. Prerequisite: Ensure Python 3.13 is installed (recommended to download from [Python Official Website](https://www.python.org/));<br />
2. Dependency Installation: Run `PackageChecker.py` — the program will automatically detect and install all required third-party libraries (no manual `pip install` needed);<br />
3. Start Service: Run `run.py` — the program will automatically start a local Web server (default address: http://localhost:8050/ ) and open a browser to navigate to the analysis panel;<br />
4. Analyze Logs: On the Web panel's upload area, drag and drop Xiaomi log `zip` files (e.g., `bugreport-2024-10-01-001217.zip`). The system will automatically complete "decompression->parsing->data storage->chart generation" and finally display results on the page.<br />

Debugging Suggestion: It is recommended to open the project with `PyCharm 2024.1.7` or later for easier code debugging.

## 技术栈 Technology Stacks
**主编程语言：Python**

1. **Web 交互与界面模块（Dashboard）**
   - 基于 `Dash` 框架构建本地 Web 面板，实现页面布局、组件渲染与交互逻辑（如文件上传触发图表更新）；
   - 使用 `dash-bootstrap-components` 优化 UI 结构（容器、卡片、行布局等），提升界面规整性；
   - 集成自定义 `dash-uploader` 组件【本地 whl 安装，基于已归档项目的**自定义 Fork 版本（由本人维护）**：[dash-uploader](https://github.com/Ozx-68102/dash-uploader)】，支持多文件拖拽上传，简化用户操作；
   - 通过 `threading.Timer` 实现服务启动后自动打开浏览器，优化用户体验；
   - 支持两种操作模式：初始化模式（重建数据库）和追加模式（向现有数据库添加数据）。

2. **文件处理模块（FileProcess）**
   - 负责小米日志 `zip` 文件的自动解压、 `txt` 日志提取与路径管理，核心依赖 Python 内置 `os` 库；
   - 支持多文件并发处理，保障批量上传时的解析效率；
   - 分离“解压逻辑”与“路径管理”，增强代码可维护性，便于后续扩展文件格式支持；
   - 使用 Python 类型提示，提升代码可读性与静态类型检查适配性。

3. **数据分析与可视化模块（DataAnalysis）**
   - 数据处理：依赖 `pandas` 实现日志数据清洗（时间格式转换、无效容量值过滤）、平均容量计算与 DataFrame 结构化；
   - 数据存储：引入 `sqlite3` 轻量级数据库替代本地 CSV 文件，提升相同数据体量下的存储效率，支持结构化查询；
   - 新增数据追加功能，支持向现有数据库追加数据，无需重建表结构；
   - 可视化生成：基于 `plotly` 库创建交互式图表：
     - 电池容量变化图：用 `plotly.subplots` 与 `go.Scatter` 实现多容量指标折线图（含平均值虚线），支持 hover 查看详情；
     - 电池健康度饼图：用 `go.Pie` 实现环形饼图，按健康百分比自动匹配颜色（绿/橙/黄/红），直观展示剩余容量占比；
   - 优化图表布局：固定宽高并调整图例位置，避免遮挡标题；
   - 改进电池容量平均值计算方式，提供更准确的整体数据展示。

4. **核心流程调度模块（Backend/Core）**
   - 封装“文件上传->解压->解析->入库->图表生成”全链路逻辑，作为 Web 回调与业务模块的桥梁；
   - 模块化设计（如 `BatteryDataService` 管理数据库交互、`PlotlyVisualizer` 负责图表生成），降低代码耦合度，便于扩展；
   - 重构代码架构，拆分单一回调为模块化流程，通过状态存储串联各环节，降低代码耦合度；
   - 消除全局变量风险，采用状态存储组件管理系统状态，提高线程安全性和代码可维护性。

5. **依赖管理工具**
   - 基于 `sys` 与 `subprocess` 实现 `PackageCheckers.py`，自动检测第三方库安装状态，缺失时自动执行安装；
   - 支持从本地 whl 文件安装自定义库，确保依赖一致性和部署可靠性；
   - 对特定版本依赖进行版本校验，确保环境一致性。

6. **跨平台适配**
   - 使用 `os.path` 处理文件路径（如动态生成 `INSTANCE_PATH`），避免硬编码绝对路径，支持 Windows/macOS/Linux；
   - 移除对 `.bat` 等系统脚本的依赖，统一通过 Python 脚本（`run.py`/`PackageCheckers.py`）管理，简化跨平台使用。


**Main Programming Language: Python**

1. **Web Interaction & Interface Module (Dashboard)**
   - Builds a local Web panel based on the `Dash` framework, enabling page layout, component rendering, and interaction logic (e.g., chart updates triggered by file uploads);
   - Uses `dash-bootstrap-components` to optimize UI structure (containers, cards, row layouts, etc.) for better regularity;
   - Integrates custom `dash-uploader` component (local whl installation, based on **my own maintained Fork** of the archived project: [dash-uploader](https://github.com/Ozx-68102/dash-uploader)) to support drag-and-drop upload of multiple files, simplifying user operations;
   - Implements automatic browser opening after service startup via `threading.Timer` to enhance user experience;
   - Supports two operation modes: Initialization mode (rebuild database) and Append mode (add data to existing database).

2. **File Processing Module (FileProcess)**
   - Responsible for automatic decompression of Xiaomi log `zip` files, extraction of `txt` logs, and path management, with core dependencies on Python's built-in `os` library;
   - Supports concurrent processing of multiple files to ensure parsing efficiency during batch uploads;
   - Separates "decompression logic" from "path management" to improve code maintainability and facilitate future expansion of file format support;
   - Uses Python type hints to enhance code readability and adaptability to static type checking.

3. **Data Analysis & Visualization Module (DataAnalysis)**
   - Data Processing: Relies on `pandas` for log data cleaning (time format conversion, invalid capacity filtering), average capacity calculation, and DataFrame structuring;
   - Data Storage: Introduces the `sqlite3` lightweight database to replace local CSV files, improving storage efficiency for the same data volume and supporting structured queries;
   - Added data append functionality, supporting appending data to existing database without rebuilding table structure;
   - Visualization Generation: Creates interactive charts based on the `plotly` library:
     - Battery Capacity Change Chart: Uses `plotly.subplots` and `go.Scatter` to implement a line chart for multiple capacity indicators (with a dashed average line), supporting hover for details;
     - Battery Health Chart: Uses `go.Pie` to implement a donut chart, automatically matching colors (green/orange/yellow/red) based on health percentage to intuitively show remaining capacity ratio;
   - Optimizes Chart Layout: Fixes width/height and adjusts legend position to avoid covering titles;
   - Improved battery capacity average calculation method, providing more accurate overall data display.

4. **Core Process Scheduling Module (Backend/Core)**
   - Encapsulates the end-to-end logic of "file upload->decompression->parsing->database storage->chart generation" as a bridge between Web callbacks and business modules;
   - Modular design (e.g., `BatteryDataService` for database interaction, `PlotlyVisualizer` for chart generation) to reduce code coupling and facilitate expansion;
   - Refactored code structure, split single callback into modular processes, connected each link via state storage, reduced code coupling;
   - Eliminated global variable risks, used state storage components to manage system state, improving thread safety and code maintainability.

5. **Dependency Management Tool**
   - Implements `PackageCheckers.py` based on `sys` and `subprocess` to automatically detect the installation status of third-party libraries and execute installation if missing;
   - Supports installing custom libraries from local whl files, ensuring dependency consistency and deployment reliability;
   - Performs version verification for specific dependencies to ensure environment consistency.

6. **Cross-Platform Adaptation**
   - Uses `os.path` to handle file paths (e.g., dynamic generation of `INSTANCE_PATH`), avoiding hard-coded absolute paths and supporting Windows/macOS/Linux;
   - Removes dependencies on system scripts such as `.bat`, and unifies management via Python scripts (`run.py`/`PackageCheckers.py`) to simplify cross-platform usage.

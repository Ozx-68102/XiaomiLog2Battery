#### 注意 Attention
**由于临近升学申请季，作者需要参加雅思考试并准备相关事宜，项目维护暂停。**<br />
**Due to the approaching graduate school application season, I need to prioritize IELTS preparation and admission-related tasks, so project maintenance will be suspended.**
****
#### 简介 Simply Introduction
通过小米手机日志去分析手机的电池容量。<br />
A program which is analyzing battery capacity on logs from Xiaomi smartphones.
****
#### 注意事项 Precautions
通过本项目分析得出的电池容量可能与官方售后检测结果有差异，一切请以官方检测的数据为准。<br />
Please note that the battery capacity analyzed through this project might differ from the results of official after-sales inspections. All data should be considered definitive based on the official tests.
****
#### 信息 Information
Python 版本：**3.13.0**<br />
主程序：`Central.py`, 目前仅支持**英语**。<br />
运行方式：**（暂不可用）**<br />
1. 将小米日志原文件（类似于`bugreport-2024-10-01-001217.zip`之类的名字）复制到`zips`文件夹下，然后双击`Start.bat`文件。<br />
2. 使用PyCharm 2024.1.7及以上版本，新建项目，然后把下载的文件剪切进去，运行`Check_packages.py`安装所需包，将日志文件拷贝到`zips`文件夹下，再运行主程序。<br />

如果需要调试运行的话，建议使用PyCharm 2024.03或以上版本。<br />

Python version **3.13.0**<br />
Main program name: `Central.py`, only **English** is supported at the moment.<br />
Usage **(Temporarily Unavailable)**:<br />
1. Copy the original Xiaomi log file (with a name similar to `bugreport-2024-10-01-001217.zip`) to the folder named `zips` , and double-click `Start.bat` file.<br />
2. Using PyCharm 2024.1.7 and above to create a new project, then cut the downloaded file into it, and run `Check_packages.py` to install the required packages. Then, copy log files into the `zips` folder, and run the main program.<br />

For debugging, use PyCharm 2024.03 or later is recommended.<br />
****
####  技术栈 Technology Stacks
**主编程语言：Python**
1. **日志记录模块（LogRecord）-暂时移除-**
    1. 核心功能通过`Python`内置的`logging`和`logging.handlers`库实现日志记录。
    2. 使用`RotatingFileHandler`实现日志文件的大小轮换，避免日志文件过大造成的问题。
    3. 针对多进程环境使用`multiprocessing.Queue`和`QueueHandler`结合`QueueListener`同步日志记录，保证进程安全。
    4. 使用`json`库从日志配置文件`LoggerConfig.json`加载日志文件，从外部灵活调整日志格式、颜色与路径等参数，提高可维护性。
    5. 自定义`ColorHandler`类，结合继承`logging.StreamHandler`类的自定义`StreamHandler`类实现带颜色的终端输出，使异常更容易被及时识别。
2. **文件处理模块（FileProcess）**
    1. 该模块与上述的`LogRecord`模块结合，实现全面的日志跟踪。
    2. 使用内置的`os`和`shutil`库进行文件路径分析、文件夹的创建与删除，还有文件的覆盖等操作。
    3. 使用内置`concurrent.futures`库的`ProcessPoolExecutor`来实现多进程并发处理解压任务，多进程的独立环境与自定义日志记录模块的适配避免了资源竞争问题。
    4. 在多进程开始前根据文件的数量动态调整并发进程数。
    5. `multiprocessing.Manager`用于跨进程共享变量，使程序能够精准统计解压任务数。
    6. 将文件夹操作、日志记录与解压部分的逻辑分离，增强可维护性与可扩展性。
    7. 使用Python内置的类型提示，提高代码可读性与静态类型检查能力。
    8. 使用了`Python 3.10+`版本的`match...case...`语句，避免出现重复的`if`语句，同时这也是面向未来的写法。
3. **数据分析模块（DataAnalysis）**
    1. 和`LogRecord`模块结合实现日志追踪。
    2. 使用`pyecharts`生成可交互式图表。根据数据量动态使用`Scatter`散点图和`Line`折线图适配，展现出其灵活性。
       1. 当只有1条数据时折线图无法显示出数据，此时改为使用散点图呈现。
       2. 有2条或以上数据时则使用折线图显示数据，结合自定义工具提示、交互式缩放等功能。
       3. 使用`Grid`管理图表布局，确保样式协调。
       4. 提供动态的最大/最小Y轴范围并通过全局样式选项优化用户观看体验。
    3. 具有强大数据操作能力的`pandas`库用于读取`csv`文件并转换成`DataFrame`，通过`apply`函数灵活地对列数据进行批量转换，且在数据过滤中实现了针对特定条件的数据的修改。
4. **其他**
    1. 使用`sys`和`subprocess`库实现第三方库的自动安装。
    2. 整个项目使用面向对象编程（OOP），实现低耦合高内聚，使得功能代码更易重构和扩展。
    3. 代码的逻辑对路径处理与包安装等关键环节都使用`os`与`sys`处理而不是直接使用相对路径或绝对路径，使程序具有跨平台运行的潜力。
    4. 引入`batch`文件脱离对IDE的依赖，不需要繁杂的安装与配置过程。
<br />

**Main Programming Language: Python**
1. **Log Recording Module (LogRecord) - temporarily remove**
    1. Core functionality is implemented using Python's built-in `logging` and `logging.handlers` libraries.
    2. Utilizes `RotatingFileHandler` to handle log file size rotation, preventing oversize log files. 
    3. Ensures process-safe logging in multiprocess environments by combining `multiprocessing.Queue`, `QueueHandler`, and `QueueListener`.
    4. Loads log configurations from an external JSON file (LoggerConfig.json) using the `json` library, enabling flexible adjustment of log format, color, and paths for better maintainability.
    5. Implements a custom ColorHandler class, which inherits from logging.StreamHandler, to enable colored terminal outputs for easier identification of exceptions.

2. **File Processing Module (FileProcess)**
    1. Integrates with the `LogRecord` module for comprehensive log tracking.
    2. Uses built-in os and shutil libraries for file path analysis, directory creation, deletion, and file overwriting.
    3. Leverages ProcessPoolExecutor from the `concurrent.futures` library for concurrent multiprocess handling of decompression tasks. This ensures independent process environments and avoids resource conflicts.
    4. Dynamically adjusts the number of concurrent processes based on the number of files to be processed.
    5. Uses `multiprocessing.Manager` for cross-process shared variables, enabling precise tracking of decompression tasks.
    6. Separates logic for folder operations, log recording, and decompression to enhance maintainability and scalability.
    7. Employs Python's type hinting to improve code readability and enable static type checking.
    8. Implements the modern `match...case...` syntax (available in `Python 3.10+`), reducing redundant `if` statements and ensuring forward compatibility.

3. **Data Analysis Module (DataAnalysis)**
    1. Integrates with the `LogRecord` module for log tracking.
    2. Uses `pyecharts` to create interactive charts, adapting between Scatter and Line charts based on the amount of data:
       1. Uses scatter plots for single data points, as line charts cannot display single points effectively.
       2. Uses line charts for two or more data points, with custom tooltips, interactive zoom, and other features.
       3. Manages chart layout with `Grid` to ensure a consistent appearance.
       4. Dynamically adjusts Y-axis ranges and applies global style options for an optimized user experience.
    3. Leverages the `pandas` library for powerful data manipulation, including reading `csv` files into `DataFrame` objects. Performs batch transformations on columns using the `apply` function and filters data to meet specific conditions.

4. **Others**
    1. Uses `sys` and `subprocess` libraries to automate the installation of required third-party packages.
    2. The entire project is implemented using Object-Oriented Programming (OOP), achieving low coupling and high cohesion, making the codebase easier to refactor and extend.
    3. Handles critical operations like path management and package installation with `os` and `sys` libraries instead of relying on relative or absolute paths, enhancing cross-platform compatibility.
    4. Includes `batch` files to eliminate dependency on IDEs, simplifying installation and configuration processes.
****

#### 简介 Simply Introduction
通过小米手机日志去分析这部手机的电池容量。<br />
A program which is analyzing battery capacity on logs from Xiaomi smartphones.
****
#### 信息 Information
Python 版本：**3.13**<br />
主程序：`XiaomiLogFinder.py`, 目前仅支持**英语**。<br />
运行方式：<br />
1. 双击`Start.bat`。<br />
2. 使用PyCharm 2024.1.7及以上版本，新建项目，然后把下载的文件剪切进去，先运行`Check_packages.py`安装所需包，再运行主程序。<br />

如果需要调试运行的话，建议使用PyCharm 2024.03或以上版本。<br />

**方法1目前存在的一个缺点是：<br />
如果存在多机型日志压缩文件，则每生成一张图都需要关闭图片，程序才能继续。**

Python version **3.13**<br />
Main program name: `XiaomiLogFinder.py`, only **English** is supported at the moment.<br />
Usage:<br />
1. Double-click `Start.bat` to run this program.<br />
2. Using PyCharm 2024.1.7 and above to create a new project, then cut the downloaded file into it, and run `Check_packages.py` to install the required packages. Next, run the main program.<br />

For debugging, use PyCharm 2024.03 or later is recommended.<br />

**Note that there is a limitation with method 1:<br />
If there are multiple device log files in the `zips` folder, you will need to manually close each generated image for the program to continue running.**

****
####  依赖 Python 库（包含Python内置库且不分先后顺序） <br /> Required Python Packages in no particular order
- matplotlib
- pandas
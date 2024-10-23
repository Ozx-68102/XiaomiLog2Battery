import os
import re
import shutil
import time
import zipfile


class BatteryInfo:
    def __init__(self) -> None:
        self.tmp = r"./tmp"
        self.zip_filename = []
        self.filename = None
        if not os.path.exists(self.tmp):
            os.makedirs(self.tmp, exist_ok=True)

    def delete(self) -> None:
        """
        递归删除临时文件夹。
        :return: None
        """
        try:
            shutil.rmtree(self.tmp)
        except OSError as e:
            print("发生错误:" % e.strerror)

    def detect_whether_include_xm_log(self) -> None:
        count = 0
        currently_dir = os.path.dirname(__file__)
        skipped_directory = [".git", ".idea", ".venv", "__pycache__", "tmp"]

        for root, dirs, files in os.walk(currently_dir):
            print("当前目录:", root)
            dirs[:] = [d for d in dirs if d not in skipped_directory]

            for file in files:
                if file.endswith(".zip") and file.startswith("bugreport"):
                    print(f"检测到小米日志文件{count}:", file)
                    self.zip_filename.append(file)
                    count += 1

            if len(self.zip_filename) == 0:
                print("尚未检测出任何小米日志文件。")

    def unzip_xiaomi_log(self, filename: str) -> list | None:
        """
        递归解压小米日志压缩包。
        :return: list[str] | None
        """
        if not filename.startswith("bugreport") and not filename.endswith(".zip"):
            print("未检测出小米日志。")
            return None

        print("解压程序初始化...")
        try:
            step = 1
            current_file = filename
            while True:
                print(f"开始解压流程{step}..")
                with zipfile.ZipFile(file=current_file, mode='r') as zip_ref:
                    zip_ref.extractall(self.tmp)
                    file_list = zip_ref.namelist()

                print(f"流程{step}:开始查找目标压缩文件")
                nested_zip = None
                for file in file_list:
                    if file.startswith("bugreport") and file.endswith(".zip"):
                        nested_zip = os.path.join(self.tmp, file)
                        break

                if nested_zip:
                    print(f"流程{step}:找到嵌套压缩文件{nested_zip}, 解压流程继续")
                    current_file = nested_zip
                    step += 1
                else:
                    print(f"流程{step}: 未找到嵌套压缩文件, 解压程序结束, 将返回该目录下的文件路径.")
                    return file_list

        except zipfile.BadZipfile as e:
            print("发生错误:" % e.strerror)
            self.delete()
            return None

    def find_xiaomi_log(self, filelist: list) -> True | False:
        for file in filelist:
            if file.startswith("bugreport") and file.endswith(".txt"):
                self.filename = file  # 下一个方法可以直接调用, 免去再次赋值的问题
                dst_path = os.path.join(".", file)
                path = os.path.join(self.tmp, file)
                if os.path.exists(dst_path):
                    src_mtime = time.localtime(os.path.getmtime(dst_path))
                    src_mtime = time.strftime('%Y-%m-%d %H:%M:%S', src_mtime)

                    dst_mtime = time.localtime(os.path.getmtime(path))
                    dst_mtime = time.strftime('%Y-%m-%d %H:%M:%S', dst_mtime)

                    print(f"原文件修改日期:{src_mtime}")
                    print(f"新文件修改日期:{dst_mtime}")
                    answer = input("文件已存在。是否覆盖原文件[y/n]？").lower()
                    if answer == "y":
                        os.remove(path=dst_path)
                        shutil.move(src=path, dst=".")
                    elif answer == "n":
                        print("原文件已保留。")
                    else:
                        print("输入错误，操作已终止。")
                else:
                    shutil.move(src=path, dst=".")
                    print("日志已找到并解压到当前目录中。")

                self.delete()
                return True

        print("未找到与电池相关的日志文件。")
        return False

    def search_battery_info(self) -> dict | None:
        if not self.filename.endswith(".txt"):
            print("错误的日志文件。")
            return None

        with open(file=self.filename, mode="r", encoding="utf-8") as file:
            content = file.read()

        battery_info = {}

        match_estimated_battery_c = re.search(pattern=r"Estimated battery capacity: (\d+)\s*mAh", string=content)
        if match_estimated_battery_c:
            battery_info["估计电池容量"] = float(match_estimated_battery_c.group(1))

        match_last_learned_battery_c = re.search(pattern=r"Last learned battery capacity: (\d+)\s*mAh", string=content)
        if match_last_learned_battery_c:
            battery_info["最近学习到的电池容量"] = float(match_last_learned_battery_c.group(1))

        match_min_learned_battery_c = re.search(pattern=r"Min learned battery capacity: (\d+)\s*mAh", string=content)
        if match_min_learned_battery_c:
            battery_info["最小学习到的电池容量"] = float(match_min_learned_battery_c.group(1))

        match_battery_time = re.search(pattern=r"Battery time remaining: \s*([\w\s]+ms)", string=content)
        if match_battery_time:
            battery_info["电池剩余可用时间"] = match_battery_time.group(1)

        return battery_info

    def mainly_process(self):
        def date_process(fd_str: str):
            dif_time = fd_str.split("-")
            year = dif_time[0]
            month = dif_time[1]
            day = dif_time[2]
            hour = dif_time[3]
            minute = dif_time[4]
            second = dif_time[5]
            return f"{year}年{month}月{day}日 {hour}:{minute}:{second}"

        self.detect_whether_include_xm_log()
        for file in self.zip_filename:
            fl = self.unzip_xiaomi_log(filename=file)
            if fl is not None:
                self.find_xiaomi_log(filelist=fl)
                filedate = self.filename.split("-", 3)[-1].rsplit(".")[0]
                date_str = date_process(filedate)
                info = self.search_battery_info()
            else:
                continue
            if info:
                print(f"电池信息：{date_str}")
                for key, value in info.items():
                    print(f"{key}: {value} mAh" if "容量" in key else f"{key}: {value}")
            else:
                print("电池信息为空。")


if __name__ == '__main__':
    f = BatteryInfo()
    f.mainly_process()

########################
# chime.py
#
# 2021/02/13
# Author: 電子ひつじ
########################

import argparse
import sched
import time

import vlc

parser = argparse.ArgumentParser()
parser.add_argument("--setting_txt_name", type = str, default = "setting.txt", help = "設定ファイル名を入力（デフォルト：setting.txt）")

def load_setting_txt(setting_txt_name):
    work_interval = []
    break_interval = []
    with open(setting_txt_name, "r") as f:
        lines = f.read().splitlines()
        sound_path = lines[1].split(",")[1]
        for line in lines[2:]:
            data = line.split(",")
            if data[0] == "Work":
                work_interval.append(int(data[1])*60) #min->sec
            elif data[0] == "Break":
                break_interval.append(int(data[1])*60) #min->sec

    return {"Sound path": sound_path,
            "Work": work_interval,
            "Break":break_interval,}

class Chime:
    end_of_work = 0
    end_of_break = 1
    def __init__(self, setting_data):
        self.chime_data = load_setting_txt(setting_data)
        self.sound_path = self.chime_data["Sound path"]
        self.round_work = len(self.chime_data["Work"])
        self.round_break = len(self.chime_data["Break"])

        #txtの各インターバル時間を開始時間から何分後に開始するかに変換
        total_time = 0
        for i in range(self.round_break):
            total_time += self.chime_data["Work"][i]
            self.chime_data["Work"][i] = total_time
            total_time += self.chime_data["Break"][i]
            self.chime_data["Break"][i] = total_time
        total_time += self.chime_data["Work"][self.round_work-1]
        self.chime_data["Work"][self.round_work-1] = total_time

    def run_chime(self):
        input("何かを入力したらチャイムが開始します。")
        self.scheduler = sched.scheduler(time.time, time.sleep)
        for i in range(self.round_break):
            self.scheduler.enter(self.chime_data["Work"][i], 1, self._chime_end_of_work)
            self.scheduler.enter(self.chime_data["Break"][i], 1, self._chime_end_of_break)
        self.scheduler.enter(self.chime_data["Work"][self.round_work-1], 1, self._chime_end_of_work)
        print("スタート!")
        self.scheduler.run()
        time.sleep(1.0)
        print("お疲れ様でした！")
        time.sleep(1.0)

    def _chime_end_of_work(self):
        print("休憩！")
        chime_sound = vlc.MediaPlayer(self.sound_path)
        chime_sound.play()

    def _chime_end_of_break(self):
        print("仕事に戻る！")
        chime_sound = vlc.MediaPlayer(self.sound_path)
        chime_sound.play()


if __name__ == "__main__":
    args = parser.parse_args()
    chime = Chime(args.setting_txt_name)
    chime.run_chime()
    input("何かを入力してプログラム終了")

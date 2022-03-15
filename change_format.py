import pandas as pd
from tkinter import *
from tkinter import ttk
from PIL import ImageTk,Image

class Reformatting():
    def __init__(self,ori_dic,filename,first_img):
        self.ori_dic = ori_dic
        self.temp_dic = {"time":[],"bpm":[]}
        self.filename = filename
        self.first_img =  first_img
    

    def find_initial_time(self):
        win = Tk ()
        win.title("기준 시간 입력")
        win.geometry('1300x1000+500+500')

        fir_img = Image.fromarray(self.first_img)
        img = ImageTk.PhotoImage(fir_img)
        label = Label(image=img)
        label.grid(column = 0 , row = 0)
        def clickMe():
            input_text = str.get()
            if len(input_text) != 12:
                pass
            else:
                self.initial_time = input_text
                win.destroy()
        str = StringVar()
        textbox = ttk.Entry(win, width=20, textvariable=str)
        textbox.grid(column = 0 , row = 1)
        action=ttk.Button(win, text="입력", command=clickMe)
        action.grid(column=0, row=2)
        win.mainloop()


     # 소요시간은 시간 데이터 형식으로 변경
    def result_time(self, addtime):
        initial_time = self.initial_time

        ini_time_split = initial_time.split(":")
        int_ini_time_list = [int(x) for x in ini_time_split]
        addtime_split = addtime.split(".")
        int_addtime_list = [int(x) for x in addtime_split]
        int_ini_time_list[-1] += int_addtime_list[-1]
        int_ini_time_list[-2] += int_addtime_list[0]
        if int_ini_time_list[-1] >=1000:
            int_ini_time_list[-2] += 1
            int_ini_time_list[-1] -= 1000
        if int_ini_time_list[-2] >=60:
            int_ini_time_list[-3] += 1
            int_ini_time_list[-2] -= 60
        if int_ini_time_list[-3] >=60:
            int_ini_time_list[-4] += 1
            int_ini_time_list[-3] -= 60
        
        int_ini_time_list = [str(x) for x in int_ini_time_list]
        if len(int_ini_time_list[-1]) == 2:
            int_ini_time_list[-1] = "0" + int_ini_time_list[-1]
        if len(int_ini_time_list[-2]) == 1:
            int_ini_time_list[-2] = "0" + int_ini_time_list[-2]

        return ":".join(int_ini_time_list)


    # 소요시간 데이터를 읽어 dic에 저장
    def duration_to_time(self):
        for i in range(len(self.ori_dic["time"])):
            round_duration = self.ori_dic["time"][i].strip().split(".")[0]
            round_duration = round_duration[:-3]+"."+round_duration[-3:]
            time = self.result_time(round_duration)
            self.temp_dic["time"].append(time)
            self.temp_dic["bpm"].append(self.ori_dic["bpm"][i])


    ## 0.5초 간격으로 평균 구하기   
    def mk_avg_result(self):
        result = {"time":[],"bpm":[]}
        check = -1
        temp = []
        for i in range(len(self.temp_dic["time"])):
            ms = int(self.temp_dic["time"][i][9:10])
            if check == -1:
                default_format = self.temp_dic["time"][i][:9]
                if ms <5:
                    check = False
                else:
                    check = True
            if ms < 5:
                if check == True:
                    current_time = default_format + "5"
                    avg = sum(temp)/len(temp)
                    temp = []
                    result["time"].append(current_time)
                    result["bpm"].append(avg)
                    check = False
                    default_format = self.temp_dic["time"][i][:9]
                temp.append(float(self.temp_dic["bpm"][i]))
            else:
                if check == False:
                    current_time = default_format + "0"
                    avg = sum(temp)/len(temp)
                    temp = []
                    result["time"].append(current_time)
                    result["bpm"].append(avg)
                    check = True
                    default_format = self.temp_dic["time"][i][:9]
                temp.append(float(self.temp_dic["bpm"][i]))
        return result


    def main(self):
        self.find_initial_time()
        self.duration_to_time()
        result_pd = pd.DataFrame(self.mk_avg_result())
        result_pd.to_csv("[python]"+self.filename+".csv",encoding="cp949")


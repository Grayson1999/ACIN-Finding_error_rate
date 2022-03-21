import pandas as pd
from tkinter import *
from tkinter import ttk
from PIL import ImageTk,Image
import os
import cv2
os.environ['KMP_DUPLICATE_LIB_OK']='True'

class Cppformatting():
    def __init__(self,folder_index=-1):
        self.folder_index = folder_index
        self.temp_dic = {"time":[],"bpm":[]}
        #path 변수
        temp_path = self.find_file_pathNname()
        self.folder_input_path = temp_path[0]+"/input/"
        self.folder_output_path = temp_path[0]+"/output/"
        self.file_name = temp_path[1]
        self.file_path = self.folder_input_path+self.file_name
        self.video_name = self.file_name[5:-4]+".mp4"
        #기준 시간 변수
        self.initial_time = ""
        self.find_initial_time()
        
    ##path 찾기
    def find_file_pathNname(self):
        path_dir = './Data/'
        ## 데이터 파일 중 마지막 폴더 이름 가져오기(폴더 선택)
        folder_name = os.listdir(path_dir)[-1]
        ##cpp csv파일 찾기
        file_path = path_dir+folder_name
        file_names = os.listdir(file_path+"/input/")
        file_name = ""
        for name in file_names:
            if name[1:4] == "cpp" and name[-3:] == "csv":
                file_name = name
                return (file_path,file_name)
        if file_name == "":## 파일이 없을 경우
            raise Cannotfoundfile
    
    
    def find_initial_time(self):
        ## find first img
        cap = cv2.VideoCapture(self.folder_input_path+self.video_name)
        first_img = cap.read()[1]
        first_img = cv2.rotate(first_img, cv2.ROTATE_180)
        first_img = cv2.resize(first_img, dsize=(800, 480), interpolation=cv2.INTER_AREA)
        
        #기준시간 입력 gui
        win = Tk ()
        win.title("기준 시간 입력")
        win.geometry('810x700+300+300')
        fir_img = Image.fromarray(first_img)
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
        textbox = ttk.Entry(win, width=40, textvariable=str)
        textbox.grid(column = 0 , row = 1)
        action=ttk.Button(win, text="입력", command=clickMe)
        action.grid(column=0, row=2)
        win.mainloop()
        
    # 소요시간 데이터를 읽어 dic에 저장
    def formatting(self):
         # 소요시간은 시간 데이터 형식으로 변경
        def result_time(addtime):
            initial_time = fm.initial_time

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
        
        f = open(self.file_path,"r")
        line = f.readline()# 첫번째 특징 부분 버리기
        while True:
            line = f.readline()
            if not line: break
            
            duration_time = line.split(";")[0]
            duration_time = duration_time[:-3]+"."+duration_time[-3:]
            self.temp_dic["time"].append(result_time(duration_time))
            self.temp_dic["bpm"].append(float(line.split(";")[-1]))
        f.close()
        
        
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
        self.formatting()
        result_pd = pd.DataFrame(self.mk_avg_result())
        result_pd.to_csv(self.folder_output_path+self.file_name,encoding="cp949")

fm = Cppformatting()
fm.main()
from tkinter import *
from tkinter import ttk
from PIL import ImageTk,Image
import os
import cv2
import pandas as pd
os.environ['KMP_DUPLICATE_LIB_OK']='True'# 충돌 해결 코드
import argparse

class Formatting():
    def __init__(self):
        pass

    ##path 찾기
    def find_file_pathNname(self, classification_name, extension):
        path_dir = './Data/'
        list_path = os.listdir(path_dir)
        ## 데이터 파일 중 폴더 이름 가져오기(폴더 선택)
        for index in range(len(list_path)): 
            print(f"[{index}] {list_path[index]}",end=" ")
        print()
        while(1):
            user_index = int(input("select index: "))
            if user_index < len(list_path):
                break
        folder_name = list_path[user_index]
        ##cpp csv파일 찾기
        file_path = path_dir+folder_name
        file_names = os.listdir(file_path+"/input/")
        file_name = ""
        for name in file_names:
            if name.find(classification_name) != -1  and name[-3:] == extension:
                file_name = name
                return (file_path,file_name)
        if file_name == "":## 파일이 없을 경우
            raise Exception("Cannotfoundfile")
    
    ## 첫 프레임 이미지를 통해 기준시간 저장
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


    ## 소요시간은 시간 데이터 형식으로 변경
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


    ## 소요시간 데이터를 읽어 dic에 저장
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


class Cppformatting(Formatting):
    def __init__(self,folder_index=-1):
        print("--cpp 변환--")
        self.folder_index = folder_index
        self.temp_dic = {"time":[],"bpm":[]}
        #path 변수
        temp_path = self.find_file_pathNname("cpp","csv")
        self.folder_input_path = temp_path[0]+"/input/"
        self.folder_output_path = temp_path[0]+"/output/"
        self.file_name = temp_path[1]
        self.file_path = self.folder_input_path+self.file_name
        self.video_name = self.file_name[5:-4]+".mp4"
        #기준 시간 변수
        self.initial_time = ""
        self.find_initial_time()
    
    ## 첫 프레임 이미지를 통해 기준시간 저장
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
    
    
    def main(self):
        self.formatting()
        result_pd = pd.DataFrame(self.mk_avg_result())
        result_pd.to_csv(self.folder_output_path+self.file_name,encoding="cp949")


class Pyformatting(Formatting):
    def __init__(self,ori_dic,filename,first_img):
        self.ori_dic = ori_dic
        self.temp_dic = {"time":[],"bpm":[]}
        self.filename = filename
        self.first_img =  first_img

    def main(self):
        self.find_initial_time()
        self.duration_to_time()
        result_pd = pd.DataFrame(self.mk_avg_result())
        result_pd.to_csv("[python]"+self.filename+".csv",encoding="cp949")


class Arduino_formatting(Formatting):
    def __init__(self):
        print("--Arduino 변환--")
        self.temp_dic = {"time":[],"bpm":[]}
        temp_dir = self.find_file_pathNname("Arduino","txt")
        self.file_path = temp_dir[0]
        self.file_name = temp_dir[1]
        f = open(self.file_path+"/input/"+self.file_name,"r")
        self.initial_time = ":".join(f.readline().strip().split("/")[1].split(":")[1:]).strip()
        
        #파일을 읽어 dictionary로 저장
        while True:
            line = f.readline().strip()
            if not line:
                break
            f_bpm = line.split("/")[0].split(":")[1].strip()
            f_time = ":".join(line.split("/")[1].split(":")[1:]).strip()    
            self.temp_dic["bpm"].append(f_bpm)
            self.temp_dic["time"].append(f_time)


    def main(self):
        result_pd = pd.DataFrame(self.mk_avg_result())
        result_pd.to_csv(self.file_path+"/output/"+self.file_name+".csv",encoding="cp949")


def main():
    parser = argparse.ArgumentParser(description="변경하고자 하는 모듈을 선택한다. \n옵션을 제외한 인자는 받지 않는다.\n\tex) change_format.py -a")
    parser.add_argument('-c','-cpp', help="cpp 모듈의 결과를 변경.", action="store_true")
    parser.add_argument('-a','-ad','-arduino', help="arduino 모듈의 결과를 변경.", action="store_true")
    args = parser.parse_args()

    if args.a:
        ad = Arduino_formatting()
        ad.main()

    if args.c:
        cpp = Cppformatting()
        cpp.main()

main()
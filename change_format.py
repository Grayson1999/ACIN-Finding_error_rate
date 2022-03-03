from unittest import result
import pandas as pd
import numpy as np
import os

path_dir = 'C:/Users/kgg/Desktop/lab/heart-rate/ACIN-Finding_error_rate/Data/'
## 데이터 파일 중 마지막 폴더 이름 가져오기(폴더 선택)
last_file_name = os.listdir(path_dir)[-1]
filename = "[python]"+last_file_name+"_face_180"
#C:\Users\kgg\Desktop\lab\heart-rate\ACIN-Finding_error_rate\Data\DataSet_2\input\[python]DataSet_2_face_180.txt
f = open(path_dir+last_file_name+"/input/"+filename+".txt", "r")

dic = {"time":[],"bpm":[]}

##0.0초 때의 시간을 입력받음
# initial_time = input()
initial_time = "17:14:25:262"
# 소요시간은 시간 데이터 형식으로 변경
def result_time(addtime,initial_time = initial_time):
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

    return ":".join(int_ini_time_list)



# 소요시간 데이터를 읽어 dic에 저장
while(True):
    lines = f.readline()
    if not lines:
        break
    lines = lines.split(",")
    lines[-1] = lines[-1].strip().split(".")[0]
    lines[-1] = lines[-1][:-3]+"."+lines[-1][-3:]
    time = result_time(lines[-1])
    dic["time"].append(time)
    dic["bpm"].append(lines[1])


## 0.5초 간격으로 평균 구하기   
def mk_avg_result(initial_result):
    result = {"time":[],"bpm":[]}
    check = -1
    temp = []
    for i in range(len(initial_result["time"])):
        ms = int(initial_result["time"][i][9:10])
        if check == -1:
            default_format = initial_result["time"][i][:9]
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
                default_format = initial_result["time"][i][:9]
            temp.append(float(initial_result["bpm"][i]))
        else:
            if check == False:
                current_time = default_format + "0"
                avg = sum(temp)/len(temp)
                temp = []
                result["time"].append(current_time)
                result["bpm"].append(avg)
                check = True
                default_format = initial_result["time"][i][:9]
            temp.append(float(initial_result["bpm"][i]))
    return result
                
                
    
   

result_pd = pd.DataFrame(mk_avg_result(dic))
result_pd.to_csv(path_dir+last_file_name+"/output/"+filename+".csv",encoding="cp949")

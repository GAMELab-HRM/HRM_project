import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import random, glob, datetime, argparse, os
from utils import draw_all

# configuration
label = ['normal', 'IEM', 'Absent', 'Fragmented']
label_dict = {"normal":[],"IEM":[],"Absent":[],"Fragmented":[]}
file_dict = {"normal":[],"IEM":[],"Absent":[],"Fragmented":[]}
swallow_dict = {} # {"ID":["Normal","Normal"......]}
type_template = {
    "normal":['Normal', 'Normal', 'Normal', 'Normal', 'Normal', 'Normal', 'Normal', 'Normal', 'Normal', 'Normal'],
    "IEM":['Failed', 'Weak', 'Weak', 'Weak', 'Weak', 'Failed', 'Failed', 'Failed', 'Weak', 'Failed'],
    "absent":['Failed', 'Failed', 'Failed', 'Failed', 'Failed', 'Failed', 'Failed', 'Failed', 'Failed', 'Failed']
}
count = 0
# parser 
def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', type=int, default='10')
    
    return parser

def read_data(filename, true_label):
    df = pd.read_csv(filename, encoding='big5')
    ans = list(np.where(df['檢查流程']!='None')[0])
    swallow_status = [df.iloc[ans[i]]['Contraction vigor'] for i in range(len(ans))][:-1]
    label_dict[true_label].append(swallow_status)
    swallow_dict[filename] = swallow_status

def get_swallow_range(df):
    swallow_names = ["Wet swallow"+str(i+1) for i in range(10)]
    swallow_index = []
    swallow_range = []
    ans = list(np.where(df['檢查流程']!='None')[0])
    for i in range(len(ans)):
        test_name = df.iloc[ans[i]]['檢查流程'] # test_name ==> 檢測的名稱
        if 'Wet swallow10' == test_name:
            swallow_index.append(ans[i])
            swallow_index.append(len(df)-1)
            continue 
        if test_name in swallow_names:
            swallow_index.append(ans[i])
    for i in range(len(swallow_index)-1):
        swallow_range.append([swallow_index[i],swallow_index[i+1]-1])
    swallow_status = [df.iloc[ans[i]]['Contraction vigor'] for i in range(len(ans))][:-1]
    return swallow_range, np.array(swallow_status)

def create_data(label):
    global count 
    datetime_dt = datetime.datetime.today()          # 獲得當地時間
    datetime_str = datetime_dt.strftime("%Y%m%d%H%M%S")  # 格式化日期
    print("[INFO] Create "+datetime_str+str(count)+'-'+label+'.CSV')

    type_number = len(file_dict[label])
    print('type number',type_number)
    df_list = []
    # 隨機挑選10次swallow
    i = 0
    while i<10:
        file_randn = random.randint(0,type_number-1)
        fname = file_dict[label][file_randn]
        
        target_stype = type_template[label][i] # Normal Failed Weak..... (swallow type )
        df = pd.read_csv(fname, encoding='big5')
        ans = list(np.where(df['檢查流程']!='None')[0])[:-1]
        swallow_range, swallow_status = get_swallow_range(df)
        type_list = np.where(swallow_status==target_stype)[0]

        if len(type_list) == 0:
            continue

        swallow_randn = random.randint(0, len(type_list)-1)
        target_swallow_index = type_list[swallow_randn]
        print('swallow'+str(i+1)+':\t'+"|From "+fname+"\t"+"swallow"+str(target_swallow_index+1)+"\t")
        
        target_swallow = swallow_range[target_swallow_index]
        df_list.append(df.iloc[target_swallow[0]:target_swallow[1]+1])
        i+=1


    res = pd.concat(df_list)
    res.to_csv(os.path.join('augmentation2',datetime_str+str(count)+'-'+label+'.CSV'), encoding='big5')
    print(count)
    count+=1
def draw():
    res = glob.glob('./augmentation2/*.csv')
    for r in res:
        df = pd.read_csv(r, encoding='big5')
        sensors = [' P' + str(i) for i in range(1,21)] # 22個sensor p1~p22
        print(r)
        draw_all(df, r, sensors)

if __name__ == "__main__":
    if not os.path.exists('augmentation2'):
        os.makedirs('augmentation2')
        print("[INFO] Create augmentation2 folder")

    res = glob.glob('./train/*.CSV')
    parser = get_parser()
    args = parser.parse_args()
    number = args.number
    
    for r in res:
        print(r)
        file_label = r.split('-')[1][:-4]
        file_dict[file_label].append(r)
        read_data(r, file_label)
    
    # Create fake HRM data 
    for i in range(number):
        create_data('normal')
        print("\n")
        create_data('IEM')
        print("\n")

    print("[INFO] Start drawing HRM curve")
    #draw()




import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 
import os 
import matplotlib.colors as mccolors 

hex_list = ["#0000ff","#00ffff","00ff00","#96f97b","ffff00","#f97306","#e50000","800000","#580f41","#490648"]

def hex_to_rgb(value):
    value = value.strip("#")
    lv = len(value)
    return tuple(int(value[i:i+lv//3],16) for i in range(0,lv,lv//3))

def rgb_to_dec(value):
    return [v/256 for v in value]

def get_continous_cmap(hex_list, float_list=None):
    rgb_list = [rgb_to_dec(hex_to_rgb(i)) for i in hex_list]
    if float_list:
        pass
    else:
        float_list = list(np.linspace(0,1,len(rgb_list)))

    cdict = dict()
    for num, col in enumerate(["red","green","blue"]):
        col_list = [[float_list[i],rgb_list[i][num],rgb_list[i][num]] for i in range(len(float_list))]
        cdict[col] = col_list
    cmp = mccolors.LinearSegmentedColormap("my_cmp",segmentdata=cdict,N=256)
    return cmp 

def draw(swallos):
    # [swallos variable] contains 10 times swallow of patient
    custom_cmap = get_continous_cmap(hex_list)
    for i in range(len(swallos)):
        data_number, sensor_number = swallos[i].shape
        y = [t for t in reversed(range(sensor_number))]
        x = [t for t in range(data_number)]
        values = []
        for j in y:
            temp = []
            for k in x:
                temp.append(swallos[i][k][j])
            values.append(temp)
        values = np.array(values)
        fig, ax = plt.subplots()
        levels = np.linspace(-30, 280, 400) # pressure lower & upper bound
        contourf = ax.contourf(x,y,values,levels=levels,cmap=custom_cmap)
        cbar = fig.colorbar(contourf)
        plt.ylabel("sensor")
        plt.xlabel("sample number")
        plt.yticks([])
        plt.title("Swallow " + str(i+1))
        plt.show()
        

    return 0 
def create_csv(dataframe, swallow_index, filename, sensors):
    sensors.append('檢查流程')
    dataframe = dataframe[swallow_index[0]:swallow_index[len(swallow_index)-1]+1][sensors]
    dataframe.to_csv(os.path.join('train',filename[13:]), encoding='big5')

def preprocess(filepath):
    sensors = [' P' + str(i) for i in range(1,23)] # 22個sensor p1~p22
    filename = filepath
    swallow_range = []
    swallows = [] # 存放這個病患的10次 wet swallow

    df = pd.read_csv(filename, encoding= 'big5', skiprows=6)
    df['檢查流程'] = df['檢查流程'].fillna(0) # csv檔空格通通填0

    ans = list(np.where(df['檢查流程']!=0)[0]) # 找出有檢測發生的index
    swallow_index = []
    for i in range(len(ans)):
        test_name = df.iloc[ans[i]]['檢查流程'] # test_name ==> 檢測的名稱
        if 'Wet swallow10' in test_name:
            swallow_index.append(ans[i])
            swallow_index.append(ans[i+1])
            continue 
        if 'Wet swallow' in test_name:
            swallow_index.append(ans[i])

    for i in range(len(swallow_index)-1):
        swallow_range.append([swallow_index[i],swallow_index[i+1]-1])

    for i in range(10):
        swallow_data = df[swallow_range[i][0]:swallow_range[i][1]+1][sensors]
        swallows.append(swallow_data.values)
    # 建立新格式的csv file(去除一些沒用的資訊)
    create_csv(df, swallow_index, filename, sensors)
    

# 將指定檔案的10次swallow轉換成np.array
def get_wet_swallow(filename):
    pass 
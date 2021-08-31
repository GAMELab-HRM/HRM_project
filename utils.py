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

def draw_all(df, filename, sensors):
    custom_cmap = get_continous_cmap(hex_list)
    levels = np.linspace(-15, 150, 400)

    hrm = df[:][sensors].values 

    data_number, sensor_number = hrm.shape 
    y = [t for t in reversed(range(sensor_number))]
    x = [t for t in range(data_number)]
    values = []
    for j in y:
        temp = []
        for k in x:
            temp.append(hrm[k][j])
        values.append(temp)
    values = np.array(values)
    plt.contourf(x,y,values,levels=levels,cmap=custom_cmap)
    plt.yticks([])
    plt.colorbar()
    plt.title(filename)
    plt.show()

def draw_wet_swallows(filename):
    df = pd.read_csv(filename, encoding='big5')
    sensors = [' P' + str(i) for i in range(1,21)] # 22個sensor p1~p22
    swallows = []
    swallow_range = []
    ans = list(np.where(df['檢查流程']!='None')[0]) # 找出有檢測發生的index
    swallow_index = []

    for i in range(len(ans)):
        test_name = df.iloc[ans[i]]['檢查流程'] # test_name ==> 檢測的名稱
        if 'Wet swallow10' in test_name:
            swallow_index.append(ans[i])
            swallow_index.append(len(df)-1)
            continue 
        if 'Wet swallow' in test_name:
            swallow_index.append(ans[i])
    #print(df.iloc[swallow_index])
    for i in range(len(swallow_index)-1):
        swallow_range.append([swallow_index[i],swallow_index[i+1]-1])

    for i in range(10):
        swallow_data = df[swallow_range[i][0]:swallow_range[i][1]+1][sensors]
        swallows.append(swallow_data.values)

    # draw 10 swallos in one figure 
    custom_cmap = get_continous_cmap(hex_list)

    show_data = []
    for i in range(len(swallows)):
        data_number, sensor_number = swallows[i].shape
        y = [t for t in reversed(range(sensor_number))]
        x = [t for t in range(data_number)]
        values = []
        for j in y:
            temp = []
            for k in x:
                temp.append(swallows[i][k][j])
            values.append(temp)
        values = np.array(values)
        show_data.append({"x":x, "y":y, "values":values})
        
    # draw 10 swallows in one figure 
    fig = plt.figure(figsize=(15,15))
    for i in range(10):
        fig.add_subplot(2, 5, i+1)
        levels = np.linspace(-15, 150, 400) # pressure lower & upper bound
        plt.suptitle(filename)
        plt.contourf(show_data[i]['x'],show_data[i]['y'],show_data[i]['values'],levels=levels,cmap=custom_cmap)
        plt.colorbar()
        plt.yticks([])
        plt.title('swallow'+str(i+1))
    plt.show()

def create_csv(df_list, filename):
    res = pd.concat(df_list)
    res.to_csv(os.path.join('train',filename[18:]), encoding='big5')

def preprocess(filepath, swallow_size):
    sensors = [' P' + str(i) for i in range(1,21)] # 22個sensor p1~p22
    filename = filepath
    swallow_names = ["Wet swallow"+str(i+1) for i in range(10)]
    df = pd.read_csv(filename, encoding= 'big5', skiprows=6)
    df['檢查流程'] = df['檢查流程'].fillna('None') # csv檔空格通通填0
    ans = list(np.where(df['檢查流程']!='None')[0]) # 找出有檢測發生的index
    swallow_index = []

    for i in range(len(ans)):
        test_name = df.iloc[ans[i]]['檢查流程'] # test_name ==> 檢測的名稱
        if 'Wet swallow10' == test_name:
            swallow_index.append(ans[i])
            swallow_index.append(ans[i+1])
            continue 
        if test_name in swallow_names:
            swallow_index.append(ans[i])

    min_bound = -15 
    max_bound = 150 
    for s in sensors:
        df.loc[df[s] > max_bound, s] = max_bound
        df.loc[df[s] < min_bound, s] = min_bound

    sensors.append('檢查流程')
    sensors.append('Contraction vigor')
    sensors.append('Contraction pattern')

    df_list = []
    for i in range(10):
        s_size = swallow_index[i+1] - swallow_index[i]
        temp = np.linspace(swallow_index[i], swallow_index[i+1] - 1, swallow_size[i], dtype='int')
        df_list.append(df.iloc[temp][sensors])

    # 建立新格式的csv file(去除一些沒用的資訊)
    create_csv(df_list, filename)

    
def compute_swallow_size(files):
    swallow_size = [[] for i in range(10)]
    swallow_names = ["Wet swallow"+str(i+1) for i in range(10)]

    for f in files:
        df = pd.read_csv(f, encoding= 'big5', skiprows=6)
        df['檢查流程'] = df['檢查流程'].fillna('None') # csv檔空格通通填0
        ans = list(np.where(df['檢查流程']!='None')[0]) # 找出有檢測發生的index
        swallow_index = []
        
        for i in range(len(ans)):
            test_name = df.iloc[ans[i]]['檢查流程'] # test_name ==> 檢測的名稱
            if 'Wet swallow10' == test_name:
                swallow_index.append(ans[i])
                swallow_index.append(ans[i+1])
                continue 
            if test_name in swallow_names:
                swallow_index.append(ans[i])
        # 計算每個swallow的長度
        for i in range(len(swallow_index)-1):
            swallow_size[i].append(swallow_index[i+1] - swallow_index[i])

    return [min(i) for i in swallow_size]
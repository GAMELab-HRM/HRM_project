import argparse
import pandas as pd
import glob
import os
from utils import draw_all


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--times', type=int, default='3')
    parser.add_argument('-s', '--stride', type=int, default='10')
    
    return parser


def check_min_rest(path_lst, times, stride):
    min_rest = -1
    for path in path_lst:
        df = pd.read_csv(path, encoding= 'big5', skiprows=6, low_memory=False)
        rest_num = df.loc[df['檢查流程']=='Wet swallow1'].index.tolist()[0]
        rest_num -= 1            # Wet swallow1 那行不計入rest time
        if rest_num < min_rest or min_rest < 0:
            min_rest = rest_num
    
    if times * stride > min_rest:
        print('指定的次數與步長超過rest time的資料數量，兩者乘積需小於 : {}'.format(min_rest))
        exit(0)


def data_transfer(path):
    remain_col = [' P' + str(i) for i in range(1,21)]
    remain_col.append('檢查流程')

    df = pd.read_csv(path, encoding= 'big5', skiprows=6, low_memory=False)
    df['檢查流程'].fillna('None', inplace=True)
    wet_swallow_10_idx = df.loc[df['檢查流程']=='Wet swallow10'].index.tolist()[0]
    temp_df = df.loc[wet_swallow_10_idx+1:, '檢查流程']
    next_test_idx = temp_df[temp_df != 'None'].index.tolist()[0]
    df = df.loc[:next_test_idx, remain_col]

    return df

def data_argumentation(path_lst, times, stride):
    argumentation_df_lst = []
    for path in path_lst:
        df = data_transfer(path)
        start_idx = df.loc[df['檢查流程']=='Wet swallow1'].index.tolist()[0]
        end_idx = df.shape[0]

        temp = []
        for _ in range(times):
            start_idx -= stride
            end_idx -= stride
            temp.append(df.iloc[start_idx:end_idx, :])
        argumentation_df_lst.append(temp)
    
    return argumentation_df_lst


def output(df_lst, name_lst):
    if not os.path.exists('data augmentation'):
        os.makedirs('data augmentation')
        print("[INFO] Create data augmentation folder")

    for i in range(len(df_lst)):
        for j in range(len(df_lst[i])):
            file_name = name_lst[i].split('.')
            file_name[0] += '_arg'+str(j)
            file_name = '.'.join(file_name)
            
            df_lst[i][j].to_csv(os.path.join('data augmentation', file_name), encoding='big5')
            print("[INFO] output {} successfully".format(file_name))



def draw():
    res = glob.glob('./data augmentation/*.csv')
    for r in res:
        df = pd.read_csv(r, encoding='big5')
        sensors = [' P' + str(i) for i in range(1,21)] # 22個sensor p1~p22
        print(r)
        draw_all(df, r, sensors)
        #draw_wet_swallows(r)



if __name__ == '__main__':
    """
    parser = get_parser()
    args = parser.parse_args()
    times = args.times
    stride = args.stride

    path_lst = glob.glob('./data/*/*.CSV')
    check_min_rest(path_lst, times, stride)
    argumentation_df_lst = data_argumentation(path_lst, times, stride)
    name_lst = [i.split('\\')[-1] for i in path_lst]
    output(argumentation_df_lst, name_lst)
    """
    draw()
    
        




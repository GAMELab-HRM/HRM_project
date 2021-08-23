import glob 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
label = ['normal', 'IEM', 'Absent', 'Fragmented']
label_dict = {"normal":[],"IEM":[],"Absent":[],"Fragmented":[]}

def read_data(filename, true_label):
    df = pd.read_csv(filename, encoding='big5')
    ans = list(np.where(df['檢查流程']!='None')[0])
    print(filename, true_label)
    # print(ans, len(ans))
    print(df.iloc[ans])
    swallow_status = [df.iloc[ans[i]]['Contraction vigor'] for i in range(len(ans))][:-1]
    # test_names = [df.iloc[ans[i]]["檢查流程"] for i in range(len(ans))][:-1]
    label_dict[true_label].append(swallow_status)
    print(swallow_status)
    

res = glob.glob('./train/*.csv')

for r in res:
    file_label = r.split('-')[1][:-4]
    read_data(r, file_label)



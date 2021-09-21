import pandas as pd
import argparse
import random
from transfer import output
from datetime import datetime
import numpy as np


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quantity', type=int, required=True, help='how much fake data to make')
    parser.add_argument('-d', '--dl', action='store_true', required=True, help='if distal latency is in all_patient')

    return parser


def score(df_data_lst):
    transfer_lst = []
    scoring_result = []
    for i in df_data_lst:
        temp_lst = []
        vigor = i[:10]
        pattern = i[10:20]
        for j in range(len(vigor)):
            if pattern[j] == 'Intact':
                temp_lst.append(vigor[j])
            else:
                temp_lst.append(pattern[j])
        transfer_lst.append(temp_lst)

    for i in transfer_lst:
        normal = i.count('Normal')/10
        weak = i.count('Weak')/10
        failed = i.count('Failed')/10
        premature = i.count('Premature')/10
        fragmented = i.count('Fragmented')/10

        ineffective = weak+failed

        # 0 for Hyper
        scoring_result.append([normal, ineffective, failed, premature, 0, fragmented])

    for i in range(len(df_data_lst)):
        df_data_lst[i].extend(scoring_result[i])
    
    return df_data_lst


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    quantity = args.quantity
    if_dl = args.dl
    
    df = pd.read_csv('./data/all_patient.csv', encoding='big5', low_memory=False)
    df.drop('ID', axis=1, inplace=True)
    swallow_ct = int(df.shape[0])*10
    aug_idx_lst = []

    for i in range(quantity):
        aug_idx_lst.append(random.sample(range(swallow_ct), 10))

    patient_data_lst = []
    for i in aug_idx_lst:
        temp_lst = []
        for j in i:
            row_idx = j//10
            col_idx = j%10
            if if_dl:
                col_idx_lst = [col_idx + x*10 for x in range(7)]
            else:
                col_idx_lst = [col_idx + x*10 for x in range(6)]
            temp = df.iloc[row_idx, col_idx_lst].tolist()
            temp_lst.append(temp)
        patient_data_lst.append(temp_lst)

    df_data_lst = []
    for i in patient_data_lst:
        temp = i.pop(0)
        for j in range(len(i)):
            for k in range(len(i[j])):
                idx = (j+1)*(k+1)+k
                temp.insert(idx, i[j][k])
        df_data_lst.append(temp)

    df_data_lst = score(df_data_lst)

    for i in range(len(df_data_lst)):
        df_data_lst[i].insert(0, str(datetime.now())+'_aug'+str(i))
        df_data_lst[i].append(np.nan)

    col_lst = list(df.columns[:-1])
    col_lst.insert(0, 'ID')
    col_lst.append('patient_type')

    aug_df = pd.DataFrame(df_data_lst, columns=col_lst)
    
    output('data augmentation', 'augmentation.csv', aug_df)

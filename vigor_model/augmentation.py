import pandas as pd
import argparse
import random


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quantity', type=int, required=True, help='how much fake data to make')
    parser.add_argument('-d', '--dl', action='store_true', required=True, help='if distal latency is in all_patient')

    return parser


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

    
    print(patient_data_lst)
    df_data_lst = []
    for i in patient_data_lst:
        temp = i.pop(0)
        for j in range(len(i)):
            for k in range(len(i[j])):
                idx = (j+1)*(k+1)+k
                temp.insert(idx, i[j][k])
        df_data_lst.append(temp)
        
    aug_df = pd.DataFrame(df_data_lst, columns=df.columns[:-7])
    print(aug_df)

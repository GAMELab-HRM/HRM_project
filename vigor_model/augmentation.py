import pandas as pd
import argparse
import random
from transfer import output
from datetime import datetime
import numpy as np
from itertools import combinations


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quantity', type=int, required=True, help='how much fake data to make')
    parser.add_argument('-d', '--dl', action='store_true', required=True, help='if distal latency is in all_patient')
    parser.add_argument('-a', '--absent', type=int, help='how much absent data to make')
    parser.add_argument('-f', '--fragmented', type=int, help='how much fragmented data to make')

    return parser


def score(df_data_lst):
    transfer_lst = []
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
    
    return transfer_lst


def compute_percentile(transfer_lst, df_data_lst):
    scoring_result = []
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


def aug_data(aug_idx_lst, df):
    patient_data_lst = []
    for i in aug_idx_lst:
        temp_lst = []
        for j in i:
            row_idx = j//10
            col_idx = j % 10
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


    return df_data_lst


def aug_absent_data(quantity, df):
    aug_idx_lst = []
    absent_idx_lst = get_type_idx('Failed', df)
    for _ in range(quantity):
        aug_idx_lst.append(random.sample(absent_idx_lst, 10))
    df_data_lst = aug_data(aug_idx_lst, df)
    df_data_lst = compute_percentile(score(df_data_lst), df_data_lst)

    return df_data_lst


def aug_fragmented_data(quantity, df):
    aug_idx_lst = []
    fragmented_idx_lst = get_type_idx(['Fragmented'], df)
    ineffective_idx_lst = get_type_idx(['Failed', 'Weak'], df)
    other_idx_lst = get_type_idx(['Normal', 'Premature'], df)

    fragmented_ct_lst = list(range(5, 11))
    
    for i in fragmented_ct_lst:
        aug_idx_lst.extend(combine_fragmented_data(i, fragmented_idx_lst, ineffective_idx_lst, other_idx_lst))
    
    aug_idx_lst = list(random.sample(aug_idx_lst, quantity))
    df_data_lst = aug_data(aug_idx_lst, df)
    df_data_lst = compute_percentile(score(df_data_lst), df_data_lst)

    return df_data_lst


def combine_fragmented_data(ct, fragmented_idx_lst, ineffective_idx_lst, other_idx_lst):
    fragmented = list(combinations(fragmented_idx_lst, ct))

    if ct == 5:
        for i in range(len(fragmented)):
            ineffective_ct = random.sample(range(0, 5), 1)[0]
            other_ct = 5 - ineffective_ct
            fragmented[i] = list(fragmented[i])
            if ineffective_ct > 0:
                fragmented[i].extend(random.sample(ineffective_idx_lst, ineffective_ct))
            fragmented[i].extend(random.sample(other_idx_lst, other_ct))
    else:
        other_idx_lst.extend(ineffective_idx_lst)
        other_ct = 10 - ct
        for i in range(len(fragmented)):
            fragmented[i] = list(fragmented[i])
            fragmented[i].extend(random.sample(other_idx_lst, other_ct))

    return fragmented


def get_type_idx(label, df):
    score_lst = []
    temp_lst = score(df.values.tolist())
    for i in temp_lst:
        score_lst.extend(i)

    score_lst = enumerate(score_lst)
    idx_lst = []

    for i, j in score_lst:
        if j in label:
            idx_lst.append(i)

    return idx_lst


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    quantity = args.quantity
    if_dl = args.dl
    absent = args.absent if args.absent else 0
    fragmented = args.fragmented if args.fragmented else 0

    quantity -= absent + fragmented

    df = pd.read_csv('./data/all_patient.csv', encoding='big5', low_memory=False)
    df.drop('ID', axis=1, inplace=True)
    swallow_ct = int(df.shape[0])*10
    
    aug_idx_lst = []
    for _ in range(quantity):
        aug_idx_lst.append(random.sample(range(swallow_ct), 10))

    df_data_lst = aug_data(aug_idx_lst, df)
    df_data_lst = compute_percentile(score(df_data_lst), df_data_lst)

    if absent > 0:
        df_absent_lst = aug_absent_data(absent, df)
        df_data_lst.extend(df_absent_lst)

    if fragmented > 0:
        df_fragmented_lst = aug_fragmented_data(fragmented, df)
        df_data_lst.extend(df_fragmented_lst)

    for i in range(len(df_data_lst)):
        df_data_lst[i].insert(0, str(datetime.now())+'_aug'+str(i))
        df_data_lst[i].append(np.nan)

    col_lst = list(df.columns[:-1])
    col_lst.insert(0, 'ID')
    col_lst.append('patient_type')

    aug_df = pd.DataFrame(df_data_lst, columns=col_lst)
    
    output('data augmentation', 'augmentation.csv', aug_df)

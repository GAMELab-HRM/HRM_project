import pandas as pd
import argparse
import random
from transfer import output
from datetime import datetime
from itertools import combinations
import cc


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


def aug_data(aug_idx_lst, if_dl, df):
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


def aug_absent_data(quantity, if_dl, df):
    aug_idx_lst = []
    absent_idx_lst = get_type_idx('Failed', df)
    for _ in range(quantity):
        aug_idx_lst.append(random.sample(absent_idx_lst, 10))
    df_data_lst = aug_data(aug_idx_lst, if_dl, df)
    df_data_lst = compute_percentile(score(df_data_lst), df_data_lst)

    return df_data_lst


def aug_fragmented_data(quantity, if_dl, df):
    aug_idx_lst = []
    fragmented_idx_lst = get_type_idx(['Fragmented'], df)
    ineffective_idx_lst = get_type_idx(['Failed', 'Weak'], df)
    other_idx_lst = get_type_idx(['Normal', 'Premature'], df)

    fragmented_ct_lst = list(range(5, 11))
    
    for i in fragmented_ct_lst:
        aug_idx_lst.extend(combine_fragmented_data(i, fragmented_idx_lst, ineffective_idx_lst, other_idx_lst))
    
    aug_idx_lst = list(random.sample(aug_idx_lst, quantity))
    df_data_lst = aug_data(aug_idx_lst, if_dl, df)
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
    quantity_lst = [quantity, int(quantity*0.34)]

    

    df = pd.read_csv('./data/all_patient.csv', encoding='big5', low_memory=False)
    temp_cols = df.columns
    train_df = df[df['flag'] == 0].values
    train_df = pd.DataFrame(train_df, columns=temp_cols)
    output('data', 'train_original.csv', train_df)

    valid_df = df[df['flag'] == 1]
    valid_df = pd.DataFrame(valid_df, columns=temp_cols)
    output('data', 'valid_original.csv', valid_df)

    df_lst = [train_df, valid_df]
    
    for i in range(len(df_lst)):
        df_lst[i].drop(['ID', 'flag'], axis=1, inplace=True)
        swallow_ct = int(df_lst[i].shape[0])*10

        aug_idx_lst = []
        for _ in range(quantity_lst[i]):
            aug_idx_lst.append(random.sample(range(swallow_ct), 10))

        df_data_lst = aug_data(aug_idx_lst, if_dl, df_lst[i])
        df_data_lst = compute_percentile(score(df_data_lst), df_data_lst)

        if absent > 0:
            absent_lst = [absent, int(absent*0.34)]
            df_absent_lst = aug_absent_data(absent_lst[i], if_dl, df_lst[i])
            df_data_lst.extend(df_absent_lst)

        if fragmented > 0:
            fragmented_lst = [fragmented, int(fragmented*0.34)]
            df_fragmented_lst = aug_fragmented_data(fragmented_lst[i], if_dl, df_lst[i])
            df_data_lst.extend(df_fragmented_lst)

        for j in range(len(df_data_lst)):
            df_data_lst[j].insert(0, str(datetime.now())+'_aug'+str(j))
            df_data_lst[j].append(i)

        col_lst = list(df_lst[i].columns[:-1])
        col_lst.insert(0, 'ID')
        col_lst.append('flag')

        aug_df = pd.DataFrame(df_data_lst, columns=col_lst)

        # CC classification
        cc_lst = []
        for j in range(aug_df.shape[0]):
            cc_lst.append(cc.cc_v3(aug_df.iloc[j]))
        
        none_ct = 0
        for j in range(len(cc_lst)):
            if cc_lst[j]=='None':
                none_ct+=1
                aug_df.drop(j, inplace=True)
                aug_df.reset_index()

        for j in range(none_ct):
            cc_lst.remove('None')
            
        aug_df['patient_type'] = cc_lst

        # output augmentation.csv to data/
        if i == 0:
            file_name = 'train_aug.csv'
        elif i == 1:
            file_name = 'valid_aug.csv'

        output('data', file_name, aug_df)

import os
import glob
from logging import exception
from os import path
from shlex import split
import pandas as pd
from tabula import read_pdf
import numpy as np


'''
def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--times', type=int, default='3')
    parser.add_argument('-s', '--stride', type=int, default='10')
    
    return parser
'''


def get_contraction(path_lst, if_pattern):
    vigor_lst = []
    pattern_lst = []
    patient_type_lst = []
    for path in path_lst:
        patient_type = path.split('-')[1][:-4]
        patient_type_lst.append(patient_type)
        df = pd.read_csv(path, encoding='big5', skiprows=6, low_memory=False)
        df['Contraction vigor'].fillna(0, inplace=True)
        vigor = df.loc[df['Contraction vigor'] != 0]['Contraction vigor'].tolist()[:10]
        
        df['Contraction pattern'].fillna(0, inplace=True)
        pattern = df.loc[df['Contraction pattern'] != 0]['Contraction pattern'].tolist()[:10]
        
        '''
        print(path)
        print(df['Contraction vigor'].unique())
        print(vigor)
        print(df['Contraction pattern'].unique())
        print(pattern)
        print("--------------------------")
        '''
        
        
        for i in range(len(vigor)):
            vigor[i] = vigor[i].strip()
            pattern[i] = pattern[i].strip()
        vigor_lst.append(vigor)
        pattern_lst.append(pattern)

    df = pd.DataFrame(vigor_lst, columns=['v'+str(i) for i in range(1, 11)])

    if if_pattern:
        df.loc[:, ['p'+str(i) for i in range(1, 11)]]=pattern_lst

        #exit(0)

    df['patient_type'] = patient_type_lst
    path_lst = [x.split("\\")[1] for x in path_lst]
    df.insert(0, 'ID', path_lst)

    return df


def output(file_path, file_name, df):       
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print("[INFO] Create {} folder".format(file_path))
    
    df.to_csv(path.join(file_path, file_name), encoding='big5', index=False)
    print("[INFO] output {} successfully".format(file_name))


def get_DCI_IRP(path_lst, contraction_df):
    DCI_lst = []
    IRP02_lst = []
    IRP08_lst = []
    IRP40_lst = []

    for path in path_lst:
        print(path)
        pdf_df_lst = read_pdf(path, guess=False, pages=[1, 2], stream=True, encoding="utf-8")
        pdf_df = pd.concat(pdf_df_lst, axis=0, ignore_index=True)

        
        col_num = set(pdf_df_lst[0].columns.tolist())
        col_num.update(pdf_df_lst[1].columns.tolist())
        
        pdf_df.columns = ['col '+str(x) for x in range(len(col_num))]
        pdf_df.replace(np.nan, '-', inplace=True)

        try:
            DCI_data = process_DCI_data(pdf_df, 'col 4')
        except Exception as e:
            try:
                DCI_data = process_DCI_data(pdf_df, 'col 3')
            except Exception as e:
                DCI_data = process_DCI_data(pdf_df, 'col 0')
        
        DCI_lst.append(DCI_data)

        try:
            IRP02_data = process_IRP02_data(pdf_df, 'col 2')
        except Exception as e:
            IRP02_data = process_IRP02_data(pdf_df, 'col 3')
        
        IRP02_lst.append(IRP02_data)

        try:
            IRP08_data = process_IRP08_data(pdf_df, 'col 3')
        except Exception as e:
            IRP08_data = process_IRP08_data(pdf_df, 'col 4')
        
        IRP08_lst.append(IRP08_data)

        
        pdf_df = pdf_df.iloc[50:, :]
        pdf_df.reset_index(inplace=True, drop=True)
        try:
            IRP40_data = process_IRP40_data(pdf_df, 'col 3')
        except Exception as e:
            IRP40_data = process_IRP40_data(pdf_df, 'col 4')

        IRP40_lst.append(IRP40_data)


    DCI_df = pd.DataFrame(DCI_lst, columns=['DCI_'+str(i) for i in range(1, 11)])
    IRP02_df = pd.DataFrame(IRP02_lst, columns=['IRP02_'+str(i) for i in range(1, 11)])
    IRP08_df = pd.DataFrame(IRP08_lst, columns=['IRP08_'+str(i) for i in range(1, 11)])
    IRP40_df = pd.DataFrame(IRP40_lst, columns=['IRP40_'+str(i) for i in range(1, 11)])
    
    df_lst = [DCI_df, IRP02_df, IRP08_df, IRP40_df]

    DCI_IRP_df = pd.concat(df_lst, axis=1)
    target = contraction_df['patient_type']
    contraction_df.drop('patient_type', axis=1, inplace=True)
    df = pd.concat([contraction_df, DCI_IRP_df], axis=1)
    df['patient_type'] = target

    return df


def process_DCI_data(pdf_df, col_name):
    ini_idx = pdf_df.loc[pdf_df[col_name].astype(str).str.contains('DCI', na=False)].index.tolist()[0]+3
    col_idx = int(col_name.split(' ')[1])
    DCI_data = pdf_df.iloc[ini_idx:ini_idx+10, col_idx].to_list()
    DCI_data = [x.split(' ')[1] for x in DCI_data]

    return DCI_data


def process_IRP02_data(pdf_df, col_name):
    ini_idx = pdf_df.loc[pdf_df[col_name].astype(str).str.contains('IRP 0.2 s', na=False)].index.tolist()[0]
    col_idx = int(col_name.split(' ')[1])
    stride = 0

    for i in range(1, 4):
        try:
            temp = float(pdf_df.iloc[ini_idx+i, col_idx].split(' ')[0])
            stride = i
            break
        except Exception as e:
            pass
    
    ini_idx += stride
    IRP02_data = pdf_df.iloc[ini_idx:ini_idx+10, col_idx].to_list()
    if type(IRP02_data[0]) != float and " " in IRP02_data[0]:
        IRP02_data = [x.split(' ')[0] for x in IRP02_data]

    return IRP02_data


def process_IRP08_data(pdf_df, col_name):
    ini_idx = pdf_df.loc[pdf_df[col_name].astype(str).str.contains('IRP 0.8 s', na=False)].index.tolist()[0]
    col_idx = int(col_name.split(' ')[1])
    stride = 0

    for i in range(1, 4):
        try:
            temp = float(pdf_df.iloc[ini_idx+i, col_idx].split(' ')[0])
            stride = i
            break
        except Exception as e:
            pass

    ini_idx += stride
    IRP08_data = pdf_df.iloc[ini_idx:ini_idx+10, col_idx].to_list()

    if type(IRP08_data[0]) != float and " " in IRP08_data[0]:
        IRP08_data = [x.split(' ')[1] for x in IRP08_data]

    return IRP08_data


def process_IRP40_data(pdf_df, col_name):
    ini_idx = pdf_df.loc[pdf_df[col_name].astype(str).str.contains('IRP 4 s', na=False)].index.tolist()[0]
    col_idx = int(col_name.split(' ')[1])
    stride = 0
    for i in range(1, 5):
        try:
            temp = float(pdf_df.iloc[ini_idx+i, col_idx].split(' ')[0])
            stride = i
            break
        except Exception as e:
            pass
    ini_idx += stride
    IRP40_data = pdf_df.iloc[ini_idx:ini_idx+10, col_idx].to_list()
    IRP40_data = [x.split(' ')[0] for x in IRP40_data]

    return IRP40_data


def get_scoring(path_lst, contraction_df):
    score = ['Normal', 'Ineffective', 'Failed contraction','Premature', 'Hyper', 'Fragmented']
    score = ['scoring_' + x for x in score]
    scoring_lst = []
    for path in path_lst:
        print(path)
        pdf_df = read_pdf(path, guess=False, pages=1, stream=True, encoding="utf-8")[0]
        pdf_df.replace(np.nan, 0, inplace=True)
        try:
            scoring_data = process_scoring_data(pdf_df, 'Unnamed: 1')
        except Exception as e:
            try:
                scoring_data = process_scoring_data(pdf_df, 'Unnamed: 0')
            except Exception as e:
                scoring_data = process_scoring_data(pdf_df, 'Unnamed: 2')
        scoring_lst.append(scoring_data)

    scoring_df = pd.DataFrame(scoring_lst, columns=score)
    target = contraction_df['patient_type']
    contraction_df.drop('patient_type', axis=1, inplace=True)
    df = pd.concat([contraction_df, scoring_df], axis=1)
    df['patient_type'] = target

    return df
    

def process_scoring_data(pdf_df, col_name):
    ini_idx = pdf_df.loc[pdf_df[col_name].astype(str).str.contains('EGJ', na=False)].index.tolist()[0]-1
    col_idx = int(col_name.split(' ')[1])+1
    scoring_data = pdf_df.iloc[ini_idx:ini_idx+6, col_idx].to_list()
    scoring_data = [float(x.split(' ')[0])*0.01 for x in scoring_data]

    return scoring_data


def get_DL(path_lst, contraction_df):
    DL_lst = []
    DL = ['DL_' + str(x) for x in range(1, 11)]

    for path in path_lst:
        print(path)
        pdf_df_lst = read_pdf(path, guess=False, pages=[1, 2], stream=True, encoding="utf-8")
        pdf_df = pd.concat(pdf_df_lst, axis=0, ignore_index=True)

        col_num = set(pdf_df_lst[0].columns.tolist())
        col_num.update(pdf_df_lst[1].columns.tolist())

        pdf_df.columns = ['col '+str(x) for x in range(len(col_num))]
        pdf_df.replace(np.nan, '-', inplace=True)
        
        pdf_df = pdf_df.iloc[:100, :]
        pdf_df.reset_index(inplace=True, drop=True)

        try:
            DL_data = process_DL_data(pdf_df, 'col 2')
        except Exception:
            try:
                DL_data = process_DL_data(pdf_df, 'col 3')
            except Exception:
                DL_data = process_DL_data(pdf_df, 'col 4')

        DL_lst.append(DL_data)

    DL_df = pd.DataFrame(DL_lst, columns=DL)
    target = contraction_df['patient_type']
    contraction_df.drop('patient_type', axis=1, inplace=True)
    df = pd.concat([contraction_df, DL_df], axis=1)
    df['patient_type'] = target

    return df


def process_DL_data(pdf_df, col_name):
    ini_idx = pdf_df.loc[pdf_df[col_name].astype(str).str.contains('Distal Latency', na=False)].index.tolist()[-1]
    col_idx = int(col_name.split(' ')[1])
    stride = 1
    ct = 0
    for i in range(1, 4):
        try:
            target = pdf_df.iloc[ini_idx+i, col_idx].split(' ')[0]
            if target.strip() == '-':
                ct += 1
            temp = float(target)
            stride = i
            break
        except Exception as e:
            pass
    else:
        if ct >= 3:
            stride = 3
        else:
            raise Exception

    ini_idx += stride
    DL_data = pdf_df.iloc[ini_idx:ini_idx+10, col_idx].to_list()
    if " " in DL_data[0]:
        DL_data = [x.split(' ')[1] for x in DL_data]

    return DL_data


if __name__ == '__main__':
    
    # parser = get_parser()
    # args = parser.parse_args()
    # times = args.times
    # stride = args.stride



    path_lst = glob.glob('./original_data/*/*.CSV')
    contraction_df = get_contraction(path_lst, if_pattern=True)
    
    pdf_path_lst = glob.glob('./original_data/*/*.pdf')
    df = get_DCI_IRP(pdf_path_lst, contraction_df)
    df = get_scoring(pdf_path_lst, df)
    df = get_DL(pdf_path_lst, df)

    output('data', 'all_patient.csv', df)

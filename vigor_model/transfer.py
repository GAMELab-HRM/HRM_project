import argparse
import glob
from os import path
import pandas as pd

'''
def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--times', type=int, default='3')
    parser.add_argument('-s', '--stride', type=int, default='10')
    
    return parser
'''


def get_contraction_vigor(path_lst, if_pattern):
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
        

        for i in range(len(vigor)):
            vigor[i] = vigor[i].strip()
            pattern[i] = pattern[i].strip()
        vigor_lst.append(vigor)
        pattern_lst.append(pattern)

    df = pd.DataFrame(vigor_lst, columns=['v'+str(i) for i in range(1, 11)])

    if if_pattern:
        df.loc[:, ['p'+str(i) for i in range(1, 11)]]=pattern_lst

    df['patient_type'] = patient_type_lst
    print(df)
    return df


def output(file_path, file_name, df):       
    df.to_csv(path.join(file_path, file_name), encoding='big5', index=False)
    print("[INFO] output {} successfully".format(file_name))


if __name__ == '__main__':
    
    # parser = get_parser()
    # args = parser.parse_args()
    # times = args.times
    # stride = args.stride

    path_lst = glob.glob('./original_data/*/*.CSV')
    df = get_contraction_vigor(path_lst, if_pattern=True)
    output('data', 'all_patient.csv', df)







    #check_min_rest(path_lst, times, stride)
    #augmentation_df_lst = data_augmentation(path_lst, times, stride)
    #name_lst = [i.split('\\')[-1] for i in path_lst]
    #output(augmentation_df_lst, name_lst)
    
    #draw()
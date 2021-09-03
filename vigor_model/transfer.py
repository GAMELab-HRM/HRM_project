import argparse
import glob
from logging import exception
from os import path
from shlex import split
import pandas as pd
from tabula import read_pdf


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


def get_DCI_IRP(path_lst):
    DCI_lst = []
    IRP_lst = []
    exception_lst = ['T220351794', 'U121003125']
    for path in path_lst:
        print(path)
        id = path.split("\\")[1]
        if id in exception_lst:
            df = read_pdf(path, guess=False, pages=1, stream=True, encoding="utf-8")[0]
            DCI = [x.split(" ")[1] for x in df.iloc[36:46, 0].tolist()]

            df = read_pdf(path, guess=False, pages=2,stream=True, encoding="utf-8")[0]
            if id == 'T220351794':
                magic_num = df.iloc[4, 1]
                temp = df.iloc[2:12, 2].tolist()
                IRP_2 = [x.split(" ")[0] for x in temp if len(x) > 3 ]
                IRP_2.insert(2, magic_num)

                temp = df.iloc[2:12, 2].tolist()
                IRP_8 = [x.split(" ")[1] if len(x) > 3 else x for x in temp]
            
            else:
                pass

        elif id == 'U120483683':
            df = read_pdf(path, guess=False, pages=1,stream=True, encoding="utf-8")[0]
            DCI = [x.split(" ")[1] for x in df.iloc[48:58, 0].tolist()]
            print(DCI)
        else:
            df = read_pdf(path, guess=False, pages=2, stream=True, encoding="utf-8")[0]
            DCI = [x.split(" ")[1] for x in df.iloc[4:14, 0].tolist()]

            print(DCI)

            IRP_2 = df.iloc[20:30, 2].tolist()
            IRP_8 = df.iloc[20:30, 3].tolist()
            IRP_4 = [x.split(" ")[0] for x in df.iloc[37:47, 3].tolist()]

            print(IRP_2)
            print(IRP_8)
            print(IRP_4)


        DCI_lst.append(DCI)
        IRP_lst.append([IRP_2, IRP_8, IRP_4])

    return DCI_lst, IRP_lst


if __name__ == '__main__':
    
    # parser = get_parser()
    # args = parser.parse_args()
    # times = args.times
    # stride = args.stride

    #path_lst = glob.glob('./original_data/*/*.CSV')
    #df = get_contraction_vigor(path_lst, if_pattern=True)
    #output('data', 'all_patient.csv', df)

    pdf_path_lst = glob.glob('./test/*/*.pdf')
    get_DCI_IRP(pdf_path_lst)






    #check_min_rest(path_lst, times, stride)
    #augmentation_df_lst = data_augmentation(path_lst, times, stride)
    #name_lst = [i.split('\\')[-1] for i in path_lst]
    #output(augmentation_df_lst, name_lst)
    
    #draw()

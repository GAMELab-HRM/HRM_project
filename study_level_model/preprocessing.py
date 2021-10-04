import pandas as pd
from pandas.core.arrays import categorical
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from transfer import output
from sklearn.impute import SimpleImputer
import glob


def mapping(param):
    def decorator(func):
        def wrap(x):
            for key, value in param.items():
                if x in value:
                    return key
            return 0
        return wrap
    return decorator


def mapping_Y_label(df, target_dict):
    
    @ mapping(param=target_dict)
    def mapping_rule(x):
        pass
    
    df['patient_type'] = df['patient_type'].map(mapping_rule)
    
    return df


def encode_data(df, **categorical_data):
    target_column = df['patient_type']
    number_df = df.loc[:, df.columns[21:-1]]
    id_column = df['ID']
    LE = LabelEncoder()
    df_lst = []

    for column, categorical in categorical_data.items():
        LE.fit(categorical)
        temp_df = df.loc[:, column.split(' ')].apply(lambda x : LE.transform(x))
        df_lst.append(temp_df)

    df_lst.append(number_df)

    df = pd.concat(df_lst, axis=1)
    df['patient_type'] = target_column
    df.insert(0, 'ID', id_column)
    
    return df


def process_DCI_IRP(df):
    id_column = df['ID']
    df.drop(['ID'], axis=1, inplace=True)
    df.replace('-', 0, inplace=True)
    df = df.astype(float)
    df.insert(0, 'ID', id_column)

    return df


def one_hot_encoding(df):
    col = ['v'+str(i+1) for i in range(10)] + ['p'+str(i+1) for i in range(10)]
    df2 = pd.get_dummies(df, columns=col, prefix=col)
    label = df2['patient_type']
    flag = df2['flag']
    df2 = df2.drop(['flag', 'patient_type'], axis=1)
    df2['flag'] = flag
    df2['patient_type'] = label

    return df2


if __name__ == '__main__':
    path_lst = glob.glob('./data/*.CSV')
    train_df_lst = []
    valid_df_lst = []
    df_lst = []
    file_name_lst = []
    
    for path in path_lst:
        df = pd.read_csv(path, encoding='big5', low_memory=False)
        df_lst.append(df)
        file_name = path.split('\\')[-1]
        file_name_lst.append(file_name)
        if 'train' in file_name:
            train_df_lst.append(df)
        elif 'valid' in file_name:
            valid_df_lst.append(df)

    df_lst.extend([pd.concat(train_df_lst), pd.concat(valid_df_lst)])
    file_name_lst.extend(['train_concat.csv', 'valid_concat.csv'])
    df_dict = dict(zip(file_name_lst, df_lst))

    for file_name, df in df_dict.items():
        # 自訂label格式 -> class: label，label可以是list
        # 自訂label從1開始，預設其他會被歸類為0
        df = mapping_Y_label(df, {
            '0': 'normal',
            '1': 'IEM',
            '2': 'Absent',
            '3': 'Fragmented'
        })

        categorical_data={
            # 因為list不能當key，所以先做成字串，放入encode_data()之後再轉回list
            ' '.join(['v'+ str(x) for x in range(1, 11)]): ['Failed', 'Weak', 'Normal'], 
            ' '.join(['p'+ str(x) for x in range(1, 11)]): ['Failed', 'Fragmented', 'Premature', 'Intact', 'Normal']
        }
        df = encode_data(df, **categorical_data)

        df = process_DCI_IRP(df)
        df = one_hot_encoding(df)

        output('training_data', file_name, df)

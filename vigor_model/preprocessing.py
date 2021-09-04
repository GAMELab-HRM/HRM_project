import pandas as pd
from pandas.core.arrays import categorical
from sklearn.preprocessing import LabelEncoder
from transfer import output

def mapping(param):
    def decorator(func):
        def wrap(x):
            label = 1 if x in param else 0
            return label
        return wrap
    return decorator


def mapping_Y_label(df, target_lst):
    
    @ mapping(param=target_lst)
    def mapping_rule(x):
        pass
    
    df['patient_type'] = df['patient_type'].map(mapping_rule)
    
    return df


def encode_data(df, **categorical_data):
    target_column = df['patient_type']
    LE = LabelEncoder()
    df_lst = []

    for column, categorical in categorical_data.items():
        LE.fit(categorical)
        temp_df = df.loc[:, column.split(' ')].apply(lambda x : LE.transform(x))
        df_lst.append(temp_df)

    
    df = pd.concat(df_lst, axis=1)
    df['patient_type'] = target_column
    
    return df


if __name__ == '__main__':
    
    df = pd.read_csv('./data/all_patient.csv', encoding='big5', low_memory=False)
    df = mapping_Y_label(df, ['IEM'])
    categorical_data={
        # 因為list不能當key，所以先做成字串，放入encode_data之後再轉回list
        ' '.join(['v'+ str(x) for x in range(1, 11)]): ['Failed', 'Weak', 'Normal'], 
        ' '.join(['p'+ str(x) for x in range(1, 11)]): ['Failed', 'Fragmented', 'Premature', 'Intact', 'Normal']
    }
    df = encode_data(df, **categorical_data)
    output('training_data', 'training.csv', df)

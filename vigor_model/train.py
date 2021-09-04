from numpy.core.fromnumeric import mean
from model import SVM_1
import pandas as pd
from sklearn.model_selection import KFold, cross_validate
from sklearn.metrics import make_scorer, recall_score, roc_auc_score, f1_score, accuracy_score

def validation(N, df, model):
    kf = KFold(n_splits=N, random_state=100, shuffle=True)
    scoring = {
        'acc': make_scorer(accuracy_score),
        'recall': make_scorer(recall_score),
        'roc and auc': make_scorer(roc_auc_score),
        'f1': make_scorer(f1_score)
    }
    
    results = cross_validate(
        estimator=model,
        X=df.iloc[:, :-1],
        y=df.iloc[:, -1],
        cv=kf,
        scoring=scoring
    )
    
    '''
    for train_idx, test_idx in kf.split(df.iloc[:, :-1]):
        X_train, X_test = df.iloc[train_idx, :-1], df.iloc[test_idx, :-1]
        y_train, y_test = df.iloc[train_idx, -1], df.iloc[test_idx, -1]

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test, y_test)
    ''' 
    for i, j in results.items():
        print(i, mean(j))


if __name__=='__main__':
    model = SVM_1()
    df = pd.read_csv('training_data/training.csv', encoding='big5', low_memory=False)
    validation(3, df, model)





from numpy import poly
from sklearn.svm import SVC



def SVM_1():
    classifier = SVC(C=5, cache_size=5000, max_iter=200, degree=5, gamma='auto')
    
    return classifier

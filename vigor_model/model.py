from numpy import poly
from sklearn.svm import SVC



def SVM_1():
    classifier = SVC(C=5, cache_size=5000, max_iter=3, degree=5, gamma=2)
    
    return classifier

import pandas as pd 
import numpy as np 


def check_IRP_Normal(IRP):
    if IRP <= 16:
        return True
    else:
        return False

def cc_v3(df):
    IRP_key = ["IRP40_"+str(i+1) for i in range(10)]

    # Chicago Classification V3 params
    ID = df["ID"]
    scoring_Normal = df["scoring_Normal"]
    scoring_Ineffective = df["scoring_Ineffective"]
    scoring_Failed = df["scoring_Failed contraction"]
    scoring_Premature = df["scoring_Premature"]
    scoring_Hyper = df["scoring_Hyper"]
    scoring_Fragmented = df["scoring_Fragmented"]

    # compute the average of Distal Latency 
    # compute the average of IRP 
    IRP = df[IRP_key].values
    IRP = round(np.mean(np.delete(IRP, np.where(IRP == '-')).astype('float64')), 1)
    
    # Chicago Classification 
    if check_IRP_Normal(IRP) and scoring_Failed == 1.0:
        # print(ID, "Absent", label)
        return "Absent"

    if check_IRP_Normal(IRP) and scoring_Ineffective >= 0.5:
        # print(ID, "IEM", label)
        return "IEM"

    if check_IRP_Normal(IRP) and scoring_Fragmented >= 0.5:
        # print(ID, "Fragmented", label)
        return "Fragmented"
    
    if check_IRP_Normal(IRP) and scoring_Normal >= 0.5:
        # print(ID, "normal", label)
        return "normal"

    return "None"


from utils import draw
import matplotlib.pyplot as plt 
import numpy as np 
import glob 


if __name__ == "__main__":
    res = glob.glob('./train/*.csv')
    for r in res:
        draw(r)


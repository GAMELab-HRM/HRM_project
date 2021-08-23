from utils import draw_wet_swallows
import matplotlib.pyplot as plt 
import numpy as np 
import glob 


if __name__ == "__main__":
    res = glob.glob('./train/*.csv')
    for r in res:
        print(r)
        draw_wet_swallows(r)


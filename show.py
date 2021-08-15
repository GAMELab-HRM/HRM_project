from utils import draw
import matplotlib.pyplot as plt 
import numpy as np 
import glob 


if __name__ == "__main__":
    res = glob.glob('./train/*.CSV')
    for r in res:
        draw(r)


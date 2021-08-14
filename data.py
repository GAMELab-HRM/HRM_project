from utils import preprocess 
import glob, os

if __name__ == "__main__":
    # create training data's folder 
    if not os.path.exists('train'):
        os.makedirs('train')
        print("[INFO] Create train folder")

    res = glob.glob('./*/*.csv') # 遞迴抓取所有的csv file 
    for fname in res:
        print(fname)
        #print(fname[13:])
        preprocess(fname)
        
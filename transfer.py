from utils import preprocess, compute_swallow_size
import glob, os

if __name__ == "__main__":
    # create training data's folder 
    if not os.path.exists('train'):
        os.makedirs('train')
        print("[INFO] Create train folder")

    res = glob.glob('./data/*/*.CSV') # 遞迴抓取所有的csv file 
    swallow_size = compute_swallow_size(res) # 算出每個swallow的大小，並找出最小值作為規範
    for fname in res:
        print(fname)
        preprocess(fname, swallow_size)
        
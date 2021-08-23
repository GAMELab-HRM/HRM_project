import glob 

label = ['normal', 'IEM', 'Absent', 'Fragmented']
filepath = './train'

res = glob.glob('./train/*.csv')

for r in res:
    file_label = r.split('-')[1][:-4]
    print(file_label)
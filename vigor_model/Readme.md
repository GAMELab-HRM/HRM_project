## HRM project

### Study-level model
使用DCI、IRP、DL等數值，以機器學習的方式，預測 Chicago classification v3 最後的診斷結果，協助醫師診斷食道相關病症

### Folder

* original_data
    * 存放醫院提供的資料(raw_data.csv、report.pdf)
    * 錯誤資料修正紀錄
        1. raw data column拼字錯誤(已修正)
            * 1375-normal (Contraction vigor)
            * 0503-IEM (Contraction vigor)
        2. 檔名錯誤(已修正)
            * 5290-Absent absent拼錯
        3. Contraction pattern 標記錯誤(已修正)
            * 8569-normal wet swallow8 拼字錯誤 Intacct，應為 Intact
            * 5941-normal wet swallow9 拼字錯誤 Inatact，應為 Intact
            * 2972-normal wet swallow4 標記為 normal，應為 Intact
        4. DCI 表格在 page1 (除1794-IEM暫時移除外，其餘已修正)
            <br>因為report.pdf執中缺乏圖片，導致DCI的數據在page1，在導入數據時，容易出錯
            * 1794-IEM **(目前無法處理，需要先刪除)**
            * 3125-IEM
            * 3683-Absent
        5. 異常資料(皆暫時移除)
            * 2134 未計算
            * 7652 無數據
        6. patient type 標記錯誤(正在與醫生協調中)
            * 6526-IEM 標記為IEM，應為Absent
            * 3425-IEM 標記為IEM，應為Absent
* data
    * 存放經由 `transfer.py`，從 original data 中提取的資料
        * all_patient.csv
    * 存放 data augmentation 所產生的資料
        * train_original.csv
        * train_aug.csv
        * valid_original.csv
        * valid_aug.csv
* training_data
    * 存放經由 `preprocessing.py`，從 data 中前處理過後的資料
        * train_original.csv
        * train_aug.csv
        * train_concat.csv
        * valid_original.csv
        * valid_aug.csv
        * valid_concat.csv

### 使用步驟

1.  提取資料<br>
    提取醫院所提供的資料(raw_data.csv、report.pdf)，並將提取的資料放入 data/all_patient.csv
    ```shell=0
    python transfer.py -d -s
    ```
    * 預設提取DCI、 IRP0.2S、IRP0.8S、IRP4.0S
    * -d(alternative)，將DL(distal latency)加入特徵
    * -s(alternative)，將scoring(即swallow type的機率分布)加入特徵

2. 資料增強<br>
   隨機組合原有病人的各個swallow，並進行scoring與CC v3，將增強所得到的資料與原資料放入 data/
  
    | 檔名 | 內容 |
    | -------- | -------- | 
    | train_original.csv   |  預計用於訓練的原始資料集     |
    | train_aug.csv   |   自train_original生成，預計用於的訓練模型的資料集  | 
    | valid_original.csv   |  預計用於驗證的原始資料集     | 
    | valid_aug.csv   |  自vaild_original生成，預計用於的驗證模型的資料集    | 

   ```shell=0
    python augmentation.py -d -q <int> -a <int> -f <int>
    ```
    
    * -d(required)，若資料中有DL(即在Step 1中有加入該特徵)，則需要加入此參數
    * -q(required)，設定總共需要增強的資料數
    * 針對特殊類別的資料增強
        <br>因為部分類別的資料產生條件較為嚴苛，難以直接隨機產生
        * -a(alternative)，設定-q中的幾筆資料為Absent類型的資料
        * -f(alternative)，設定-q中的幾筆資料為Fragmented類型的資料

3. 資料前處理<br>
   處理資料的異常值、對資料做label encoding，將資料存入training_data/
    
    ```shell=0
    python preprocessing.py
    ```
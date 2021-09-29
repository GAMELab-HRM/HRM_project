## HRM project

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

### python File

* `transfer.py`
    
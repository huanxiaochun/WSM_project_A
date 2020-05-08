import os
import json
from datetime import datetime
import sqlite3
import re
from tqdm import tqdm

data_root = r'C:\Users\86183\Desktop\研究生课\研一下\互联网信息搜索与挖掘\project_A\data\\'
data1_path = r'C:\Users\86183\Desktop\研究生课\研一下\互联网信息搜索与挖掘\project_A\data\data1\home\data\law\zxgk\\'
data2_path = r'C:\Users\86183\Desktop\研究生课\研一下\互联网信息搜索与挖掘\project_A\data\data2\home\data\law\hshfy\info\\'
instruments_path = r'C:\Users\86183\Desktop\研究生课\研一下\互联网信息搜索与挖掘\project_A\data\instruments\home\data\law\hshfy_wenshu\\'

conn = sqlite3.connect(data_root + 'data.db')
print("Opened database successfully...")
c = conn.cursor()


def deal_instruments(filepath):
    '''
        Deal with instruments files.
        :param filepath: path name
        :return: None
    '''
    instruments_files = os.listdir(filepath)

    '''Convert to json file'''
    # for file in tqdm(instruments_files, desc='instruments convert to json...'):
    #     oldname = filepath + file
    #     newname = filepath + file + ".json"
    #     os.rename(oldname, newname)

    '''Create table instruments'''
    sql = '''CREATE TABLE instruments
            (ID   CHAR(100)  PRIMARY KEY   NOT NULL,
            caseCode         TEXT,
            Title          TEXT,
            Type           TEXT,
            Cause          TEXT,
            Department     TEXT,
            Level          TEXT,
            ClosingDate    DATE,
            Content        TEXT);'''
    c.execute(sql)
    print("Table created successfully...")
    conn.commit()

    '''Save data to the database'''
    for file in tqdm(instruments_files, desc="insert instruments..."):
        with open(instruments_path + file) as f:
            data = json.load(f)

            # data processing
            for key in data:
                if key == "结案日期":
                    data[key] = datetime.strptime(data[key].strip(), '%Y-%m-%d').date()
                elif key == "content":
                    data[key] = ' '.join(data[key].strip().split())
                else:
                    data[key] = data[key].strip()

            # Insert each record
            values = []
            for key in data:
                values.append(data[key])
            values = tuple(values)
            sql = "insert into instruments values(?, ?, ?, ?, ?, ?, ?, ?, ?)"
            c.execute(sql, values)

    conn.commit()
    print("Records created successfully...")


def deal_data1(filepath):
    '''
        Deal with data1 files.
        :param filepath: path name
        :return: None
    '''
    data1_files = os.listdir(filepath)

    '''Convert to json file'''
    # for file in tqdm(data1_files, desc='data1 convert to json...'):
    #     oldname = filepath + file
    #     newname = filepath + file + ".json"
    #     os.rename(oldname, newname)

    '''Create table data1'''
    # sql = '''CREATE TABLE data1
    #             (ID            INT  PRIMARY KEY   NOT NULL,
    #             iname          TEXT,
    #             caseCode       TEXT,
    #             age            INT,
    #             sexy           CHAR(10),
    #             cardNum        TEXT,
    #             businessEntity     TEXT,
    #             courtName          TEXT,
    #             areaName    DATE,
    #             partyTypeName        TEXT,
    #             gistId        TEXT,
    #             regDate        DATE,
    #             gistUnit        TEXT,
    #             duty        TEXT,
    #             performance        TEXT,
    #             performedPart        TEXT,
    #             unperformPart        TEXT,
    #             disruptTypeName        TEXT,
    #             publishDate          DATE,
    #             qysler            TEXT);'''
    #
    # c.execute(sql)
    # print("Table created successfully...")
    # conn.commit()

    keys = ['id', 'iname', 'caseCode', 'age', 'sexy', 'cardNum', 'businessEntity', 'courtName', 'areaName', 'partyTypeName',
     'gistId', 'regDate', 'gistUnit', 'duty', 'performance', 'performedPart', 'unperformPart', 'disruptTypeName',
     'publishDate', 'qysler']


    '''Save data to the database'''
    for file in tqdm(data1_files, desc="insert data1..."):
        with open(data1_path + file) as f:
            data = json.load(f)

            # data processing
            for key in data:
                if key == "regDate" or key == "publishDate":
                    # 2015年04月09日(str) ------> 2015-04-09(str) ------> 2015-04-09(date)
                    d = '-'.join(re.findall(r"\d+", data[key]))
                    data[key] = datetime.strptime(d.strip(), '%Y-%m-%d').date()
                elif key == 'qysler':
                    data[key] = str(data[key])
                elif key == 'gistId' and isinstance(data[key], list):
                    data[key] = ' '.join(data[key])
                else:
                    if isinstance(data[key], str):
                        data[key] = data[key].strip()

            # for key in data:
            #     print(key, data[key], type(data[key]))

            # Insert each record
            values = []
            for key in keys:
                if key not in data:
                    values.append(None)  # Some files are missing fields
                else:
                    values.append(data[key])

            values = tuple(values)
            sql = "insert into data1 values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            c.execute(sql, values)

    conn.commit()
    print("Records created successfully...")


def deal_data2(filepath):
    '''
        Deal with data1 files.
        :param filepath: path name
        :return: None
    '''
    data2_files = os.listdir(filepath)
    print(len(data2_files))


if __name__ == '__main__':
    # print("start processing instruments..")
    # deal_instruments(instruments_path)

    # print("start processing data1..")
    # deal_data1(data1_path)

    print("start processing data2..")
    deal_data2(data2_path)

    conn.close()
import os
import shutil
import json
from datetime import datetime
import sqlite3
import re
from tqdm import tqdm

# the path to server html, js, css files
root_path = os.path.join(os.path.split(__file__)[0], '../../data')
# os.path.abspath返回绝对路径
root_path = os.path.abspath(root_path)

data1_path = os.path.join(root_path, r'data1\home\data\law\zxgk')
data2_path = os.path.join(root_path, r'data2\home\data\law\hshfy\info')
instruments_path = os.path.join(root_path, r'instruments\home\data\law\hshfy_wenshu')

conn = sqlite3.connect(os.path.join(root_path, 'data.db'))
conn.text_factory = str
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
    #     oldname = os.path.join(filepath, file)
    #     newname = os.path.join(filepath, file, '.json')
    #     os.rename(oldname, newname)

    '''Create table instruments'''
    # sql = '''CREATE TABLE instruments
    #         (ID   CHAR(100)  PRIMARY KEY   NOT NULL,
    #         caseCode         TEXT,
    #         Title          TEXT,
    #         Type           TEXT,
    #         Cause          TEXT,
    #         Department     TEXT,
    #         Level          TEXT,
    #         ClosingDate    DATE,
    #         Content        TEXT);'''
    # c.execute(sql)
    # print("Table created successfully...")
    # conn.commit()

    '''Save data to the database'''
    for file in tqdm(instruments_files, desc="insert instruments..."):
        with open(os.path.join(filepath, file)) as f:
            data = json.load(f)

            # data processing
            for key in data:
                if key == "结案日期":
                    data[key] = datetime.strptime(data[key].strip(), '%Y-%m-%d').date()
                elif key == "content":
                    lines = data[key].strip().split("\r")
                    new_lines = []
                    for line in lines:
                        line = line.replace('\n', '').replace('\t', '').replace('\xa0', '').strip()
                        new_lines.append(line)
                    data[key] = ' '.join(new_lines)
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
    #     oldname = os.path.join(filepath, file)
    #     newname = os.path.join(filepath, file, '.json')
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
    #             areaName    TEXT,
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
        with open(os.path.join(filepath, file)) as f:
            data = json.load(f)

            # data processing
            for key in data:
                if key == "regDate" or key == "publishDate":
                    # 2015年04月09日(str) ------> 2015-04-09(str) ------> 2015-04-09(date)
                    d = '-'.join(re.findall(r"\d+", data[key]))
                    data[key] = datetime.strptime(d.strip(), '%Y-%m-%d').date()
                # 该字段为列表，列表里是字典，如
                # [{'cardNum': '3408031970****2397', 'corporationtypename': '法定代表人', 'iname': '孙剑平'}, {'cardNum': '3408031953****286X', 'corporationtypename': '法定代表人', 'iname': '刘宝玲'}]
                elif key == 'qysler':
                    data[key] = str(data[key])
                # 该字段一般为str，但有时是list需处理
                elif key == 'gistId' and isinstance(data[key], list):
                    data[key] = ' '.join(data[key])
                else:
                    if isinstance(data[key], str):
                        data[key] = data[key].strip()

            # Insert each record
            values = []
            for key in keys:
                if key not in data:
                    values.append(None)  # Some files are missing fields
                else:
                    values.append(data[key])

            values = tuple(values)
            # sql = "insert into data1 values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            # c.execute(sql, values)

    conn.commit()
    print("Records created successfully...")


def deal_data2(filepath):
    '''
        Deal with data1 files.
        :param filepath: path name
        :return: None
    '''
    data2_files = os.listdir(filepath)

    '''Create table instruments'''
    sql = '''CREATE TABLE data2
                (caseCode           TEXT  ,
                iname               CHAR(20),
                iaddress            TEXT,
                imoney              TEXT,
                ename               CHAR(20),
                courtName_phone     TEXT);'''
    c.execute(sql)
    print("Table created successfully...")
    conn.commit()

    total_num = 390355
    pbar = tqdm(total=total_num, desc='insert data2...')
    '''Save data to the database'''
    for root, dirs, files in os.walk(filepath):
        # Gets all files that are not folders
        for filename in files:
            full_path = os.path.join(root, filename)

            with open(full_path) as f:
                data = json.load(f, encoding='utf-8')

                # for key in data:
                #     if key == "执行标的金额（元）":
                #         m = re.findall(r"\d+\.*?\d*", data[key])[0]
                #         data[key] = float(m)

                # Insert each record
                values = []
                for key in data:
                    item = data[key].encode().decode('utf-8').replace(u'\xa0', ' ')
                    values.append(item)
                values = tuple(values)
                sql = "insert into data2 values(?, ?, ?, ?, ?, ?)"
                c.execute(sql, values)
                pbar.update(1)

    pbar.close()
    conn.commit()
    print("Records created successfully...")


if __name__ == '__main__':
    # print("start processing instruments..")
    # deal_instruments(instruments_path)

    print("start processing data1..")
    deal_data1(data1_path)

    # print("start processing data2..")
    # deal_data2(data2_path)

    conn.close()

import os
import Levenshtein
from tqdm import trange
from datetime import datetime
print(os.path.split(__file__))
print(type(datetime.strptime("2019-5-26", '%Y-%m-%d')))
print(Levenshtein.distance("上海徐汇人民法院", "上海市徐汇区人民法院"))
print(Levenshtein.ratio("(2017)沪0112执5984号", "(2017)沪 0112 执 5983 号"))
import sqlite3
root_path = os.path.join(os.path.split(__file__)[0], 'data')
root_path = os.path.abspath(root_path)
conn = sqlite3.connect(os.path.join(root_path, 'data.db'))
conn.text_factory = str
print("Opened database successfully...")
c = conn.cursor()
sql = "select * from instruments"
c.execute(sql)
data = c.fetchall()
conn.close()
for i in trange(len(data), desc="instruments..."):
    if "该合同系双方真实意思表示，被告没有利用强势地位强行与原告签订合同。" in data[i][9]:
        print(data[i][0])



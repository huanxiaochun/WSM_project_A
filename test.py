import os
import Levenshtein
from datetime import datetime
print(os.path.split(__file__))
print(type(datetime.strptime("2019-5-26", '%Y-%m-%d')))
print(Levenshtein.distance("上海徐汇人民法院", "上海市徐汇区人民法院"))
print(Levenshtein.ratio("(2017)沪0112执5984号", "(2017)沪 0112 执 5983 号"))

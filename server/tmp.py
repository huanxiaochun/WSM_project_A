from fuzzywuzzy import fuzz
from fuzzywuzzy import process

print(fuzz.ratio("上海徐汇人民法院", "上海市徐汇区人民法院"))
print(fuzz.ratio("上海市徐汇区人民法院", "上海市徐汇区人民法院"))
print(fuzz.ratio("(2017)沪 0112 执 5984 号", "(2017)沪 0112 执 5983 号"))
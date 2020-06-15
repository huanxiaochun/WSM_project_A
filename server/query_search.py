import sqlite3
import os
from tqdm import trange
import string
import struct
from indexer import BYTE_SIZE, IGNORE_NUMBERS, IGNORE_STOPWORDS, is_number
from zhon.hanzi import punctuation
import re
import jieba
from collections import defaultdict
import json
import codecs
import io
import math
import nltk
from utils import *
TOTAL_DOCS = 3089
THRESH = 200

DICTIONARY_FILE = os.path.join('../index', 'ins_dictionary')
POSTINGS_FILE = os.path.join('../index', 'ins_postings')

root_path = os.path.join(os.path.split(__file__)[0], '../data')
root_path = os.path.abspath(root_path)


def process_tokens(tokens):
    results = []
    stopwords = nltk.corpus.stopwords.words('chinese')
    for word in tokens:
        term = word.strip()
        if term == '':
            continue
        elif (IGNORE_STOPWORDS and term in stopwords):
            continue
        elif (IGNORE_NUMBERS and is_number(term)):
            continue
        else:
            results.append(term)
    return results


def load_dictionary():
    dict_file = codecs.open(DICTIONARY_FILE, encoding='utf-8')
    dictionary = {}                 # dictionary map loaded
    # indexed_docIDs = []             # list of all docIDs indexed
    # docIDs_processed = False        # if indexed_docIDs is processed

    # load each term along with its df and postings file pointer to dictionary
    for entry in dict_file.read().split('\n'):
        # if entry is not empty (last line in dictionary file is empty)
        if (entry):
            # print(entry)
            # print(entry[0])
            # print(entry[1])
            # print(len(entry))
            token = entry.split(" ")
            # print([len(t) for t in token])
            term = token[0]
            df = int(token[1])
            offset = int(token[2])
            dictionary[term] = (df, offset)
    return dictionary


def remove_punct(text):
    return re.sub(r"[%s]+" % (punctuation + string.punctuation), "", text)


def segment(text):
     text = text.replace(' ', '').replace('\xa0', '')
     return list(jieba.cut(text, cut_all=False))


def process_lines(lines):
    new_lines = []
    for line in lines:
        line = line.replace('\n', '').replace('\t', '').replace('\xa0', '').replace(' ', '').strip()
        new_lines.append(line)
    text = ''.join(new_lines)
    return text


def save_tfdict(doc_tfdict_path):
    doc_tfdict_path = os.path.join(doc_tfdict_path, "doc_tfdict.json")
    conn = sqlite3.connect(os.path.join(root_path, 'data.db'))
    conn.text_factory = str
    print("Opened database successfully...")
    c = conn.cursor()
    sql = "select * from instruments"
    c.execute(sql)
    data = c.fetchall()
    conn.close()
    doc_tfdict = dict()

    for i in trange(len(data), desc="instruments..."):
        tokens = []
        tfdict = defaultdict(int)
        for j in range(len(data[0])):
            if j == 0 or j == 1:  # DocID   ID
                continue
            elif j == 2 or j == 4 or j == 5 or j == 6 or j == 7 or j == 8:
                text = str(data[i][j]).strip().replace(' ', '').replace('\xa0', '')
            else:
                lines = str(data[i][j]).strip().split("\r")
                text = process_lines(lines)
            text_clean = remove_punct(text)
            tokens += segment(text_clean)
        tokens = process_tokens(tokens)
        for t in tokens:
            tfdict[t] += 1
        doc_tfdict[str(data[i][0])] = tfdict


    wf = open(doc_tfdict_path, 'w', encoding='utf-8')
    json.dump(doc_tfdict, wf, ensure_ascii=False)
    wf.close()


def query_search(query):
    doc_tfdict_path = '../index'
    doc_tfdict_path = os.path.join(doc_tfdict_path, "doc_tfdict.json")
    post_file = io.open(POSTINGS_FILE, 'rb')
    query = query.strip()
    query = remove_punct(query)
    query_tokens = segment(query)
    query_tokens = process_tokens(query_tokens)

    print(query_tokens)
    with open(doc_tfdict_path, "r",encoding='utf-8') as rf:
        doc_tfdict= json.loads(rf.read())
    dictionary = load_dictionary()

    docscore_dict = dict()
    query_tokens_new = []
    for term in query_tokens:
        if term in dictionary.keys():
            doc_list = load_posting_list(post_file, dictionary[term][0], dictionary[term][1])
            for doc in doc_list:
                docscore_dict[str(doc)] = 0
            query_tokens_new.append(term)

    for doc in docscore_dict.keys():
        tfdict = doc_tfdict[doc]
        for qt in query_tokens_new:
            if qt in tfdict.keys():
                docscore_dict[doc] += (1 + math.log(float(tfdict[qt]))) \
                                      * math.log(float(TOTAL_DOCS)/float(dictionary[qt][0]))

    docscorc_list = [(int(doc), score) for doc, score in docscore_dict.items()]

    def takeSecond(elem):
        return elem[1]

    docscorc_list.sort(key=takeSecond, reverse=True)
    Doclist = [x[0] for x in docscorc_list]
    if len(Doclist) >= THRESH:
        Doclist = Doclist[: THRESH]

    result = search_Doc(Doclist, ["instruments"])
    return result


if __name__ == '__main__':
    index_path = '../index'
    if os.path.exists(index_path):
        print("Folder %s exists." % index_path)
    else:
        try:
            print("Creating new folder: %s." % index_path)
            os.mkdir(index_path)
        except Exception as e:
            print("Creating new folder: %s."
                  % index_path)
            os.makedirs(index_path)

    # save_tfdict(index_path)
    result = query_search("该合同系双方真实意思表示，被告没有利用强势地位强行与原告签订合同。")
    print(result)

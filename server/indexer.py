#!/usr/bin/python
import nltk
import re
import sys
import getopt
import codecs
import os
import struct
import timeit
import os
import json 
import jieba
from zhon.hanzi import punctuation
import re
import argparse
from tqdm import tqdm

IGNORE_STOPWORDS = True     # toggling the option for ignoring stopwords
IGNORE_NUMBERS = False       # toggling the option for ignoring numbers
BYTE_SIZE = 4               # docID is in int


class Indexer(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.stopwords = nltk.corpus.stopwords.words('chinese')
        self.docs_indexed = 0  # counter for the number of docs indexed
        self.dictionary = {}  # key: term, value: [postings list]
        self.id2file = {}

    def remove_punct(self, text):
        return re.sub(r"[%s]+" % (punctuation + ',()'), "", text)

    def segment(self, text):
         return list(jieba.cut(text, cut_all=False))

    def process_lines(self, lines):
        new_lines = []
        for line in lines:
            line = line.replace('\n', '').replace('\t', '').replace('\xa0', '').strip()
            new_lines.append(line)
        text = ''.join(new_lines)
        return text

    def process_tokens(self, tokens, docID):
        for word in tokens:
            term = word
            if term == '':
                continue
            if (IGNORE_STOPWORDS and term in self.stopwords):
                continue
            if (IGNORE_NUMBERS and is_number(term)):
                continue
            if (term not in self.dictionary):
                self.dictionary[term] = [docID]  # define new term in in dictionary
            else:
                # if current docID is not yet in the postings list for term, append it
                if (self.dictionary[term][-1] != docID):
                    self.dictionary[term].append(docID)

    def deal_instruments(self, document_directory):
        '''
        Deal with instruments files
        :param document_directory: instruments path
        :return:
        '''
        #       id
        #       案号 *
        #       标题
        #       文书类别  *
        #       案由 *
        #       承办部门 *
        #       级别 *
        #       结案日期 *

        filenames = os.listdir(document_directory)
        for filename in tqdm(filenames, desc="Indexing instruments"):
            docID = self.docs_indexed

            filepath = os.path.join(document_directory, filename)
            self.id2file[docID] = filepath

            if (os.path.isfile(filepath)):
                fo = open(filepath, 'r', encoding='utf8')
                json_data = json.load(fo)

                tokens = []
                for key in json_data.keys():
                    if key == 'id':
                        continue
                    elif key == '案号' or key == '结案日期':
                        text = json_data[key].strip()
                        tokens.append(text)
                    else:
                        lines = json_data[key].strip().split("\r")
                        text = self.process_lines(lines)

                    text_clean = self.remove_punct(text)
                    tokens += self.segment(text_clean)

                self.process_tokens(tokens, docID)
                self.docs_indexed += 1
                fo.close()

    def deal_data1(self, document_directory):
        '''
        Deal with data1 files
        :param document_directory: data1 path
        :return: None
        '''
        #   keys = ['id', 'iname', 'caseCode', 'age', 'sexy',
        #   'cardNum', 'courtName', 'areaName', 'partyTypeName',
        #   'gistId', 'regDate', 'gistUnit', 'duty', 'performance',
        #   'performedPart', 'unperformPart', 'disruptTypeName',
        #   'publishDate', 'qysler']

        filenames = os.listdir(document_directory)
        for filename in tqdm(filenames, desc="Indexing data1"):
            docID = self.docs_indexed

            filepath = os.path.join(document_directory, filename)
            self.id2file[docID] = filepath

            if (os.path.isfile(filepath)):
                fo = open(filepath, 'r', encoding='utf8')
                json_data = json.load(fo)

                tokens = []
                for key in json_data.keys():
                    if key == 'id' or key == 'partyTypeName':
                        continue
                    elif key =='iname' or key == 'caseCode' or key == 'regDate' or key == 'publishDate':
                        text = json_data[key].strip()
                        tokens.append(text)
                    # 该字段为列表，列表里是字典，如
                    # [{'cardNum': '3408031970****2397', 'corporationtypename': '法定代表人',
                    # 'iname': '孙剑平'}, {'cardNum': '3408031953****286X',
                    # 'corporationtypename': '法定代表人', 'iname': '刘宝玲'}]
                    elif key == 'qysler':
                        text = str(json_data[key])
                    # 该字段一般为str，但有时是list需处理
                    elif key == 'gistId':
                        if isinstance(json_data[key], list):
                            tokens += json_data[key]
                            text = ''.join(json_data[key])
                        else:
                            text = json_data[key].strip()
                    else:
                        lines = str(json_data[key]).strip().split("\r")
                        text = self.process_lines(lines)

                    text_clean = self.remove_punct(text)
                    tokens += self.segment(text_clean)

                self.process_tokens(tokens, docID)
                self.docs_indexed += 1
                fo.close()

    def deal_data2(self, document_directory):
        '''
        Deal with data2 files
        :param document_directory: data2 path
        :return: None
        '''
        #   keys = ['案号', '被执行人', '被执行人地址', '执行标的金额（元）', '申请执行人', '承办法院、联系电话']

        filenames = os.listdir(document_directory)
        for filename in tqdm(filenames, desc="Indexing data2"):
            docID = self.docs_indexed

            filepath = os.path.join(document_directory, filename)
            self.id2file[docID] = filepath

            if (os.path.isfile(filepath)):
                fo = open(filepath, 'r', encoding='utf8')
                json_data = json.load(fo)

                tokens = []
                for key in json_data.keys():
                    if key == '案号' or key == '执行标的金额（元）':
                        text = json_data[key].strip()
                        tokens.append(text)
                    else:
                        lines = json_data[key].strip().split("\r")
                        text = self.process_lines(lines)

                    text_clean = self.remove_punct(text)
                    tokens += self.segment(text_clean)

                self.process_tokens(tokens, docID)
                self.docs_indexed += 1
                fo.close()

    def create_index(self, documents):
        '''
        Create index
        :param documents: List[tuple(str, str)]
        :return: None
        '''
        for document_directory, document_type in documents:
            if document_type == 'instruments':
                self.deal_instruments(document_directory)
            elif document_type == 'data1':
                self.deal_data1(document_directory)
            elif document_type == 'data2':
                self.deal_data2(document_directory)
            else:
                pass

    def save_index(self, index_directory):
        '''
        Save index files:
            dictionary:    dictionary of terms with corresponding document frequencies and offsets
            postings:      postings file for all terms in dictionary
            id2file.json:  mapping docIDs to filepaths
        :param index_directory: where to save the index files
        :return: None
        '''
        # open files for writing
        dict_file = codecs.open(os.path.join(index_directory, 'dictionary'), 'w', encoding='utf-8')
        post_file = open(os.path.join(index_directory, 'postings'), 'wb')

        byte_offset = 0 # byte offset for pointers to postings file

        # build dictionary file and postings file
        for term, postings_list in self.dictionary.items():
            df = len(postings_list)                     # document frequency is the same as length of postings list
        
            # write each posting into postings file
            for docID in postings_list:
                posting = struct.pack('I', docID)   # pack docID into a byte array of size 4
                post_file.write(posting)

            # write to dictionary file and update byte offset
            dict_file.write(term + " " + str(df) + " " + str(byte_offset) + "\n")
            byte_offset += BYTE_SIZE * df


        with open(os.path.join(index_directory, 'id2file.json'), 'w') as f:
            json.dump(self.id2file, f)

        # close files
        dict_file.close()
        post_file.close()

        print('# indexed documents = ', self.docs_indexed)


if __name__ == '__main__':

    index_path = '../index'
    instruments_path = '../data/instruments'
    data1_path = '../data/data1'
    data2_path = '../data/data2'

    if os.path.exists(index_path):
        print("Folder %s exists." % index_path)
    else:
        try:
            print("Creating new folder: %s." % index_path)
            os.mkdir(index_path)
        except Exception as e:
            print("Creating new folder: %s." % index_path)
            os.makedirs(index_path)

    indexer = Indexer()
    # indexer.create_index([(data1_path, 'data1'), (data2_path, 'data2')])
    indexer.create_index([(instruments_path, 'instruments')])
    indexer.save_index(index_path)

    # 2020.06.09

#!/usr/bin/python
import nltk
import re
import codecs
import struct
import string
import os
import jieba
from zhon.hanzi import punctuation
import re
import sqlite3
from tqdm import trange

IGNORE_STOPWORDS = True      # toggling the option for ignoring stopwords
IGNORE_NUMBERS = False       # toggling the option for ignoring numbers
BYTE_SIZE = 4                # docID is in int

root_path = os.path.join(os.path.split(__file__)[0], '../data')
root_path = os.path.abspath(root_path)

conn = sqlite3.connect(os.path.join(root_path, 'data.db'))
conn.text_factory = str
print("Opened database successfully...")
c = conn.cursor()


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


class Indexer(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.stopwords = nltk.corpus.stopwords.words('chinese')
        self.dictionary = {}    # key: term, value: [postings list]

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
            term = word.strip()
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

    def deal_instruments(self, table_name):
        '''
        Deal with instruments files
        :param table_name: instruments table name
        :return:
        '''
        # ["DocID", "ID", "caseCode", "Title", "Type", "Cause", "Department", "Level", "ClosingDate", "Content"]

        sql = "select * from " + table_name
        c.execute(sql)
        data = c.fetchall()

        for i in trange(len(data), desc="instruments..."):
            tokens = []
            for j in range(len(data[0])):
                if j == 0 or j == 1:  # DocID   ID
                    continue
                elif j == 2 or j == 4 or j == 5 or j == 6 or j == 7 or j == 8:
                    text = str(data[i][j]).strip()
                    tokens.append(text)
                else:
                    lines = str(data[i][j]).strip().split("\r")
                    text = self.process_lines(lines)

                text_clean = self.remove_punct(text)
                tokens += self.segment(text_clean)

            self.process_tokens(tokens, data[i][0])

    def deal_data1(self, table_name):
        '''
        Deal with data1 files
        :param document_directory: data1 table name
        :return: None
        '''
        #   keys = ['DocID', 'ID', 'iname', 'caseCode', 'age', 'sexy',
        #   'cardNum', 'businessEntity', 'courtName', 'areaName', 'partyTypeName',
        #   'gistId', 'regDate', 'gistUnit', 'duty', 'performance',
        #   'performedPart', 'unperformPart', 'disruptTypeName',
        #   'publishDate', 'qysler']

        sql = "select * from " + table_name
        c.execute(sql)
        data = c.fetchall()

        for i in trange(len(data), desc="data1..."):
            tokens = []
            for j in range(len(data[0])):
                if j == 0 or j == 1 or j == 10:  # DocID   ID   partyTypeName
                    continue
                elif j == 2 or j == 3 or j == 8 or j == 9 or j == 12 or j == 13 or j == 15 or j == 19:
                    text = str(data[i][j]).strip()
                    tokens.append(text)
                elif j == 11:  # gistId
                    text = data[i][j].strip()
                    tokens += text.split()
                else:
                    lines = str(data[i][j]).strip().split("\r")
                    text = self.process_lines(lines)

                text_clean = self.remove_punct(text)
                tokens += self.segment(text_clean)

            self.process_tokens(tokens, data[i][0])

    def deal_data2(self, table_name):
        '''
        Deal with data2 files
        :param document_directory: data2 table name
        :return: None
        '''
        #   keys = ['DocID', 'caseCode', 'iname', 'iaddress', 'imoney', 'ename', 'courtName_phone']

        sql = "select * from " + table_name
        c.execute(sql)
        data = c.fetchall()

        for i in trange(len(data), desc="data2..."):
            tokens = []
            for j in range(len(data[0])):
                if j == 0:  # DocID
                    continue
                elif j == 1 or j == 2 or j == 5:
                    text = str(data[i][j]).strip()
                    tokens.append(text)
                elif j == 6:  # courtName_phone  only save court name
                    text = data[i][j].strip().split()[0]
                    tokens.append(text)
                else:
                    lines = str(data[i][j]).strip().split("\r")
                    text = self.process_lines(lines)

                text_clean = self.remove_punct(text)
                tokens += self.segment(text_clean)

            self.process_tokens(tokens, data[i][0])

    def create_index(self, documents):
        '''
        Create index
        :param documents: List[tuple(str, str)]
        :return: None
        '''
        for table_name, document_type in documents:
            if document_type == 'instruments':
                self.deal_instruments(table_name)
            elif document_type == 'data1':
                self.deal_data1(table_name)
            elif document_type == 'data2':
                self.deal_data2(table_name)
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

        byte_offset = 0      # byte offset for pointers to postings file

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

        # close files
        dict_file.close()
        post_file.close()


if __name__ == '__main__':
    index_path = '../index'
    instruments_table = "instruments"
    data1_table = "data1"
    data2_table = "data2"

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
    indexer.create_index([(data1_table, 'data1'), (data2_table, 'data2')])
    # indexer.create_index([(instruments_table, 'instruments')])
    indexer.save_index(index_path)

    # 2020.06.09

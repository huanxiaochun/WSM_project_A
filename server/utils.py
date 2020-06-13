#!/usr/bin/python
import re
import nltk
import sys
import getopt
import codecs
import struct
import math
import io
import collections
import timeit
import argparse
import os
import json
import sqlite3

RECORD_TIME = False # toggling for recording the time taken for indexer
BYTE_SIZE = 4       # docID is in int

root_path = os.path.join(os.path.split(__file__)[0], '../data')
root_path = os.path.abspath(root_path)


def load_dictionary(dict_file):
    '''
    load dictionary
    :param dict_file: opened dictionary file
    :return: (dictionary, indexed_docIDs)
    '''
    dictionary = {}                 # dictionary map loaded
    indexed_docIDs = []             # list of all docIDs indexed

    # load each term along with its df and postings file pointer to dictionary
    for entry in dict_file.read().split('\n'):
        # if entry is not empty (last line in dictionary file is empty)
        if (entry):
            token = entry.split(" ")
            term = token[0]
            df = int(token[1])
            offset = int(token[2])
            dictionary[term] = (df, offset)

    return (dictionary, indexed_docIDs)


def load_posting_list(post_file, length, offset):
    '''
    returns posting list for term corresponding to the given offset
    :param post_file: opened postings file
    :param length: length of posting list (same as df for the term)
    :param offset: byte offset which acts as pointer to start of posting list in postings file
    :return: posting_list
    '''
    post_file.seek(offset)
    posting_list = []
    for i in range(length):
        posting = post_file.read(BYTE_SIZE)
        docID = struct.unpack('I', posting)[0]
        posting_list.append(docID)
    return posting_list


def search_Doc(Dlist, table_name_list):
    conn = sqlite3.connect(os.path.join(root_path, 'data.db'))
    conn.text_factory = str
    print("Opened database successfully...")
    c = conn.cursor()

    str_list = str(tuple(Dlist))
    if len(Dlist) == 1:
        str_list = str_list.replace(",", "")


    # query
    if len(table_name_list) == 1:
        sql = "select * from " + table_name_list[0] + " where DocID in " + str_list
        c.execute(sql)
        data = c.fetchall()
        conn.close()
        return data
    else:   # others
        result = {}
        for table_name in table_name_list:
            sql = "select * from " + table_name + " where DocID in " + str_list
            c.execute(sql)
            data = c.fetchall()
            result[table_name] = data

        conn.close()
        return result


def process_query(query, dictionary, post_file, indexed_docIDs):
    '''
    returns the list of docIDs in the result for the given query
    :param query: the query string e.g. '中国 OR 人民 AND (法院 OR 检察) AND NOT 上海'
    :param dictionary:
    :param post_file: the dictionary in memory
    :param indexed_docIDs: the list of all docIDs indexed (used for negations)
    :return: list of docIDs
    '''
    stemmer = nltk.stem.porter.PorterStemmer() # instantiate stemmer
    # prepare query list
    query = query.replace(' ', '')
    query = query.replace('AND', ' AND ')
    query = query.replace('OR', ' OR ')
    query = query.replace('NOT', 'NOT ')
    query = query.replace('(', '( ')
    query = query.replace(')', ' )')
    query = query.split(' ')

    results_stack = []
    postfix_queue = collections.deque(shunting_yard(query)) # get query in postfix notation as a queue
#     print (postfix_queue)

    while postfix_queue:
        token = postfix_queue.popleft()
        result = [] # the evaluated result at each stage
        # if operand, add postings list for term to results stack
        if (token != 'AND' and token != 'OR' and token != 'NOT'):
            if (token in dictionary):
                result = load_posting_list(post_file, dictionary[token][0], dictionary[token][1])
        # else if AND operator
        elif (token == 'AND'):
            right_operand = results_stack.pop()
            left_operand = results_stack.pop()
            # print(left_operand, 'AND', left_operand) # check
            result = boolean_AND(left_operand, right_operand)   # evaluate AND

        # else if OR operator
        elif (token == 'OR'):
            right_operand = results_stack.pop()
            left_operand = results_stack.pop()
            # print(left_operand, 'OR', left_operand) # check
            result = boolean_OR(left_operand, right_operand)    # evaluate OR

        # else if NOT operator
        elif (token == 'NOT'):
            right_operand = results_stack.pop()
            # print('NOT', right_operand) # check
            result = boolean_NOT(right_operand, indexed_docIDs) # evaluate NOT

        # push evaluated result back to stack
        results_stack.append(result)                        
        # print ('result', result) # check

    # NOTE: at this point results_stack should only have one item and it is the final result
    if len(results_stack) != 1:
        print ("ERROR: results_stack. Please check valid query") # check for errors

    result = search_Doc(results_stack.pop(), ["data1", "data2"])
    return result


def shunting_yard(infix_tokens):
    '''
    returns the list of postfix tokens converted from the given infix expression
    :param infix_tokens: list of tokens in original query of infix notation
    :return:
    '''
    # define precedences
    precedence = {}
    precedence['NOT'] = 3
    precedence['AND'] = 2
    precedence['OR'] = 1
    precedence['('] = 0
    precedence[')'] = 0    

    # declare data strucures
    output = []
    operator_stack = []

    # while there are tokens to be read
    for token in infix_tokens:
        
        # if left bracket
        if (token == '('):
            operator_stack.append(token)
        
        # if right bracket, pop all operators from operator stack onto output until we hit left bracket
        elif (token == ')'):
            operator = operator_stack.pop()
            while operator != '(':
                output.append(operator)
                operator = operator_stack.pop()
        
        # if operator, pop operators from operator stack to queue if they are of higher precedence
        elif (token in precedence):
            # if operator stack is not empty
            if (operator_stack):
                current_operator = operator_stack[-1]
                while (operator_stack and precedence[current_operator] > precedence[token]):
                    output.append(operator_stack.pop())
                    if (operator_stack):
                        current_operator = operator_stack[-1]

            operator_stack.append(token) # add token to stack
        
        # else if operands, add to output list
        else:
            output.append(token.lower())

    # while there are still operators on the stack, pop them into the queue
    while (operator_stack):
        output.append(operator_stack.pop())
    # print ('postfix:', output)  # check
    return output


def boolean_NOT(right_operand, indexed_docIDs):
    '''
    returns the list of docIDs which is the compliment of given right_operand
    :param right_operand: sorted list of docIDs to be complimented
    :param indexed_docIDs: sorted list of all docIDs indexed
    :return:
    '''
    # complement of an empty list is list of all indexed docIDs
    if (not right_operand):
        return indexed_docIDs
    
    result = []
    r_index = 0 # index for right operand
    for item in indexed_docIDs:
        # if item do not match that in right_operand, it belongs to compliment 
        if (item != right_operand[r_index]):
            result.append(item)
        # else if item matches and r_index still can progress, advance it by 1
        elif (r_index + 1 < len(right_operand)):
            r_index += 1
    return result


def boolean_OR(left_operand, right_operand):
    '''
    returns list of docIDs that results from 'OR' operation between left and right operands
    :param left_operand: docID list on the left
    :param right_operand: docID list on the right
    :return:
    '''
    result = []     # union of left and right operand
    l_index = 0     # current index in left_operand
    r_index = 0     # current index in right_operand

    # while lists have not yet been covered
    while (l_index < len(left_operand) or r_index < len(right_operand)):
        # if both list are not yet exhausted
        if (l_index < len(left_operand) and r_index < len(right_operand)):
            l_item = left_operand[l_index]  # current item in left_operand
            r_item = right_operand[r_index] # current item in right_operand
            
            # case 1: if items are equal, add either one to result and advance both pointers
            if (l_item == r_item):
                result.append(l_item)
                l_index += 1
                r_index += 1

            # case 2: l_item greater than r_item, add r_item and advance r_index
            elif (l_item > r_item):
                result.append(r_item)
                r_index += 1

            # case 3: l_item lower than r_item, add l_item and advance l_index
            else:
                result.append(l_item)
                l_index += 1

        # if left_operand list is exhausted, append r_item and advance r_index
        elif (l_index >= len(left_operand)):
            r_item = right_operand[r_index]
            result.append(r_item)
            r_index += 1

        # else if right_operand list is exhausted, append l_item and advance l_index 
        else:
            l_item = left_operand[l_index]
            result.append(l_item)
            l_index += 1

    return result


def boolean_AND(left_operand, right_operand):
    '''
    returns list of docIDs that results from 'AND' operation between left and right operands
    :param left_operand: docID list on the left
    :param right_operand: docID list on the right
    :return:
    '''
    # perform 'merge'
    result = []                                 # results list to be returned
    l_index = 0                                 # current index in left_operand
    r_index = 0                                 # current index in right_operand
    l_skip = int(math.sqrt(len(left_operand)))  # skip pointer distance for l_index
    r_skip = int(math.sqrt(len(right_operand))) # skip pointer distance for r_index

    while (l_index < len(left_operand) and r_index < len(right_operand)):
        l_item = left_operand[l_index]  # current item in left_operand
        r_item = right_operand[r_index] # current item in right_operand
        
        # case 1: if match
        if (l_item == r_item):
            result.append(l_item)   # add to results
            l_index += 1            # advance left index
            r_index += 1            # advance right index
        
        # case 2: if left item is more than right item
        elif (l_item > r_item):
            # if r_index can be skipped (if new r_index is still within range and resulting item is <= left item)
            if (r_index + r_skip < len(right_operand)) and right_operand[r_index + r_skip] <= l_item:
                r_index += r_skip
            # else advance r_index by 1
            else:
                r_index += 1

        # case 3: if left item is less than right item
        else:
            # if l_index can be skipped (if new l_index is still within range and resulting item is <= right item)
            if (l_index + l_skip < len(left_operand)) and left_operand[l_index + l_skip] <= r_item:
                l_index += l_skip
            # else advance l_index by 1
            else:
                l_index += 1

    return result


# index_path = '../tmp/index'
# dictionary, indexed_docIDs, id2file = load_files(index_path)
# post_file = io.open(os.path.join(index_path, 'postings'), 'rb')
#
# token = '中国'
# result = load_posting_list(post_file, dictionary[token][0], dictionary[token][1])
# print(len(result))
# print(len(set(result)))
# query =（2017）沪0104民初19331号OR (法院 OR 上海)NOT 检察 AND 人民

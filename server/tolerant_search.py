#!/usr/bin/python
# coding=gbk
from indexer import BYTE_SIZE
import struct
import codecs
import io
import Levenshtein
import collections
import math
import os
DICTIONARY_FILE = os.path.join('../index', 'dictionary')
POSTINGS_FILE = os.path.join('../index', 'postings')
TOLERANT_THRESHOLD = 70
INDEXED_DOCIDS = 1636926

def load_posting_list(post_file, length, offset):
    post_file.seek(offset)
    posting_list = []
    for i in range(length):
        posting = post_file.read(BYTE_SIZE)
        docID = struct.unpack('I', posting)[0]
        posting_list.append(docID)
    return posting_list


def load_dictionary(dict_file):
    dictionary = {}                 # dictionary map loaded
    # indexed_docIDs = []             # list of all docIDs indexed
    # docIDs_processed = False        # if indexed_docIDs is processed

    # load each term along with its df and postings file pointer to dictionary
    for entry in dict_file.read().split('\n'):
        # if entry is not empty (last line in dictionary file is empty)
        if (entry):
            print(entry.replace(' ', ''))
            print(len(entry))
            token = entry.split(" ")
            print(token)
            term = token[0]
            df = int(token[1])
            offset = int(token[2])
            dictionary[term] = (df, offset)

    return dictionary


def tolerant_search(query):
    # open files
    dict_file = codecs.open(DICTIONARY_FILE, encoding='utf-8')
    post_file = io.open(POSTINGS_FILE, 'rb')
    # load dictionary to memory
    dictionary = load_dictionary(dict_file)
    dict_file.close()
    code, result = process_query(query, dictionary, post_file)
    # close files
    post_file.close()
    if code == 0:
        return code, result
    else:
        def takeSecond(elem):
            return elem[0]
        result.sort(key=takeSecond)
        return code, [x[0] for x in result]


def get_similar_score(token, term):
    return Levenshtein.ratio(token, term)


def get_similar_docscorc_list(token, dictionary, postfile):
    result = []
    docscorc_dict = dict()
    for term in dictionary.keys():
        score = get_similar_score(token, term)
        if score > TOLERANT_THRESHOLD:
            result.append(term)
            doc_list = load_posting_list(postfile, dictionary[term][0], dictionary[term][1])
            for doc in doc_list:
                if str(doc) not in docscorc_dict.keys() or docscorc_dict[str(doc)] < score:
                    docscorc_dict[str(doc)] = score
    docscorc_list = [(int(doc), score) for doc, score in docscorc_dict.items()]
    def takeFirst(elem):
        return elem[0]
    docscorc_list.sort(key=takeFirst)
    return docscorc_list


def shunting_yard(infix_tokens):
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

            operator_stack.append(token)  # add token to stack

        # else if operands, add to output list
        else:
            output.append(token.lower())

    # while there are still operators on the stack, pop them into the queue
    while (operator_stack):
        output.append(operator_stack.pop())
    # print ('postfix:', output)  # check
    return output


def process_query(query, dictionary, post_file):
    # stemmer = nltk.stem.porter.PorterStemmer()  # instantiate stemmer
    # prepare query list
    query = query.replace(' ', '')
    query = query.replace('AND', ' AND ')
    query = query.replace('OR', ' OR ')
    query = query.replace('NOT', ' NOT ')
    query = query.replace('(', '( ')
    query = query.replace(')', ' )')
    query_old = query.split(' ')
    query = [x for x in query_old if x.strip()]  # 去掉空值

    results_stack = []
    postfix_queue = collections.deque(shunting_yard(query))  # get query in postfix notation as a queue

    while postfix_queue:
        token = postfix_queue.popleft()
        result = []  # the evaluated result at each stage
        # if operand, add postings list for term to results stack
        if (token != 'AND' and token != 'OR' and token != 'NOT'):
            # token = stemmer.stem(token)  # stem the token
            # default empty list if not in dictionary
            if (token in dictionary):
                result = get_similar_docscorc_list(token, dictionary, post_file)
                # result = load_posting_list(post_file, dictionary[token][0], dictionary[token][1])

        # else if AND operator
        elif (token == 'AND'):
            right_operand = results_stack.pop()
            left_operand = results_stack.pop()
            # print(left_operand, 'AND', left_operand) # check
            result = boolean_AND(left_operand, right_operand)  # evaluate AND

        # else if OR operator
        elif (token == 'OR'):
            right_operand = results_stack.pop()
            left_operand = results_stack.pop()
            # print(left_operand, 'OR', left_operand) # check
            result = boolean_OR(left_operand, right_operand)  # evaluate OR

        # else if NOT operator
        elif (token == 'NOT'):
            right_operand = results_stack.pop()
            # print('NOT', right_operand) # check
            result = boolean_NOT(right_operand, INDEXED_DOCIDS)  # evaluate NOT

        # push evaluated result back to stack
        results_stack.append(result)
        # print ('result', result) # check

    # NOTE: at this point results_stack should only have one item and it is the final result
    if len(results_stack) != 1:
        print("ERROR: results_stack. Please check valid query")  # check for errors
        return 0, "ERROR: results_stack. Please check valid query"
    else:
        return 1, results_stack.pop()


def boolean_AND(left_list, right_list):
    docscore_list = []
    left_operand = [x[0] for x in left_list]
    right_operand = [x[0] for x in right_list]
    # perform 'merge'
    # result = []  # results list to be returned
    l_index = 0  # current index in left_operand
    r_index = 0  # current index in right_operand
    l_skip = int(math.sqrt(len(left_operand)))  # skip pointer distance for l_index
    r_skip = int(math.sqrt(len(right_operand)))  # skip pointer distance for r_index

    while (l_index < len(left_operand) and r_index < len(right_operand)):
        l_item = left_operand[l_index]  # current item in left_operand
        r_item = right_operand[r_index]  # current item in right_operand

        # case 1: if match
        if (l_item == r_item):
            # result.append(l_item)  # add to results
            l_index += 1  # advance left index
            r_index += 1  # advance right index
            score = min(left_list[l_index][1], right_list[r_index][1])
            docscore_list.append((l_item, score))

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

    return docscore_list


def boolean_OR(left_list, right_list):
    docscore_list = []
    left_operand = [x[0] for x in left_list]
    right_operand = [x[0] for x in right_list]
    # result = []  # union of left and right operand
    l_index = 0  # current index in left_operand
    r_index = 0  # current index in right_operand

    # while lists have not yet been covered
    while (l_index < len(left_operand) or r_index < len(right_operand)):
        # if both list are not yet exhausted
        if (l_index < len(left_operand) and r_index < len(right_operand)):
            l_item = left_operand[l_index]  # current item in left_operand
            r_item = right_operand[r_index]  # current item in right_operand

            # case 1: if items are equal, add either one to result and advance both pointers
            if (l_item == r_item):
                # result.append(l_item)
                l_index += 1
                r_index += 1
                score = max(left_list[l_index][1], right_list[r_index][1])
                docscore_list.append((l_item, score))

            # case 2: l_item greater than r_item, add r_item and advance r_index
            elif (l_item > r_item):
                # result.append(r_item)
                r_index += 1
                docscore_list.append(right_list[r_index])


            # case 3: l_item lower than r_item, add l_item and advance l_index
            else:
                # result.append(l_item)
                l_index += 1
                docscore_list.append(left_list[l_index])

        # if left_operand list is exhausted, append r_item and advance r_index
        elif (l_index >= len(left_operand)):
            r_item = right_operand[r_index]
            # result.append(r_item)
            r_index += 1
            docscore_list.append(right_list[r_index])


        # else if right_operand list is exhausted, append l_item and advance l_index
        else:
            l_item = left_operand[l_index]
            # result.append(l_item)
            l_index += 1
            docscore_list.append(left_list[l_index])
    return docscore_list


def boolean_NOT(right_list, indexed_docIDs):
    # complement of an empty list is list of all indexed docIDs
    docscore_list = []
    right_operand = [x[0] for x in right_list]
    if (not right_operand):
        return [(x, 0) for x in range(1, indexed_docIDs+1)]

    # result = []
    r_index = 0  # index for right operand
    for item in range(1, indexed_docIDs+1):
        # if item do not match that in right_operand, it belongs to compliment
        if (item != right_operand[r_index]):
            docscore_list.append((item, 0))
        # else if item matches and r_index still can progress, advance it by 1
        elif (r_index + 1 < len(right_operand)):
            r_index += 1
    return docscore_list


if __name__ == '__main__':
    result = tolerant_search("上海徐汇人民法院 AND（2017）沪0112执5983号")
    print(result)

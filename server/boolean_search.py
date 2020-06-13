from utils import *

if __name__ == '__main__':
    index_path = '/path/to/index'
    dictionary, indexed_docIDs = load_files(index_path)
    post_file = io.open(os.path.join(index_path, 'postings'), 'rb')

    value = '（2017）沪0104民初19331号OR (法院OR上海) AND NOT 人民'
    result = process_query(value, dictionary, post_file, indexed_docIDs)

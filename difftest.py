from itertools import combinations
from functools import reduce
import htmltreediff
from bs4 import BeautifulSoup as Soup
from difflib import *
import os


def get_tree(file):
    content = open('samples/' + file).read()
    soup = Soup(content, 'html5lib')
    body = soup.find('body')
    body.parent = None
    return body


def reducer(acc, x):
    matcher = SequenceMatcher(a=x, b=acc)
    opcodes = matcher.get_opcodes()
    print(x, acc, [(op, x[i1:i2], acc[j1:j2]) for op, i1, i2, j1, j2 in opcodes])
    equal = filter(lambda x: x[0] == 'equal', opcodes)
    equal = [x[i1:i2] for _, i1, i2, j1, j2 in equal]
    return sum(equal, [])


def temp_diff(a, b):
    matcher = SequenceMatcher(a=a, b=b)
    opcodes = matcher.get_opcodes()
    print(a, b, [(op, a[i1:i2], b[j1:j2]) for op, i1, i2, j1, j2 in opcodes])
    # equal = filter(lambda x: x[0] == 'equal', opcodes)
    # equal = [x[i1:i2] for _, i1, i2, j1, j2 in equal]
    # return sum(equal, [])


def get_buckets(common, children):
    a = 0
    bucket = []
    result = []
    for child in children:
        if a == len(common) or child != common[a]:
            bucket.append(child)
        else:
            result.append(bucket)
            bucket = []
            a += 1
    result.append(bucket)
    return result


def similarity(a, b):
    if a.name != b.name: return 0


def process_bucket(bucket):
    return bucket


def mark_version(buckets, i):
    for bucket in buckets:
        for child in bucket:
            child.version = i


def merge_lists(lists, versions):
    lists = list(filter(None, lists))
    if not lists:
        return lists
    common = reduce(reducer, lists, lists[0])
    if not common:
        return lists
    bucket_lists = [get_buckets(common, lst) for lst in lists]
    for i, buckets in enumerate(bucketlists):
        mark_version(buckets, i)
    buckets = [sum(i, []) for i in zip(*bucketlists)]
    commons = [extract_common(bucket) for bucket in buckets]
    return [[el] + sum(lst, []) for el, lst in zip([None] + common, commons)][1:]


def simplify_buckets():
    pass


def superdiff(roots):
    root_children = [[child for child in root.children if str(child) != '\n'] for root in roots]

    rc = root_children
    temp_diff(rc[0], rc[1])
    temp_diff(rc[1], rc[2])
    temp_diff(rc[2], rc[0])
    return

    common = reduce(reducer, root_children, root_children[0])
    ibuckets = [get_buckets(common, children) for children in root_children]
    for i, buckets in enumerate(ibuckets): mark_version(buckets, i)
    buckets = [sum(i, []) for i in zip(*ibuckets)]
    buckets = [process_bucket(bucket) for bucket in buckets]
    result = sum(([a] + b for a, b in zip([None] + common, buckets)), [])[1:]
    print('result:', result)
    print('common:', common)
    print('buckets:', buckets)


if __name__ == '__main__':
    files = os.listdir('samples')[:3]
    roots = [get_tree(file) for file in files]
    superdiff(roots)

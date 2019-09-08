from itertools import combinations
from functools import reduce
import htmltreediff
from bs4 import BeautifulSoup as Soup, Tag
from difflib import *
import copy
import os




def get_tree(file):
    content = open('samples/' + file).read()
    soup = Soup(content, 'html5lib')
    body = soup.find('body')
    body.parent = None
    body.soup = soup
    return body


def reducer(acc, x):
    print('red', x, acc)
    matcher = SequenceMatcher(a=x, b=acc)
    opcodes = matcher.get_opcodes()
    print('op:', opcodes)
    equal = filter(lambda x: x[0] == 'equal', opcodes)
    equal = [x[i1:i2] for _, i1, i2, j1, j2 in equal]
    print('redd', equal)
    return sum(equal, [])


def get_buckets(common, children, comp):
    a = 0
    bucket = []
    result = []
    for child in children:
        if a == len(common) or not comp(child, common[a]):
            bucket.append(child)
        else:
            result.append(bucket)
            bucket = []
            a += 1
    result.append(bucket)
    return result


def similarity(a, b):
    # print('*', a, b, a.name, b.name, a.version, b.version)
    if a.version == b.version: return 0
    if a.name != b.name: return 0
    if hash(a) == hash(b): return 1
    vchildren = [[child for child in root.children if str(child).strip()] for root in [a, b]]
    common = list(reduce(reducer, vchildren, vchildren[0]))
    return len(common) / (len(sum(vchildren, [])) / 2)


def process_bucket(buckets):
    if not sum(buckets, []): return buckets
    print('process start')
    print('buckets:', buckets)
    eq = lambda self, other: similarity(self, other) > 0.6
    items = sum(buckets, [])
    xitems = items[:]
    groups = []
    while xitems:
        target = xitems.pop(0)
        similar = list(filter(lambda ix: eq(target, ix[1]), enumerate(xitems)))
        groups.append([target] + [x for _, x in similar])
        for i, _ in reversed(similar): del xitems[i]
    print('groups:', groups)
    for i, group in enumerate(groups):
        for item in group:
            item.hash = i

    patched_buckets = []
    for bucket in buckets:
        patched_bucket = []
        for item in bucket:
            patched_bucket.append(
                type('_', (), {
                    'item': item,
                    '__hash__': lambda _, item=item: item.hash,
                    '__repr__': lambda _, item=item: '@' + str(item) + ' hash: ' + str(item.hash) + ' @',
                    '__eq__': lambda _, other, item=item: item.hash == hash(other),
                })()
            )
        patched_buckets.append(patched_bucket)
    common = reduce(reducer, patched_buckets, patched_buckets[0])
    print('>>>', common)
    xgroups = groups[:]

    # COMMON
    comm_groups = [hash(item) for item in common]
    xcomm_groups = comm_groups[:]
    comm_groups.sort()
    common = [superdiff(xgroups[hash(item)]) for item in common]
    print('comm groups:', comm_groups)
    for i in reversed(comm_groups): del xgroups[i]

    # NEW
    new = [group[0] for group in xgroups if len(group) == 1]
    for item in new: item.attrs['class'] = 'new'
    new_groups = [i for i, x in enumerate(xgroups) if len(x) == 1]
    new_groups.sort()
    print('groups:', xgroups)
    print('new groups:', new_groups)
    for i in reversed(new_groups): del xgroups[i]

    # OTHER
    print('ONLY LEFT GROUPS:', xgroups)
    other = xgroups
    for group in xgroups:
        for item in group: item.attrs['class'] = 'other'
        kok = superdiff(group)

    for item, group in zip(common, xcomm_groups): item.group = group
    new_buckets = [get_buckets(common, children, lambda a, b: hash(a) == b.group) for children in patched_buckets]
    print('new buckets:', new_buckets)
        
    return buckets


def mark_version(buckets, i):
    for bucket in buckets:
        for child in bucket:
            child.version = i


def superdiff(roots):
    print('name:', roots[0].name)
    vchildren = [[child for child in root.children if str(child).strip()] for root in roots]
    common = reduce(reducer, vchildren, vchildren[0])
    vbuckets = [get_buckets(common, children, lambda a, b: a == b) for children in vchildren]
    for i, buckets in enumerate(vbuckets): mark_version(buckets, i)
    buckets = [process_bucket(list(bucket)) for bucket in zip(*vbuckets)]
    result = sum(([a] + b for a, b in zip([None] + common, buckets)), [])[1:]

    print('result:', result)
    print('common:', common)
    print('buckets:', buckets)

    global soup
    root = soup.new_tag(roots[0].name)
    flat = []
    for something in result:
        if type(something) == list: flat.extend(something)
        else: flat.append(something)
    for item in flat: root.append(copy.copy(item))

    return root


soup = Soup(features='html5lib')


if __name__ == '__main__':
    files = os.listdir('samples')[:3]
    roots = [get_tree(file) for file in files]
    kok = superdiff(roots)
    print(kok)

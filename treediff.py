from bs4 import BeautifulSoup as Soup, NavigableString as Text, Tag
from difflib import SequenceMatcher
from shutil import copyfile
import copy
import os

THRESHOLD = 0.6


def is_atom(node):
    if node.attrs.get('data-atom'): return True
    if node.name in ['li', 'td', 'th']: return True
    # if node.get('class') == 'text-wrapper': return True
    return False


def reducer(a, b):
    # assert a.attrs.get('class') != 'text-wrapper'
    matcher = SequenceMatcher(a=a, b=b)
    opcodes = matcher.get_opcodes()
    # print('matching:', a, b)
    # print('opcodes:', opcodes)
    equal = filter(lambda x: x[0] == 'equal', opcodes)
    equal = [a[i1:i2] for _, i1, i2, j1, j2 in equal]
    return sum(equal, [])


def flatten_children(root, no_versions=False):
    children = [child for child in root.children if str(child).strip()]
    if root.name in ['table', 'tbody', 'thead', 'tfoot'] and no_versions:
        children = root.find_all('td') + root.find_all('th')
    if root.name in ['table', 'thead', 'tbody', 'tfoot']:
        for tr in root.find_all('tr'):
            for i, td in enumerate(tr.find_all('td') + tr.find_all('th')):
                td['data-index'] = i
    result = []
    for child in children:
        if child.name is None:
            if no_versions: continue
            soup = Soup(features='html5lib')
            wrapper = soup.new_tag('div')
            wrapper['class'] = 'text-wrapper'
            words = str(child).split()
            for word in words:
                word_wrapper = soup.new_tag('span')
                word_wrapper['class'] = 'word-wrapper'
                word_wrapper['data-atom'] = '+'
                word_wrapper.append(Text(word + ' '))
                wrapper.append(word_wrapper)
            child = wrapper
        if not no_versions: child['data-ver'] = root['data-ver']
        result.append(child)
    return result


def similarity(a, b):
    # print('sim:', a, b)
    if a['data-ver'] == b['data-ver']: return 0
    if a == b: return 1
    if is_atom(a) and is_atom(b):
        # return next(a.children) == next(b.children)
        return list(a.children) == list(b.children)
    if a.name != b.name: return 0
    a_children = flatten_children(a, no_versions=True)
    b_children = flatten_children(b, no_versions=True)
    if not a_children and not b_children: return 1
    common = reducer(a_children, b_children)
    # print('common:', common)
    return len(common) / min(len(a_children), len(b_children))
    # return len(common) / (len(a_children + b_children) / 2)


def groupby(children):
    groups = [[None]] + [[child] for child in children[0]]
    for ver in children[1:]:
        ver = [None] + ver
        lcs = [[0] * len(ver) for _ in range(len(groups))]
        prev = [[None] * len(ver) for _ in range(len(groups))]
        for i in range(1, len(lcs)):
            for j in range(1, len(lcs[i])):
                if any(similarity(child, ver[j]) > THRESHOLD for child in groups[i]):
                    lcs[i][j] = lcs[i - 1][j - 1] + 1
                    prev[i][j] = (i - 1, j - 1)
                elif lcs[i - 1][j] >= lcs[i][j - 1]:
                    lcs[i][j] = lcs[i - 1][j]
                    prev[i][j] = (i - 1, j)
                else:
                    lcs[i][j] = lcs[i][j - 1]
                    prev[i][j] = (i, j - 1)

        # nonlocal result
        result = []

        def build_lcs(i, j):
            nonlocal result
            if i == 0:
                result.append(ver[1:j+1])
            elif j == 0:
                result = result + groups[1:i+1]
            elif prev[i][j] == (i - 1, j - 1):
                build_lcs(i - 1, j - 1)
                result.append(groups[i] + [ver[j]])
            elif prev[i][j] == (i - 1, j):
                build_lcs(i - 1, j)
                result.append(groups[i])
            else:
                build_lcs(i, j - 1)
                result.append([ver[j]])

        build_lcs(len(groups) - 1, len(ver) - 1)
        groups = result

    # children_copy = children[:]
    # while children_copy:
    #     test_child = children_copy.pop(0)
    #     similar_items = [test_child]
    #     similar_indices = []
    #     for i, x in enumerate(children_copy):
    #         if compare(test_child, x):
    #             similar_indices.append(i)
    #             similar_items.append(x)
    #     groups.append(similar_items)
    #     for i in reversed(similar_indices):
    #         del children_copy[i]

    return groups[1:]


# def topsort(graph):
#     def dfs(i):
#         used[i] = True
#         for group in graph[i]:
#             if not used[group]:
#                 dfs(group)
#         result.append(i)
#
#     used = [False] * len(graph)
#     result = []
#     for i, group in enumerate(graph):
#         if not used[i]: dfs(i)
#     return result[::-1]


def merge_versions(roots):
    raw = [root['data-ver'] for root in roots]
    raw = set(sum((ver.split(',') for ver in raw), []))
    return ','.join(sorted(raw))


def merge(roots):
    if is_atom(roots[0]):
        atom = Tag(name=roots[0].name)
        for child in roots[0].children: atom.append(copy.copy(child))
        atom['data-ver'] = merge_versions(roots)
        # if atom.name == 'tr': print('TR', roots)
        atom['class'] = 'atom-wrapper'
        return atom

    # print('name', roots[0].name)

    tree_children = [flatten_children(root) for root in roots]
    tree_children.sort(key=len, reverse=True)
    # flat_children = sum(tree_children, [])

    groups = groupby(tree_children)
    for index, group in enumerate(groups):
        for item in group:
            item['data-group'] = index
            item.group = index
    # print('groups:', groups)

    # graph = [[] for _ in groups]
    # for children in tree_children:
    #     prev = None
    #     for child in children:
    #         if prev is not None:
    #             graph[prev.group].append(child.group)
    #         prev = child

    print('C', list(map(lambda children: list(map(lambda child: child.group, children)), tree_children)))
    # print('T', topsort(graph))
    print('G', groups)

    # sorted_groups = [groups[i] for i in topsort(graph)]
    # # if roots[0].get('class') == 'text-wrapper': print('wrapper:', graph, topsort(graph))
    # sorted_groups = [merge(group) for group in sorted_groups]
    sorted_groups = [merge(group) for group in groups]

    soup = Soup(features='html5lib')
    root = soup.new_tag(roots[0].name)
    for x in roots: root.attrs.update(x.attrs)
    root['data-ver'] = merge_versions(roots)
    for item in sorted_groups:
        root.append(copy.copy(item))

    return root

def diff(files):
    roots = []
    for ver, file in enumerate(files):
        content = ' '.join(open(file).read().split())
        soup = Soup(content, 'html5lib')
        root = soup.find('body')
        root.name = 'div'
        root['class'] = 'root'
        root['data-ver'] = str(ver)
        roots.append(root)
    return merge(roots)


if __name__ == '__main__':
    files = ['samples/' + file for file in os.listdir('samples')[:3]]
    html = str(diff(files))
    file = open('diff.html', 'w')
    file.write(html)
    file.close()
    copyfile('diff.html', 'frontend/source/diff.html')

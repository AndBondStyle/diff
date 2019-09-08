from bs4 import BeautifulSoup as Soup, NavigableString as Text, Tag
from difflib import SequenceMatcher
import copy, os

THRESHOLD = 0.6


def is_atom(node):
    if node.attrs.get('atom'): return True
    if node.name == 'li': return True


def reducer(a, b):
    matcher = SequenceMatcher(a=a, b=b)
    opcodes = matcher.get_opcodes()
    print('matching:', a, b)
    print('opcodes:', opcodes)
    equal = filter(lambda x: x[0] == 'equal', opcodes)
    equal = [a[i1:i2] for _, i1, i2, j1, j2 in equal]
    return sum(equal, [])


def flatten_children(root, no_versions=False):
    children = [child for child in root.children if str(child).strip()]
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
                word_wrapper['atom'] = '+'
                word_wrapper.append(Text(word))
                wrapper.append(word_wrapper)
            child = wrapper
        if not no_versions: child['data-ver'] = root['data-ver']
        result.append(child)
    return result


def similarity(a, b):
    print('sim:', a, b)
    if a['data-ver'] == b['data-ver']: return 0
    if a == b: return 1
    if is_atom(a) and is_atom(b):
        return next(a.children) == next(b.children)
    if a.name != b.name: return 0
    a_children = flatten_children(a, no_versions=True)
    b_children = flatten_children(b, no_versions=True)
    if not a_children and not b_children: return 1
    common = reducer(a_children, b_children)
    print('common:', common)
    return len(common) / (len(a_children + b_children) / 2)


def groupby(children):
    compare = lambda a, b: similarity(a, b) > THRESHOLD
    children_copy = children[:]
    groups = []
    while children_copy:
        test_child = children_copy.pop(0)
        similar_items = [test_child]
        similar_indices = []
        for i, x in enumerate(children_copy):
            if compare(test_child, x):
                similar_indices.append(i)
                similar_items.append(x)
        groups.append(similar_items)
        for i in reversed(similar_indices):
            del children_copy[i]
    return groups


def topsort(graph):
    def dfs(i):
        used[i] = True
        for group in graph[i]:
            if not used[group]:
                dfs(group)
        result.append(i)

    used = [False] * len(graph)
    result = []
    for i, group in enumerate(graph):
        if not used[i]: dfs(i)
    return result[::-1]


def merge(roots):
    if is_atom(roots[0]):
        atom = Tag(name=roots[0].name)
        atom.append(roots[0].text)
        atom['data-ver'] = ','.join(root['data-ver'] for root in roots)
        atom['class'] = 'word-wrapper'
        return atom

    tree_children = [flatten_children(root) for root in roots]
    flat_children = sum(tree_children, [])

    groups = groupby(flat_children)
    print('groups:', groups)
    for index, group in enumerate(groups):
        for item in group:
            item.group = index

    graph = [[] for _ in groups]
    for children in tree_children:
        prev = None
        for child in children:
            if prev is not None:
                graph[prev.group].append(child.group)
            prev = child

    sorted_groups = [groups[i] for i in topsort(graph)]
    sorted_groups = [merge(group) for group in sorted_groups]

    soup = Soup(features='html5lib')
    root = soup.new_tag(roots[0].name)
    for x in roots: root.attrs.update(x.attrs)
    root['data-ver'] = ','.join(root['data-ver'] for root in roots)
    for item in sorted_groups:
        root.append(copy.copy(item))

    return root


def diff(files):
    roots = []
    for ver, file in enumerate(files):
        content = open(file).read()
        soup = Soup(content, 'html5lib')
        body = soup.find('body')
        body['data-ver'] = str(ver)
        roots.append(body)
    return merge(roots)


if __name__ == '__main__':
    files = ['samples/' + file for file in os.listdir('samples')[:3]]
    html = str(diff(files))
    print(html)
    with open('output.html', 'w') as f: f.write(html)

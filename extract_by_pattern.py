import re
from collections import Counter, defaultdict

def extract_strict(str_headers, str_items):
    names = []
    def replace(match):
        names.append(match[1].strip())
        if match.end() == len(str_headers) or str_headers[match.end()] == '\n':
            return '(.*)$'
        else:
            return r'(.{{{0}}}|.{{,{0}}}$)'.format(len(match[1]))
    regex = re.compile(re.sub(r'(\S+[ \t]*)', replace, str_headers.strip()), re.MULTILINE)

    for str_item in str_items:
        groups = regex.match(str_item).groups()
        yield {name: value.strip() for name, value in zip(names, groups)}

line_regex = re.compile(r'^.*$', re.MULTILINE)
header_regex = re.compile(r'(\S+[ \t]*)')
chunk_regex = re.compile(r'(\S+)')
def extract_loose(str_headers, str_items):
    names = []
    owners_by_line = []
    for line_n, line_match in enumerate(line_regex.finditer(str_headers)):
        line_start, line_end = line_match.span()
        owners_by_line.append([None] * (line_end - line_start))
        for match in header_regex.finditer(str_headers, line_start, line_end):
            name = match[1].strip()
            names.append(name)
            start, end = match.span()
            for i in range(start, end):
                # TODO: allow multiple names per character,
                # and include spaces to the left of the name too.
                owners_by_line[-1][i-line_start] = name

    for str_item in str_items:
        parts_by_name = defaultdict(list)
        for line_n, line_match in enumerate(line_regex.finditer(str_item)):
            line_start, line_end = line_match.span()
            for match in chunk_regex.finditer(str_item, *line_match.span()):
                start, end = match.span()
                counter = Counter(owners_by_line[line_n][start-line_start:end-line_start] or owners_by_line[line_n][-1])
                counter[None] = 0
                (name, count), = counter.most_common(1)
                parts_by_name[name].append(match[1])
        yield {name: ' '.join(parts_by_name[name]) for name in names}

extract = extract_loose

if __name__ == '__main__':
    import unittest

    class TestLoose(unittest.TestCase):
        def t(self, str_header, str_item, expected):
            self.assertEqual(list(extract_loose(str_header, [str_item])), [expected])
        def test_1(self):
            self.t('field', 'value', {'field': 'value'})
        def test_2(self):
            self.t('field   ', 'value', {'field': 'value'})
        def test_3(self):
            self.t('field   ', 'value    ', {'field': 'value'})
        def test_4(self):
            self.t('field', 'value    ', {'field': 'value'})
        def test_5(self):
            self.t('  field', 'value', {'field': 'value'})
        def test_6(self):
            self.t('    field', 'value', {'field': 'value'})
        def test_7(self):
            self.t('     field', 'value', {'field': ''})
        def test_8(self):
            self.t('field', '    value', {'field': 'value'})
        def test_9(self):
            self.t('field', '     value', {'field': ''})
        def test_10(self):
            self.t('a b', '1 2', {'a': '1', 'b': '2'})
        def test_11(self):
            self.t('a b c', '1 2', {'a': '1', 'b': '2', 'c': ''})
        def test_12(self):
            self.t('a b', '11 2', {'a': '11', 'b': '2'})
        def test_13(self):
            self.t('a b', '112', {'a': '112', 'b': ''})
        def test_14(self):
            self.t('a b', '111 2', {'a': '111', 'b': '2'})
        def test_15(self):
            # TODO: this should split 1-2. Fixing this would auto-detect
            # header names that are centered.
            self.t('a  b', '1 2', {'a': '1 2', 'b': ''})
        def test_16(self):
            self.t('a b\nc', '1 2\n3', {'a': '1', 'b': '2', 'c': '3'})
        def test_17(self):
            self.t('a b c', '1   3', {'a': '1', 'b': '', 'c': '3'})

    class TestStrict(unittest.TestCase):
        def t(self, str_header, str_item, expected):
            self.assertEqual(list(extract_strict(str_header, [str_item])), [expected])
        def test_1(self):
            self.t('aaa', '111', {'aaa': '111'})
        def test_2(self):
            self.t('aaa', '1', {'aaa': '1'})
        def test_3(self):
            self.t('aaa', '1234', {'aaa': '1234'})
        def test_4(self):
            self.t('aaa bbb', '1 2 3 4', {'aaa': '1 2', 'bbb': '3 4'})
        def test_5(self):
            self.t('aaa bbb', '123456', {'aaa': '1234', 'bbb': '56'})
        def test_7(self):
            self.t('aaa\n', '123456', {'aaa': '123456'})
        def test_8(self):
            self.t('a b\nc', '1 234\n567', {'a': '1', 'b': '234', 'c': '567'})

    unittest.main()
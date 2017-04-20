# extract_by_pattern

Extracts data from monospaced text by giving a similarly formatted example. Useful for extracting structured data from sources with no clear separators.

```python
from extract_by_pattern import extract

str_headers = """
name                 age  sex
address
"""

str_data = ["""
John Smith           55    M
5322 Otter Lane
""", """
Jane Smith           57    F
5322 Otter Lane
"""]

items = list(extract(str_headers, str_data))
print(items[1]['name'])
# 'Jane Smith'
```

The `extract_loose` implementation is the default one, and tries to keep chunks of text together, looking for which header is most likely for each chunk, then grouping the chunks under that name. This is what a human would do if there was any empty space between the "fields".

The `extract_strict` function is not afraid of splitting a word if crosses the boundary between two headers. Internally it converts the boundaries to a single regular expression, so matching is done very quickly.

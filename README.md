# extract_by_pattern

Extracts data from monospaced text by giving a similarly formatted example. Useful for extracting structured data from sources with no clear separators. Each header is assumed to include all spaces to its right.

    from extract_by_pattern import extract

    str_data = """
    John Smith           55    M
    5322 Otter Lane
    """
    
    str_headers = """
    name                 age  sex
    address
    """

    data, = extract(str_headers, [str_data])
    print(data)
    # 'John Smith'

The `extract_loose` implementation is the default one, and tries to keep chunks of text together, looking for which header is most likely for each chunk, then grouping the chunks under that name. 

The `extract_strict` function is not afraid of splitting a word if crosses the boundary between two headers.
#!/usr/bin/env python3

import argparse
from sys import stderr
from typing import TextIO


BASE_SCALE = 10000000


def main(argv: list[str] = None):
    parser = argparse.ArgumentParser(description="Read scale factor for a single combination of sample and condition.")
    parser.add_argument("-s", "--scales", type=argparse.FileType('r'), required=True,
                        help="Tab delimited file containing scale factors")
    parser.add_argument("-r", "--row", required=True,
                        help="Row index or content to look for in row headers to find row index containing scale factor to read")
    parser.add_argument("-c", "--column", required=True,
                        help="Column index or content to look for in column headers to find column index containing scale factor to read")

    args = parser.parse_args(argv)
    scale = read_scale_factor(scale_factors_file=args.scales, row_content=args.row, column_content=args.column)
    print(f"{scale}")


def read_scale_factor(scale_factors_file: TextIO, row_content: str, column_content: str) -> float:
    """
    Read scale factor for a single combination of sample and condition.

    :param scale_factors_file: Tab delimited file containing scale factors
    :param row_content: Row index or content to look for in row headers to find row index containing scale factor to read
    :param column_content: Column index or content to look for in column headers to find column index containing scale factor to read
    :return: Scale factor found or 0 if content is not a valid scale factor
    """
    scale_factors_file_content = scale_factors_file.readlines()

    row_index = get_row_index(row_content, scale_factors_file_content)
    column_index = get_column_index(column_content, scale_factors_file_content)

    row_columns = scale_factors_file_content[row_index].rstrip("\r\n").split("\t")
    try:
        return float(row_columns[column_index])
    except ValueError:
        print(f"found value to parse in row {row_index} and column {column_index}, "
              f"but content {row_columns[column_index]} is not a float", file=stderr)
        return 0


def get_row_index(row_content: str, scale_factors_file_content: list[str]) -> int:
    """
    Gets row index based on row_content which can be an index or content to look for.

    :param row_content: Row index or content to look for in row headers to find row index containing scale factor to read
    :param scale_factors_file_content: Content of tab delimited file containing scale factors
    :return: row index based on row_content which can be an index or content to look for
    """
    try:
        row_index = int(row_content)
    except ValueError:
        row_headers = [line.rstrip("\r\n").split("\t")[0] for line in scale_factors_file_content]
        row_indexes = [i for i in range(0, len(row_headers)) if row_content in row_headers[i]]
        if len(row_indexes) == 0:
            print(f"row content {row_content} not found in any row headers", file=stderr)
            return 0
        row_index = row_indexes[0]
        if len(row_indexes) > 1:
            print(f"row content {row_content} found in multiple row headers (indexes: {row_indexes}), "
                  f"using row index {row_index}", file=stderr)
    return row_index


def get_column_index(column_content: str, scale_factors_file_content: list[str]) -> int:
    """
    Gets column index based on column_content which can be an index or content to look for.

    :param column_content: Column index or content to look for in column headers to find column index containing scale factor to read
    :param scale_factors_file_content: Content of tab delimited file containing scale factors
    :return: column index based on column_content which can be an index or content to look for
    """
    try:
        column_index = int(column_content)
    except ValueError:
        column_headers = scale_factors_file_content[0].rstrip("\r\n").split("\t")
        column_indexes = [i for i in range(0, len(column_headers)) if column_content in column_headers[i]]
        if len(column_indexes) == 0:
            print(f"column content {column_content} not found in any column headers", file=stderr)
            return 0
        column_index = column_indexes[0]
        if len(column_indexes) > 1:
            print(f"column content {column_content} found in multiple column headers (indexes: {column_indexes}), "
                  f"using column index {column_index}", file=stderr)
    return column_index


if __name__ == '__main__':
    main()

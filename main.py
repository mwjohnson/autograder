#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
import csv
import sys
import logging
import functools
from pathlib import Path
from timeit import default_timer

from L2SCA import analyzeText4 as analyzeText
from lca import lc_anc3 as lc_anc


logger = logging.getLogger('autograder')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(name)s(%(levelname)s):%(module)s.%(funcName)s[%(lineno)d]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(level=logging.INFO)


def timer_decorator(func_to_time):
    """
    A timer decorator. Using this, like in the load_settings() function declaration below will enable a timing
    report for the function call.
    Simply include @timer_decorator before you function definition.
    @timer_decorator
    def my_timed_function():
    :param func_to_time: the function to measure the time of execution.
    :return: the wrapper - used for decoration.
    """

    @functools.wraps(func_to_time)
    def wrapper_timer(*args, **kwargs):
        start = default_timer()
        result = func_to_time(*args, **kwargs)
        end = default_timer()
        logger.info(func_to_time.__name__ + ': elapsed time: %s', end - start)
        return result

    return wrapper_timer


def process_variables(lca_res, l2sca_res):
    """
    lca_res = {'filename': 'dickhole.txt', 'wordtypes': 59, 'swordtypes': 59, 'lextypes': 3, 'slextypes': 3, 'wordtokens': 72,
       'swordtokens': 72, 'lextokens': 3, 'slextokens': 3, 'ld': 0.041666666666666664, 'ls1': 1.0, 'ls2': 1.0,
       'vs1': 1.0, 'vs2': 1.0, 'cvs1': 0.7071067811865475, 'ndw': 59, 'ndwz': 44, 'ndwerz': 43.0, 'ndwesz': 43.6,
       'ttr': 0.8194444444444444, 'msttr': 0.88, 'cttr': 4.916666666666667, 'rttr': 6.953216681667718,
       'logttr': 0.9534383396859258, 'uber': 39.88973941012686, 'vv1': 1.0, 'svv1': 1.0, 'cvv1': 0.7071067811865475,
       'lv': 1.0, 'vv2': 0.3333333333333333, 'nv': 1.0, 'adjv': 0.3333333333333333, 'advv': 0.0,
       'modv': 0.3333333333333333}
    l2sca_res = {'w': 76, 's': 4, 'vp': 9, 'c': 7, 't': 4, 'dc': 3, 'ct': 2, 'cp': 2, 'cn': 9, 'MLS': 19.0, 'MLT': 19.0,
       'MLC': 10.857142857142858, 'C/S': 1.75, 'VP/T': 2.25, 'C/T': 1.75, 'DC/C': 0.42857142857142855, 'DC/T': 0.75,
       'T/S': 1.0, 'CT/T': 0.5, 'CP/T': 0.5, 'CP/C': 0.2857142857142857, 'CN/T': 2.25, 'CN/C': 1.2857142857142858}
    :return:
    """
    var_res = [-1] * 17
    var_res[0] = 1 if lca_res['lextypes'] > 25 else 0
    if lca_res['wordtokens'] > 70:
        var_res[1] = 2
    elif lca_res['wordtokens'] > 60:
        var_res[1] = 1
    else:
        var_res[1] = 0
    if lca_res['lextokens'] > 35:
        var_res[2] = 2
    elif lca_res['lextokens'] > 30:
        var_res[2] = 1
    else:
        var_res[2] = 0

    var_res[3] = 1 if lca_res['ld'] > 0.5 else 0
    var_res[4] = 1 if lca_res['ndw'] > 50 else 0

    if lca_res['cttr'] > 4:
        var_res[5] = 2
    elif lca_res['cttr'] > 3.75:
        var_res[5] = 1
    else:
        var_res[5] = 0

    var_res[6] = 1 if lca_res['uber'] > 20 else 0
    var_res[7] = 1 if lca_res['vv1'] > 6 else 0

    if l2sca_res['w'] > 70:
        var_res[8] = 3
    elif l2sca_res['w'] > 60:
        var_res[8] = 2
    elif l2sca_res['w'] > 50:
        var_res[8] = 1
    else:
        var_res[8] = 0

    if l2sca_res['cn'] > 7.5:
        var_res[9] = 3
    elif l2sca_res['cn'] > 6:
        var_res[9] = 2
    elif l2sca_res['cn'] > 4:
        var_res[9] = 1
    else:
        var_res[9] = 0
    var_res[10] = 1 if l2sca_res['MLS'] > 14 else 0

    if l2sca_res['MLT'] > 14:
        var_res[11] = 2
    elif l2sca_res['MLT'] > 12.5:
        var_res[11] = 1
    else:
        var_res[11] = 0

    var_res[12] = 1 if l2sca_res['MLC'] > 8 else 0
    var_res[13] = 1 if l2sca_res['DC/T'] > 0.6 else 0
    var_res[14] = 1 if l2sca_res['CT/T'] > 0.5 else 0

    if l2sca_res['CN/T'] > 1.2:
        var_res[15] = 2
    elif l2sca_res['CN/T'] > 0.9:
        var_res[15] = 1
    else:
        var_res[15] = 0

    if l2sca_res['CN/C'] > 0.75:
        var_res[16] = 3
    elif l2sca_res['CN/C'] > 0.65:
        var_res[16] = 2
    elif l2sca_res['CN/C'] > 0.55:
        var_res[16] = 1
    else:
        var_res[16] = 0

    return var_res


def process_result_array(result_array):
    score = sum(result_array) / 28

    if score >= 0.8:
        final = 3
    elif score > 0.6:
        final = 2
    else:
        final = 1

    print(f'Score: {score}, final: {final}')


@timer_decorator
def process_lca(lemlines, input_filename, wordranks, adjdict):
    lca_result = lc_anc.main(lemlines, input_filename, wordranks, adjdict)
    return lca_result


@timer_decorator
def process_l2sca(input_file, lexparser_path, tregex_path, write_output_file):
    l2sca_result = analyzeText.main(input_file, lexparser_path, tregex_path, write_output_file)
    return l2sca_result


@timer_decorator
def preprocess(anc_all_count_filepath):
    wordranks, adjdict = lc_anc.process_wordrank(anc_all_count_filepath)
    logger.info(f'{anc_all_count_filepath} data loaded.')
    return wordranks, adjdict


def read_input_text(filename):
    with open(filename, 'r') as f:
        text_lines = f.readlines()
    logger.info(f'Read file: {filename} - {len(text_lines)} lines read.')
    return text_lines


def get_lexical_data_string(lca_result, l2sca_result):
    """
    Get the lca_string from lca_result.
    Get the l2sca_string from l2sca_result.
    Concatenate those two strings together with a comma "," and return the resulting string.
    :param lca_result:
    :param l2sca_result:
    :return:
    """

    with io.StringIO() as lca_csv:
        writer = csv.DictWriter(lca_csv, fieldnames=lca_result.keys())
        writer.writerow(lca_result)
        lca_string = lca_csv.getvalue().rstrip()

    with io.StringIO() as l2sca_csv:
        writer = csv.DictWriter(l2sca_csv, fieldnames=l2sca_result.keys())
        writer.writerow(l2sca_result)
        l2sca_string = l2sca_csv.getvalue()

    lex_data = lca_string+','+l2sca_string
    return lex_data


def get_lexical_data_header_string(lca_result, l2sca_result):
    """
    Get the Header string from lca_result.
    Get the Header string from l2sca_result.
    Concatenate those two strings together with a comma "," and return the resulting string.
    :param lca_result:
    :param l2sca_result:
    :return: One combined string of the lca_header and l2sca_header in csv format.
    """
    with io.StringIO() as lca_csv:
        writer = csv.DictWriter(lca_csv, fieldnames=lca_result.keys())
        writer.writeheader()
        lca_header = lca_csv.getvalue().rstrip()

    with io.StringIO() as l2sca_csv:
        writer = csv.DictWriter(l2sca_csv, fieldnames=l2sca_result.keys())
        writer.writeheader()
        l2sca_header = l2sca_csv.getvalue()

    return lca_header+','+l2sca_header


def write_string_to_file(string, output_filename):
    with open(output_filename, 'w', encoding='utf8') as output_file:
        output_file.write(string)
    logger.info(f'{output_filename} written to disk.')


def write_header_and_data_to_file(header, data, output_filename):
    """

    :type header - a string.
    :param header:
    :type data - list of strings.
    :param data:
    :param output_filename:
    :return:
    """
    with open(output_filename, 'w', encoding='utf8') as output_file:
        output_file.write(header)
        for d in data:
            output_file.write(d)
    logger.info(f'{len(data)} lines of output written to: {output_filename}.')


def check_mode(input_filepath):
    assert os.path.exists(input_filepath), f'{input_filepath} does not exist.'
    if os.path.isdir(input_filepath):
        mode = 'directory'
    elif os.path.isfile(input_filepath):
        mode = 'file'
    else:
        assert False, f'{input_filepath} is not a file nor a directory.'
    logger.info(f'{mode} mode recognized. Loading data from: {input_filepath}')
    return mode


@timer_decorator
def main(input_path='./input_data/piranhas.txt'):
    wordranks, adjdict = preprocess('./lca/anc_all_count.txt')  # pre-process the word ranks.

    input_filepath = os.path.join(os.getcwd(), input_path)
    mode = check_mode(input_filepath)

    if mode == 'file':
        text_lines = read_input_text(input_path)
        lca_result = process_lca(text_lines, Path(input_path).name, wordranks, adjdict)
        l2sca_result = process_l2sca(input_path, "./L2SCA/stanford-parser-full-2014-01-04/lexparser.sh", "./L2SCA/tregex.sh", False)
        result_array = process_variables(lca_result, l2sca_result)
        header = get_lexical_data_header_string(lca_result, l2sca_result)
        lex_data = get_lexical_data_string(lca_result, l2sca_result)
        write_string_to_file(header+lex_data, f'./output/{Path(input_path).name}.out.csv')

    if mode == 'directory':
        header = None
        lex_data = []
        for fdx, filename in enumerate(os.listdir(input_filepath)):
            if filename.endswith('.txt'):
                file_path = os.path.join(input_filepath, filename)
                text_lines = read_input_text(file_path)
                lca_result = process_lca(text_lines, Path(filename).name, wordranks, adjdict)
                l2sca_result = process_l2sca(file_path, "./L2SCA/stanford-parser-full-2014-01-04/lexparser.sh", "./L2SCA/tregex.sh", False)
                result_array = process_variables(lca_result, l2sca_result)

                if fdx == 0:
                    header = get_lexical_data_header_string(lca_result, l2sca_result)

                lex_data.append(get_lexical_data_string(lca_result, l2sca_result))

        write_header_and_data_to_file(header, lex_data, os.path.join(os.getcwd(), './output/out.csv'))

    process_result_array(result_array)
    logger.info('Autograder Complete.')


if __name__ == '__main__':
    main(sys.argv[1])

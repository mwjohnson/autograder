#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from timeit import default_timer
import functools
from L2SCA import analyzeText4 as analyzeText
from lca import lc_anc3 as lc_anc

logging.basicConfig()
logger = logging.getLogger(__name__)
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


@timer_decorator
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
def process_l2sca(input_file, lexparser_path, tregex_path):
    l2sca_result = analyzeText.main(input_file, lexparser_path, tregex_path)
    return l2sca_result


@timer_decorator
def preprocess(anc_all_count_filepath):
    wordranks, adjdict = lc_anc.process_wordrank(anc_all_count_filepath)
    return wordranks, adjdict


@timer_decorator
def read_input_text(filename):
    with open(filename, 'r') as f:
        lemlines = f.readlines()
    return lemlines


def main():
    # pre-process the word ranks.
    wordranks, adjdict = preprocess('./lca/anc_all_count.txt')
    input_file = './input_data/moon.txt'

    lemlines = read_input_text(input_file)

    lca_result = process_lca(lemlines, 'dickhole.txt', wordranks, adjdict)
    l2sca_result = process_l2sca(input_file, "./L2SCA/stanford-parser-full-2014-01-04/lexparser.sh","./L2SCA/tregex.sh")

    result_array = process_variables(lca_result, l2sca_result)
    print(result_array)
    process_result_array(result_array)


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
import csv

from arg_counter.arg_counter import ArgCounter
from main import check_mode, write_header_and_data_to_file
from spacy_full import process


def write2csv(grade_output):
    output_filename = './your_grades.csv'
    with open(output_filename, 'w', encoding='utf8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=",", lineterminator="\r\n")
        writer.writerows(grade_output)


def calculate_g3(score):
    slex = score['scores']['slextypes']
    cttr = score['scores']['cttr']
    mls = score['syntax']['mls']
    mlc = score['syntax']['mlc']
    cstr = score['syntax']['CSTR_t']
    sframe = score['phrase']['SFraming']
    arg = score['argument_scores']['arg_cnt']
    c = score['syntax']['c']
    c2sdm_c = arg - (arg/c)

    if slex > 14.9:
        slex_score = 3
    elif slex >5.1:
        slex_score = 2+((slex-10)/4.9)
    else:
        slex_score = 1

    if cttr > 5.3:
        cttr_score = 3
    elif cttr > 4.3:
        cttr_score = 2+((cttr-4.8)/0.5)
    else:
        cttr_score = 1

    if mls > 22.7:
        mls_score = 3
    elif mls > 14.3:
        mls_score = 2+((mls-18.5)/4.2)
    else:
        mls_score = 1

    if mlc > 9.6:
        mlc_score = 3
    elif mlc > 6.8:
        mlc_score = 2+((mlc-8.4)/1.4)
    else:
        mlc_score = 1

    if cstr > 5.9:
        cstr_score = 3
    elif cstr > 2.5:
        cstr_score = 2+((cstr-4.2)/1.7)
    else:
        cstr_score = 1

    if c2sdm_c > 6.2:
        arg_score = 3
    elif c2sdm_c > 2.8:
        arg_score = 2+((c2sdm_c-4.5)/1.7)
    else:
        arg_score = 1

    if sframe > 4.5:
        sframe_score = 3
    elif sframe > 1.5:
        sframe_score = 2+((sframe-3)/1.5)
    else:
        sframe_score = 1

    summed_score = (slex_score * 7.5) + (cttr_score * 24.8) + (mls_score * 14.97) + (mlc_score * 3.29) + (cstr_score * 10.96) + (arg_score * 21.43) + (sframe_score * 17.04)

    if summed_score > 190:
        g3score = 3
    else:
        g3score = 2

    return g3score


def calculate_g2(score):
    cvv1 = score['scores']['cvv1']
    cttr = score['scores']['cttr']
    w = score['syntax']['w']
    mls = score['syntax']['mls']
    mlc = score['syntax']['mlc']
    sframe = score['phrase']['SFraming']
    arg = score['argument_scores']['arg_cnt']
    c = score['syntax']['c']
    c2sdm_c = arg - (arg/c)

    if cvv1 > 2.7:
        cvv1_score = 3
    elif cvv1 > 1.9:
        cvv1_score = 2+((cvv1-2.3)/0.4)
    else:
        cvv1_score = 1

    if cttr > 4.9:
        cttr_score = 3
    elif cttr > 3.9:
        cttr_score = 2+((cttr-4.4)/0.5)
    else:
        cttr_score = 1

    if w > 133:
        w_score = 3
    elif w > 77:
        w_score = 2+((w-105)/28)
    else:
        w_score = 1

    if mls > 20:
        mls_score = 3
    elif mls > 10:
        mls_score = 2+((mls-15)/5)
    else:
        mls_score = 1

    if mlc > 9.4:
        mlc_score = 3
    elif mlc > 6.4:
        mlc_score = 2+((mlc-7.9)/1.5)
    else:
        mlc_score = 1

    if c2sdm_c > 4.5:
        arg_score = 3
    elif c2sdm_c > 1.5:
        arg_score = 2+((c2sdm_c-3)/1.5)
    else:
        arg_score = 1

    if sframe > 2:
        sframe_score = 3
    elif sframe > 0:
        sframe_score = 2+((sframe-1)/1)
    else:
        sframe_score = 0


    summed_score = (w_score * 45.12) + (cvv1_score * 16.78) + (cttr_score * 19.51) + (mls_score * 11.86) + (mlc_score * 1.99) + (arg_score * 3.25) + (sframe_score * 1.5)

    if summed_score >= 168:
        g2score = 2
    else:
        g2score = 1

    return g2score


def grademe(pre_scores):
    """
    Decides scores 1~4 based on transformation of results from AnalyzeText.
    If less than 50 words, automatic grade of 1 is given.
    Otherwise, sends particular AnalyzeText results to functions to determine if they should be a 2, 3, or 4.
    :param pre_scores:
    :return:
    """

    post_p_scores = []
    for score in pre_scores:
        w = score['syntax']['w']
        filename = score['scores']['filename']

        if w < 50:
            post_p = 0
        else:
            g2 = calculate_g2(score)
            if g2 == 1:
                post_p = g2
            else:
                post_p = calculate_g3(score)

        post_p_scores.append((filename, post_p))

    return post_p_scores


def analyze_text(input_path):
    input_filepath = os.path.join(os.getcwd(), input_path)
    mode = check_mode(input_filepath)

    ac = ArgCounter('arg_counter/word_list.txt')

    if mode == 'file':
        result = process(input_path, Path(input_path).name, ac)
        print(f"Results for {result['scores']['filename']}")
        for k, v in result.items():
            print(f'{k}: {v}')

    if mode == 'directory':
        scores = []
        for fdx, filename in enumerate(os.listdir(input_filepath)):
            if filename.endswith('.txt'):
                result = process(os.path.join(input_filepath, filename), filename, ac)
                scores.append(result)
        return scores


def rater(i_path):
    """
    Calls spacy_full to run analyzeText which gets a set of scores from an input text.
    Runs grademe on the AnalyzeText result.
    Writes the output to file.

    Example output.csv:
    moon.txt,4
    multiline.txt,4
    piranhas.txt,3

    :param i_path: the input file name.
    :type i_path: string
    :return: None
    """
    # pre_analysis =
    grades = grademe(analyze_text(i_path))
    write2csv(grades)


if __name__ == '__main__':
    assert sys.argv[1], 'input file parameter missing.'
    rater(sys.argv[1])

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
    ndw = score['scores']['ndw']
    svv1 = score['scores']['svv1']
    mls = score['syntax']['mls']
    mlc = score['syntax']['mlc']
    cstr = score['syntax']['CSTR_c']

    if ndw > 80:
        ndw_score = 3
    elif ndw > 52:
        ndw_score = 2+((ndw-66)/14)
    else:
        ndw_score = 1

    if svv1 > 12.2:
        svv1_score = 3
    elif svv1 > 9.8:
        svv1_score = 2+((svv1-11)/1.2)
    else:
        svv1_score = 1

    if mls > 17:
        mls_score = 3
    elif mls > 11:
        mls_score = 2+((mls-14)/3)
    else:
        mls_score = 1

    if mlc > 9.6:
        mlc_score = 3
    elif mlc > 7.2:
        mlc_score = 2+((mlc-8.4)/1.2)
    else:
        mlc_score = 1

    if cstr > 2.74:
        add3_score = 3
    elif cstr > 1.46:
        add3_score = 2+((cstr-2.1)/0.64)
    else:
        add3_score = 1

    summed_score = (ndw_score * 0.8082) + (svv1_score * 0.0431) + (mls_score * 0.0742) + (mlc_score * 0.0598) + (add3_score * 0.0148)

    if summed_score >= 1.788:
        g3score = 4
    else:
        g3score = 3

    return g3score


def calculate_g2(score):
    cvs1 = score['scores']['cvs1']
    ndw = score['scores']['ndw']
    cttr = score['scores']['cttr']
    w = score['syntax']['w']
    mls = score['syntax']['mls']
    c_t = score['syntax']['c_t']
    arg = score['argument_scores']['arg']
    c = score['syntax']['c']
    c2sdm_c = arg - (arg/c)

    if cvs1 > 0.645:
        cvs1_score = 3
    elif cvs1 > 0.145:
        cvs1_score = 2+((cvs1-.395)/.25)
    else:
        cvs1_score = 1

    if ndw > 57:
        ndw_score = 3
    elif ndw > 41:
        ndw_score = 2+((ndw-49)/8)
    else:
        ndw_score = 1

    if cttr > 4.375:
        cttr_score = 3
    elif cttr > 3.625:
        cttr_score = 2+((cttr-4)/0.375)
    else:
        cttr_score = 1

    if w > 87:
        w_score = 3
    elif w > 57:
        w_score = 2+((w-72)/15)
    else:
        w_score = 1

    if mls > 14:
        mls_score = 3
    elif mls > 9:
        mls_score = 2+((mls-11.5)/2.5)
    else:
        mls_score = 1

    if c_t > 1.88:
        c_t_score = 3
    elif c_t > 1.08:
        c_t_score = 2+((c_t-1.48)/0.4)
    else:
        c_t_score = 1

    if c2sdm_c > 2.8:
        arg_score = 3
    elif c2sdm_c > 0.8:
        arg_score = 2+((c2sdm_c-1.8)/1)
    else:
        arg_score = 1

    summed_score = (w_score * 0.3864) + (cvs1_score * 0.1604) + (ndw_score * 0.1671) + (cttr_score * 0.1604) + \
                   (arg_score * 0.008) + (c_t_score * 0.0441) + (mls_score * 0.0735)

    if summed_score >= 1.63:
        g2score = 3
    else:
        g2score = 2

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
            post_p = 1
        else:
            g2 = calculate_g2(score)
            if g2 == 2:
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

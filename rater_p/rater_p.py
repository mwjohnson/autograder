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
    w = score['syntax']['w']
    cvs1 = score['scores']['cvs1']
    ndw = score['scores']['ndw']
    cttr = score['scores']['cttr']
    cvv1 = score['scores']['cvv1']
    argd = score['argument_scores']['arg_den']
    mlsubj = score['syntax']['mlc']
    add3 = score['syntax']['Add3']

    if w > 115:
        w_score = 3
    elif w > 85:
        w_score = 2
    else:
        w_score = 1

    if cvs1 > 0.64:
        cvs1_score = 3
    elif cvs1 > 0.44:
        cvs1_score = 2
    else:
        cvs1_score = 1

    if ndw > 75:
        ndw_score = 3
    elif ndw > 61:
        ndw_score = 2
    else:
        ndw_score = 1

    if cttr > 4.8:
        cttr_score = 3
    elif cttr > 4.2:
        cttr_score = 2
    else:
        cttr_score = 1

    if cvv1 > 2.55:
        cvv1_score = 3
    elif cvv1 > 2.25:
        cvv1_score = 2
    else:
        cvv1_score = 1

    if argd > 0.5:
        argd_score = 3
    elif argd > -0.5:
        argd_score = 2
    else:
        argd_score = 1

    if mlsubj > 10:
        mlsubj_score = 3
    elif mlsubj > 6:
        mlsubj_score = 2
    else:
        mlsubj_score = 1

    if add3 > 5:
        add3_score = 3
    elif add3 > 3:
        add3_score = 2
    else:
        add3_score = 1

    summed_score = (w_score * 0.04) + (cvs1_score * 0.06) + (ndw_score * 0.13) + (cttr_score * 0.05) + (
                cvv1_score * 0.32) + (argd_score * 0.03) + (mlsubj_score * 0.32) + (add3_score * 0.05)

    if summed_score >= 2:
        g3score = 4
    else:
        g3score = 3

    return g3score


def calculate_g2(score):
    w = score['syntax']['w']
    cvs1 = score['scores']['cvs1']
    ndw = score['scores']['ndw']
    cttr = score['scores']['cttr']
    cvv1 = score['scores']['cvv1']
    argd = score['argument_scores']['arg_den']
    subj = score['syntax']['Subj']
    add3 = score['syntax']['Add3']

    if w > 85:
        w_score = 3
    elif w > 65:
        w_score = 2
    else:
        w_score = 1

    if cvs1 > 0.495:
        cvs1_score = 3
    elif cvs1 > 0.295:
        cvs1_score = 2
    else:
        cvs1_score = 1

    if ndw > 61:
        ndw_score = 3
    elif ndw > 39:
        ndw_score = 2
    else:
        ndw_score = 1

    if cttr > 4.3:
        cttr_score = 3
    elif cttr > 3.7:
        cttr_score = 2
    else:
        cttr_score = 1

    if cvv1 > 2.3:
        cvv1_score = 3
    elif cvv1 > 2.1:
        cvv1_score = 2
    else:
        cvv1_score = 1

    if argd > -.8:
        argd_score = 3
    elif argd > -2.2:
        argd_score = 2
    else:
        argd_score = 1

    if subj > 13:
        subj_score = 3
    elif subj > 9:
        subj_score = 2
    else:
        subj_score = 1

    if add3 > 3:
        add3_score = 3
    elif add3 > 1:
        add3_score = 2
    else:
        add3_score = 1

    summed_score = (w_score * 0.18) + (cvs1_score * 0.35) + (ndw_score * 0.02) + (cttr_score * 0.13) + (
                cvv1_score * 0.18) + (argd_score * 0.06) + (subj_score * 0.02) + (add3_score * 0.06)

    if summed_score > 1.5:
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

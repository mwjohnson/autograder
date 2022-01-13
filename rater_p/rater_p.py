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
    mlc = score['syntax']['mlc']
    mls = score['syntax']['mls']
    m_s = score['syntax']['m_s']
    m_c = score['syntax']['m_c']
    comp_c = score['syntax']['comp_c']
    allmod = score['syntax']['allmod']

    if w > 125:
        w_score = 3
    elif w < 85:
        w_score = 1
    else:
        w_score = 2 + ((w-105)/20)

    if cvs1 > 0.64:
        cvs1_score = 3
    elif cvs1 < 0.44:
        cvs1_score = 1
    else:
        cvs1_score = 2 + ((cvs1-0.54)/0.1)

    if ndw > 80:
        ndw_score = 3
    elif ndw < 52:
        ndw_score = 1
    else:
        ndw_score = 2 + ((ndw-66)/14)

    if cttr > 4.9:
        cttr_score = 3
    elif cttr < 4.1:
        cttr_score = 1
    else:
        cttr_score = 2 + ((cttr-4.5)/0.4)

    if cvv1 > 2.55:
        cvv1_score = 3
    elif cvv1 < 2.25:
        cvv1_score = 1
    else:
        cvv1_score = 2 + ((cvv1-2.4)/0.15)

    if argd > 0.79:
        argd_score = 3
    elif argd < -0.61:
        argd_score = 1
    else:
        argd_score = 2 + ((argd-0.09)/0.7)

    if mlc > 11.2:
        mlc_score = 3
    elif mlc < 5.8:
        mlc_score = 1
    else:
        mlc_score = 2 + ((mlc-8.5)/2.7)

    if allmod > 16:
        allmod_score = 3
    elif allmod < 8:
        allmod_score = 1
    else:
        allmod_score = 2 + ((allmod-12)/4)

    if m_s > 2.15:
        m_s_score = 3
    elif m_s < 1.05:
        m_s_score = 1
    else:
        m_s_score = 2 + ((m_s-1.6)/0.55)

    if mls > 17:
        mls_score = 3
    elif mls < 11:
        mls_score = 1
    else:
        mls_score = 2 + ((mls-14)/3)

    if m_c > 1.5:
        m_c_score = 3
    elif m_c < 0.3:
        m_c_score = 1
    else:
        m_c_score = 2 + ((m_c-0.9)/0.6)

    if comp_c > 0.49:
        comp_c_score = 3
    elif comp_c < 0.17:
        comp_c_score = 1
    else:
        comp_c_score = 2 + ((comp_c-0.33)/0.16)


    summed_score = (w_score * 0.12) + (cvs1_score * 0.0925) + (ndw_score * 0.1229) + (cttr_score * 0.1232) + (
                cvv1_score * 0.1488) + (argd_score * 0.0415) + (mlc_score * 0.0203) + (mls_score * .1357) + (m_s_score * 0.1216) + (allmod_score * 0.0333) + (m_c_score * 0.0377) + (comp_c_score * 0.0024)

    if summed_score >= 1.8:
        g3score = 4

    else:
        g3score = 3

    return g3score


def calculate_g2(score):
    w = score['syntax']['w']
    cvs1 = score['scores']['cvs1']
    ndw = score['scores']['ndw']
    cttr = score['scores']['cttr']
    svv1 = score['scores']['svv1']
    argc = score['argument_scores']['arg_cnt']
    c = score['syntax']['c']
    add3 = score['syntax']['add3']
    mls = score['syntax']['mls']
    dc = score['syntax']['dc']
    allmod = score['syntax']['allmod']
    dc_s = score['syntax']['dc_s']


    if w > 82:
        w_score = 3
    elif w < 62:
        w_score = 1
    else:
        w_score = 2+((w-72)/10)

    if cvs1 > 0.645:
        cvs1_score = 3
    elif cvs1 < .145:
        cvs1_score = 1
    else:
        cvs1_score = 2+((cvs1-0.395)/0.25)

    if ndw > 54:
        ndw_score = 3
    elif ndw < 42:
        ndw_score = 1
    else:
        ndw_score = 2+((ndw-49)/5)

    if cttr > 4.6:
        cttr_score = 3
    elif cttr < 3.8:
        cttr_score = 1
    else:
        cttr_score = 2+((cttr-4.2)/0.4)

    if svv1 > 10:
        svv1_score = 3
    elif svv1 < 5.6:
        svv1_score = 1
    else:
        svv1_score = 2+((svv1-7.8)/2.2)

    if argc > 5:
        argc_score = 3
    elif argc < 1:
        argc_score = 1
    else:
        argc_score = 2+((argc-3)/2)

    if c > 14:
        c_score = 3
    elif c < 8:
        c_score = 1
    else:
        c_score = 2+((c-11)/3)

    if add3 > 14:
        add3_score = 3
    elif add3 < 2:
        add3_score = 1
    else:
        add3_score = 2+((add3-8)/6)

    if mls > 14:
        mls_score = 3
    elif mls < 8:
        mls_score = 1
    else:
        mls_score = 2 + ((mls - 11) / 3)

    if allmod > 13:
        allmod_score = 3
    elif allmod < 5:
        allmod_score = 1
    else:
        allmod_score = 2 + ((allmod - 9) / 4)

    if dc > 5:
        dc_score = 3
    elif dc < 1:
        dc_score = 1
    else:
        dc_score = 2 + ((dc - 3) / 2)

    if dc_s > 0.95:
        dc_s_score = 3
    elif dc_s < 0.15:
        dc_s_score = 1
    else:
        dc_s_score = 2 + ((dc_s - 0.55) / 0.4)

    summed_score = (w_score * 0.002) + (cvs1_score * 0.2) + (ndw_score * 0.09) + (cttr_score * 0.028) + (
                svv1_score * 0.0644) + (argc_score * 0.007) + (c_score * 0.0846) + (add3_score * 0.3) + (mls_score * 0.1275) + (allmod_score * 0.0705) + (dc_score * 0.011) + (dc_s_score * 0.017)

    if summed_score > 1.7:
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
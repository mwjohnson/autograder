import os
import sys
from pathlib import Path
import csv
from main import check_mode, write_header_and_data_to_file
from spacy_full import process
from source_checker.source_c import prepare_all as source_check
from arg_counter.arg_counter import ArgCounter


def write2csv(grade_output):
    output_filename = './summary_grades.csv'
    with open(output_filename, 'w', encoding='utf8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=",", lineterminator="\r\n")
        writer.writerows(grade_output)

def calculate_g3(score, source_score):
    cvs1 = score['scores']['cvs1']
    cvv1 = score['scores']['cvv1']
    cc = score['syntax']['cc']
    allmod = score['syntax']['allmod']
    c = score['syntax']['c']
    cstr = score['syntax']['CSTR']
    arg = score['argument_scores']['arg_cnt']
    c2sdm_c = arg - (arg/c)
    cstr_c = cstr / c

    if cvs1 > 0.44:
        cvs1_score = 3
    elif cvs1 > 0.04:
        cvs1_score = 2+((cvs1-0.24)/0.2)
    else:
        cvs1_score = 1

    if cvv1 > 2.85:
        cvv1_score = 3
    elif cvv1 > 1.95:
        cvv1_score = 2+((cvv1-2.4)/0.45)
    else:
        cvv1_score = 1

    if cc > 8:
        cc_score = 3
    elif cc > 3:
        cc_score = 2+((cc-8)/5)
    else:
        cc_score = 1

    if allmod > 19:
        allmod_score = 3
    elif allmod > 7:
        allmod_score = 2+((allmod-13)/6)
    else:
        allmod_score = 1

    if cstr_c > 4:
        cstr_c_score = 3
    elif cstr > 2:
        cstr_c_score = 2+((cstr_c-3)/1)
    else:
        cstr_c_score = 1

    if c2sdm_c > 2:
        c2sdm_c_score = 3
    elif c2sdm_c > 0:
        c2sdm_c_score = 2+((c2sdm_c-1))
    else:
        c2sdm_c_score = 1

    summed_score = (cvs1_score * -.0469) + (cvv1_score * 0.411034) + (cc_score * 0.257931) + (allmod_score * 0.605517) + (cstr_c_score * -0.30483) + (c2sdm_c_score * 0.077241)

    if summed_score >= 2.4:
        g3score = 3
    else:
        g3score = 2

    return g3score


def calculate_g2(score, source_score):
    w = score['syntax']['w']
    n3 = int(source_score[0])
    n5 = int(source_score[2])

    original_n3 = w + 2
    ratio = n3 / original_n3


    if w > 205 or n5 > 2 or ratio > 0.18:
        g2score = 1
    else:
        g2score = 2

    return g2score

def grademe(pre_scores, source_scores):

    """
    Decides scores 1~4 based on transformation of results from AnalyzeText.
    If less than 50 words, automatic grade of 1 is given.
    Otherwise, sends particular AnalyzeText results to functions to determine if they should be a 2, 3, or 4.
    :param pre_scores:
    :return:
    """

    post_p_scores = []
    i = 0
    for score in pre_scores:
        w = score['syntax']['w']
        filename = score['scores']['filename']

        if w < 50:
            post_p = 1
        else:
            source_score = source_scores[i]
            g2 = calculate_g2(score, source_score)
            if g2 == 1:
                post_p = g2
            else:
                post_p = calculate_g3(score, source_scores)
        i += 1
        post_p_scores.append((filename, post_p))

    return post_p_scores

def analyze_text(input_path):
    input_filepath = os.path.join(os.getcwd(), input_path)
    mode = check_mode(input_filepath)

    ac = ArgCounter('arg_counter/word_list.txt')



    if mode == 'directory':
        scores = []
        for fdx, filename in enumerate(os.listdir(input_filepath)):
            if filename.endswith('.txt'):
                result = process(os.path.join(input_filepath, filename), filename, ac)
                scores.append(result)
        return scores

def source_scores_getter(input_path):
    input_filepath = os.path.join(os.getcwd(), input_path)
    mode = check_mode(input_filepath)

    if mode == 'directory':
        source_scores = []
        for fdx, filename in enumerate(os.listdir(input_filepath)):
            if filename.endswith('.txt'):
                result = source_check(os.path.join(input_filepath, filename))
                source_scores.append(result)
        return source_scores

def rater(i_path):
    """
    Calls spacy_full to run analyzeText which gets a set of scores from an input text.
    Also calls source_checker to check against the sources text.
    Runs grademe on the AnalyzeText result and source checker_results.
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
    grades = grademe(analyze_text(i_path), source_scores_getter(i_path))
    write2csv(grades)


if __name__ == '__main__':
    assert sys.argv[1], 'input file parameter missing.'
    rater(sys.argv[1])
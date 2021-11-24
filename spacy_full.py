#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from collections import Counter

import spacy

from L2SCA.analyzeText4 import division
from arg_counter.arg_counter import ArgCounter
from lca.lc_anc3 import prepare_empty_results, read_coca_frequent_data, process_lex_stats_coca, process_scores
from main import read_input_text, check_mode, write_header_and_data_to_file


def process_spacy_syntax(spacy_syntax, word_count):
    count_dict = dict(Counter(spacy_syntax))
    w = word_count
    s = count_dict['ROOT']

    subj_keys = ['nsubj', 'nsubjpass']
    subj = 0
    for k in subj_keys:
        if k in count_dict:
            subj += count_dict[k]

    nmod_keys = ['nmod', 'npmod', 'tmod', 'poss']
    nmod = 0
    for k in nmod_keys:
        if k in count_dict:
            nmod += count_dict[k]

    pd_keys = ['acl', 'relcl']
    pd = 0
    for k in pd_keys:
        if k in count_dict:
            pd += count_dict[k]

    cc_keys = ['csubj', 'csubjpass', 'ccmop', 'xcomp']
    cc = 0
    for k in cc_keys:
        if k in count_dict:
            cc += count_dict[k]

    # compute the 6 additional syntactic complexity indices
    mls = division(w, s)
    mlc = division(w, subj)
    c_s = division(subj, s)
    nmod_s = division(nmod, s)
    pd_s = division(pd, s)
    cc_s = division(cc, s)

    return {'w': w, 's': s, 'Subj': subj, 'nmod': nmod, 'pd': pd, 'cc': cc, 'mls': mls, 'mlc': mlc, 'c_s': c_s,
            'nmod_s': nmod_s, 'pd_s': pd_s, 'cc_s': cc_s}


def process_spacy(input_text, filename):
    """

    :param input_text:
    :param filename:
    :return:
    """
    spacy_results = prepare_empty_results()
    wordranks = read_coca_frequent_data()
    nlp = spacy.load("en_core_web_lg")
    spacy_tokens = nlp(input_text)
    spacy_syntax = []
    for idx, token in enumerate(spacy_tokens):
        spacy_word = spacy_tokens[idx].text
        spacy_tag = spacy_tokens[idx].tag_
        spacy_lemma = spacy_tokens[idx].lemma_
        spacy_syntax.append(spacy_tokens[idx].dep_)
        spacy_results = process_lex_stats_coca(spacy_word, spacy_lemma, spacy_tag, spacy_results, wordranks)

    spacy_scores = process_scores(filename, spacy_results)
    word_count = len([token for token in spacy_tokens if
                      token.is_alpha or token.shape_ == 'dd'])  # dd is spacy's definition for digits.
    spacy_syntax_results = process_spacy_syntax(spacy_syntax, word_count)
    return spacy_scores, spacy_syntax_results


def build_header(scores):
    header = ''
    for k in scores[0]['scores'].keys():
        header += f'{k},'
    for k in scores[0]['syntax'].keys():
        header += f'{k},'
    header += '\n'
    return header


def stringify_scores(scores):
    """
    Scores array is a list of dictionaries
    Format:
    [{'filename': filename, 'scores': spacy_scores, 'syntax': spacy_syntax_results},...]

    :param scores:
    :return:
    """
    string_scores = ''
    for sc in scores:
        for v in sc['scores'].values():
            string_scores += f'{v},'
        for v in sc['syntax'].values():
            string_scores += f'{v},'
        string_scores += '\n'
    return string_scores


def process_d2_d3(arg_count, word_count):
    d2 = arg_count / word_count
    d3 = arg_count - (100*arg_count/word_count)
    return d2, d3


def process():
    pass
#    return {'scores': spacy_scores, 'syntax': spacy_syntax_results, 'arguments': arg_count,
#                               'argument_details': details, 'd2': d2, 'd3': d3}

def main(input_path):
    input_filepath = os.path.join(os.getcwd(), input_path)
    mode = check_mode(input_filepath)

    ac = ArgCounter('./arg_counter/test/word_list.txt')

    if mode == 'file':
        filename = input_path
        text_lines = read_input_text(input_path)
        input_text = ''.join(text_lines)
        spacy_scores, spacy_syntax_results = process_spacy(input_text, filename)
        arg_count, counts = ac.count_arguments(input_text)
        d2, d3 = process_d2_d3(arg_count, spacy_scores)
        print(f'{spacy_scores}\n{spacy_syntax_results}')
        print(f'{arg_count}\n{counts}')

    if mode == 'directory':
        scores = []
        for fdx, filename in enumerate(os.listdir(input_filepath)):
            if filename.endswith('.txt'):
                text_lines = read_input_text(os.path.join(input_filepath, filename))
                #result = process(read_input_text(os.path.join(input_filepath, filename)))
                input_text = ''.join(text_lines)
                spacy_scores, spacy_syntax_results = process_spacy(input_text, filename)
                arg_count, details = ac.count_arguments(input_text)
                d2, d3 = process_d2_d3(arg_count, spacy_syntax_results['w'])

                scores.append({'scores': spacy_scores,
                               'syntax': spacy_syntax_results,
                               'arguments': arg_count,
                               'argument_details': details,
                               'd2': d2,
                               'd3': d3})

        header = build_header(scores)
        string_scores = stringify_scores(scores)
        write_header_and_data_to_file(header, string_scores, os.path.join(os.getcwd(),
                                                                          f'./output/spacy_full_out_{len(scores)}.csv'))


if __name__ == '__main__':
    assert sys.argv[1], 'input file parameter missing.'
    main(sys.argv[1])

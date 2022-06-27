#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from collections import Counter
from pathlib import Path

import spacy

from L2SCA.analyzeText4 import division
from arg_counter.arg_counter import ArgCounter
from lca.lc_anc3 import prepare_empty_results, read_coca_frequent_data, process_lex_stats_coca, process_scores
from main import read_input_text, check_mode, write_header_and_data_to_file


def process_spacy_syntax(spacy_syntax, word_count):
    count_dict = dict(Counter(spacy_syntax))
    w = word_count
    s = count_dict['ROOT']

    try:
        nsubjpass = count_dict['nsubjpass']
    except KeyError:
        nsubjpass = 0

    try:
        csubj = count_dict['csubj']
    except KeyError:
        csubj = 0

    try:
        csubjpass = count_dict['csubjpass']
    except KeyError:
        csubjpass = 0

    try:
        ccomp = count_dict['ccomp']
    except KeyError:
        ccomp = 0

    try:
        xcomp = count_dict['xcomp']
    except KeyError:
        xcomp = 0

    try:
        adverbclause = count_dict['advcl']
    except KeyError:
        adverbclause = 0

    try:
        acl = count_dict['acl']
    except KeyError:
        acl = 0

    try:
        relcl = count_dict['relcl']
    except KeyError:
        relcl = 0

    clause_keys = ['nsubj', 'nsubjpass', 'csubj', 'csubjpass']
    clause = 0
    for k in clause_keys:
        if k in count_dict:
            clause += count_dict[k]

    nmod_keys = ['nmod', 'npmod','tmod', 'poss']
    nmod = 0
    for k in nmod_keys:
        if k in count_dict:
            nmod += count_dict[k]

    omod_keys = ['advmod', 'amod', 'appos']
    omod = 0
    for k in omod_keys:
        if k in count_dict:
            omod += count_dict[k]

    cord_keys = ['conj', 'cc']
    cord = 0
    for k in cord_keys:
        if k in count_dict:
            cord += count_dict[k]

    dc_keys = ['acl', 'relcl', 'advcl', 'ccomp']
    dc = 0
    for k in dc_keys:
        if k in count_dict:
            dc += count_dict[k]

    # compute the additional syntactic complexity indices
    T = clause - (adverbclause + relcl + acl)
    VP = ccomp + clause
    passives = nsubjpass + csubjpass
    allmod = nmod + omod
    CSTR = (dc + xcomp + cord + nmod + omod)
    adjcl = acl + relcl
    mls = division(w, s)
    mlt = division(w, T)
    mlc = division(w, clause)
    c_s = division(clause, s)
    vp_t = division(VP, T)
    c_t = division(clause, T)
    t_s = division(T, s)
    co_s = division(cord, s)
    co_t = division(cord, T)
    co_c = division(cord, clause)
    adv_s = division(adverbclause, s)
    adv_t = division(adverbclause, T)
    adv_c = division(adverbclause, clause)
    adj_s = division(adjcl, s)
    adj_t = division(adjcl, T)
    adj_c = division(adjcl, clause)
    dc_s = division(dc, s)
    dc_t = division(dc, T)
    dc_c = division(dc, clause)
    pass_s = division(passives, s)
    pass_t = division(passives, T)
    pass_c = division(passives, clause)
    allmod_s = division(allmod, s)
    allmod_t = division(allmod, T)
    allmod_c = division(allmod, clause)
    CSTR_s = division(CSTR, s)
    CSTR_t = division(CSTR, T)
    CSTR_c = division(CSTR, clause)


    return {'w': w, 's': s, 'c': clause, 't-unit':T, 'vp':VP, 'ccomp':ccomp, 'xcomp':xcomp, 'cc': cord, 'advcl':adverbclause, 'acl':acl, 'relcl':relcl, 'adjcl':adjcl, 'nmod': nmod, 'omod': omod, 'allmod':allmod, 'dc': dc,  'pass':passives, 'CSTR':CSTR,
            'mls': mls, 'mlt':mlt, 'mlc': mlc, 'c_s': c_s, 'vp_t':vp_t, 'c_t':c_t, 't_s': t_s, 'co_s': co_s, 'co_t':co_t, 'co_c':co_c, 'adv_s':adv_s, 'adv_t':adv_t, 'adv_c':adv_c,
            'adj_s':adj_s, 'adj_t':adj_t, 'adj_c':adj_c, 'dc_s':dc_s, 'dc_t':dc_t, 'dc_c':dc_c, 'pass_s':pass_s, 'pass_t':pass_t, 'pass_c':pass_c, 'allmod_s':allmod_s, 'allmod_t':allmod_t, 'allmod_c':allmod_c, 'CSTR_s':CSTR_s, 'CSTR_t':CSTR_t, 'CSTR_c':CSTR_c}


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
    for key in scores[0]:
        for k in scores[0][key].keys():
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
        for key in sc.keys():
            for v in sc[key].values():
                string_scores += f'{v},'
        string_scores += '\n'
    return string_scores


def list_stringify_scores(scores):
    string_scores_list = []

    for sc in scores:
        string_score = ''
        for key in sc.keys():
            for v in sc[key].values():
                string_score += f'{v},'
        string_score += '\n'
        string_scores_list.append(string_score)
    return string_scores_list


def process_arguments(arg_count, word_count):
    return {'arg_cnt': arg_count,
            'arg_pct': arg_count / word_count,
            'arg_den': arg_count - (100*arg_count/word_count)}


def process(file_path: str, filename: str, arg_counter: ArgCounter):
    """

    :param file_path:
    :param filename:
    :param arg_counter:
    :return:
    """
    text_lines = read_input_text(file_path)
    input_text = ''.join(text_lines)
    spacy_scores, spacy_syntax_results = process_spacy(input_text, filename)
    arg_count, details = arg_counter.count_arguments(input_text)
    argument_scores = process_arguments(arg_count, spacy_syntax_results['w'])
    return {'scores': spacy_scores, 'syntax': spacy_syntax_results, 'argument_scores': argument_scores}


def main(input_path):
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

        header = build_header(scores)
        string_scores = list_stringify_scores(scores)
        write_header_and_data_to_file(header, string_scores, os.path.join(os.getcwd(),
                                                                          f'./output/spacy_full_out_{len(scores)}.csv'))


if __name__ == '__main__':
    assert sys.argv[1], 'input file parameter missing.'
    main(sys.argv[1])

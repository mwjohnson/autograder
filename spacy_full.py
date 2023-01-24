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
    T = s + ccomp
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

def process_phrase(spacy_deps, spacy_pos, spacy_heads, spacy_words, spacy_children, spacy_lemmas):
    """
    Creates phrasal complexity measures based on Kyle (2016) and Kyle & Crossley (2018). Specifically, going after
    Av_nom_deps_NN, Prep_pobj_deps_NN, and Pobj_NN_SD (as of 10/14/2022) because though TAASSC (Kyle, 2016) offer a lot
    of measures, this program just focuses on a few that are indicative of L2 proficiency for L1 Japanese EFL learners,
    and so far these are consistently correlated with both as per (forthcoming paper). The NN means that pronouns and
    proper nouns are discluded from the counts.
    Also, does a rough calculation of Satellite-Framing, which can be considered a type of phrasal complexity.
    :param spacy_deps:
    :return:
    """

    def stdev(data):
        """
        Calculates standard deviation of a data set. Would rather write it than wazawaza import just for this
        :param data:
        :return:
        """
        n = len(data)
        if n == 0 or n == 1:
            return 0

        else:
            mean = sum(data) / n
            dev = [(x - mean) ** 2 for x in data]
            variance = sum(dev) / (n - 1)
            mystdev = variance ** 0.5
            return mystdev

    def safe_avg(data):
        n = len(data)
        if n == 0:
            return 0
        else:
            mean = sum(data) / n
            return mean

    nom_deps = 0
    phrase_deps = []
    phrases = 0
    pobj = 0
    pobj_deps = []
    pobj_prep_deps = []
    preps = []
    prep_pobj = 0
    prep_pobj2 = 0
    stative_verbs = ["be", "exist", "appear", "feel", "hear", "look", "see", "seem", "belong", "have", "own", "possess",
                     "like", "live", "want", "wish", "prefer", "love", "hate", "make", "become", "meet", "depend",
                     "fit", "touch", "matter", "lay", "lie", "find"]
    satellites = ["aboard", "above", "across", "after", "against", "ahead", "along", "amid", "among",
                  "amongst", "around", "aside", "away", "back", "before", "behind", "below", "beneath", "beside",
                  "between", "beyond", "down", "in", "inside", "into", "near", "off", "on", "onto", "opposite",
                  "out", "outside", "over", "past", "through", "toward", "towards", "together", "under",
                  "underneath", "up", "upon"]
    likely_dates = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                    "November", "December", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
                    "Sunday"]
    satellite_framings = 0
    verbs = 0
    list_o_verbs = []
    list_o_vb_lemmas = []

    for i in range(0, len(spacy_pos)):
        pos = spacy_pos[i]
        verb_lemma = spacy_lemmas[i]
        verb = spacy_words[i]
        if pos == "VERB":
            list_o_verbs.append(verb)
            list_o_vb_lemmas.append(verb_lemma)


    for i in range(0, len(spacy_deps)):
        dep = spacy_deps[i]
        pos = spacy_pos[i]
        word = spacy_words[i]
        head = spacy_heads[i]
        head = f'{head}'

        if pos == "VERB":
            verbs += 1

        if dep in ["nsubj", "nsubjpass", "agent", "ncomp", "dobj", "iobj", "pobj"] and pos == "NOUN":
            phrases += 1
            counter = 0
            tempkids = []
            for x in spacy_children[i]:
                tempkids.append(f'{x}')
            for child in tempkids:
                for x in range(0, len(spacy_deps)):
                    word_match = spacy_words[x]
                    dep_match = spacy_deps[x]
                    if word_match == child:
                        if dep_match in ["det", "amod", "prep", "poss", "vmod", "nn", "rcmod", "advmod", "conj_and", "conj_or"]:
                            counter += 1
                            break
            phrase_deps.append(counter)

        if dep == "pobj" and pos == "NOUN":
            pobj += 1
            tempdesp = []
            counter = 0
            counter2 = 0
            for x in spacy_children[i]:
                tempdesp.append(f'{x}')
            for child in tempdesp:
                for x in range(0, len(spacy_deps)):
                        word_match = spacy_words[x]
                        dep_match = spacy_deps[x]
                        if word_match == child:
                            if dep_match in ["det", "amod", "prep", "poss", "vmod", "nn", "rcmod", "advmod", "conj_and", "conj_or"]:
                                counter += 1
                            if dep_match == "prep":
                                prep_pobj += 1
                                counter2 += 1
                            break
            pobj_deps.append(counter)
            pobj_prep_deps.append(counter2)

        if pos == "ADJ": #handles adjectives as satellites
            if head in list_o_verbs:
                for y in range(0, len(list_o_verbs)):
                    word_match = list_o_verbs[y]
                    word_lemma = list_o_vb_lemmas[y]
                    if word_match == head and word_lemma not in stative_verbs:
                        x = 0
                        while x < i:
                            double_match = spacy_words[x]
                            if head == double_match:
                                satellite_framings += 1
                                break
                            else:
                                x += 1


        if pos == "ADP" and word in satellites: #handles most satellites
            if head in satellites:
                satellite_framings += 1
            elif head in list_o_verbs:
                if word in ["in", "into", "on", "onto"]:
                    if spacy_words[i+1] not in likely_dates and spacy_pos[i+1] != "NUM" and spacy_pos[i+1] != "PROPN":
                        for y in range(0, len(list_o_verbs)):
                            word_match = list_o_verbs[y]
                            word_lemma = list_o_vb_lemmas[y]
                            if word_match == head and word_lemma not in stative_verbs:
                                satellite_framings += 1
                                break

        if pos == "ADV" and word in satellites: #handles particles marked as adverbs as satellites
            if head in satellites:
                satellite_framings += 1
            elif head in list_o_verbs:
                for y in range(0, len(list_o_verbs)):
                    word_match = list_o_verbs[y]
                    word_lemma = list_o_vb_lemmas[y]
                    if word_match == head and word_lemma not in stative_verbs:
                        satellite_framings += 1
                        break


    av_nom_deps_NN = safe_avg(phrase_deps)
    Prep_pobj_deps_NN = safe_avg(pobj_prep_deps)
    Pobj_NN_SD = stdev(pobj_deps)

    return {'AvgNomDeps_NN': av_nom_deps_NN, 'Prep_PobjDeps_NN': Prep_pobj_deps_NN, 'Pobj_NN_Sd': Pobj_NN_SD, 'SFraming': satellite_framings}

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
    spacy_deps = []
    spacy_pos = []
    spacy_heads = []
    spacy_words = []
    spacy_children = []
    spacy_lemmas = []

    for idx, token in enumerate(spacy_tokens):
        spacy_words.append(spacy_tokens[idx].text)
        spacy_lemmas.append(spacy_tokens[idx].lemma_)
        spacy_pos.append(spacy_tokens[idx].pos_)
        spacy_deps.append(spacy_tokens[idx].dep_)
        spacy_heads.append(spacy_tokens[idx].head)
        kids = []
        for x in spacy_tokens[idx].children:
            kids.append(x)
        spacy_children.append(kids)

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
    spacy_phrase_results = process_phrase(spacy_deps, spacy_pos, spacy_heads, spacy_words, spacy_children, spacy_lemmas)
    return spacy_scores, spacy_syntax_results, spacy_phrase_results


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
    spacy_scores, spacy_syntax_results, spacy_phrase_results = process_spacy(input_text, filename)
    arg_count, details = arg_counter.count_arguments(input_text)
    argument_scores = process_arguments(arg_count, spacy_syntax_results['w'])
    return {'scores': spacy_scores, 'syntax': spacy_syntax_results, 'argument_scores': argument_scores, 'phrase': spacy_phrase_results}


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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script analyzes a single plain text file.  

It counts the occurrences of the following 9 structures in the text: words (W), sentences (S), verb phrases (VP),
clauses (C), T-units (T), dependent clauses (DC), complex T-units (CT), coordinate phrases (CP), and complex
nominals (CN).

These frequency counts are then used to compute the following 14 syntactic complexity indices of the text: mean length
of sentence (MLS), mean length of T-unit (MLT), mean length of clause (MLC), clauses per sentence (C/S), verb phrases
per T-unit (VP/T), clauses per T-unit (C/T), dependent clauses per clause (DC/C), dependent clauses per T-unit (DC/T),
T-units per sentence (T/S), complex T-unit ratio (CT/T), coordinate phrases per T-unit (CP/T), coordinate phrases per
clause (CP/C), complex nominals per T-unit (CN/T), and complex nominals per clause (CN/C).

To run the script, type the following at the command line:
python analyzeText.py inputFileName outputFileName

inputFileName is the name of your input text file. outputFileName is the name you want to assign to the output file.
Both names must be provided.

The output file will contain 2 lines. The first line is a comma-delimited list of 24 fields (including Filename,
abbreviations of the 9 structures, and abbreviations of the 14 syntactic complexity indices). The second line is a
comma-delimited list of 24 values (including the name of the input file, frequency counts of the 9 structures, and the
values of the 14 syntactic complexity indices). This format may be hard to read but allows easy import to Excel or SPSS.
"""
import os
import re
import subprocess
import sys
import logging


def division(x, y):
    """
    Divides two numbers from strings
    :param x:
    :param y:
    :return:
    """
    if float(x) == 0 or float(y) == 0:
        return 0
    return float(x) / float(y)


def initialize_pattern_list():
    """
    the following is a list of tregex patterns for various structures
    :return:
    """
    # sentence (S)
    s = "'ROOT'"

    # verb phrase (VP)
    vp = "'VP > S|SINV|SQ'"
    vp_q = "'MD|VBZ|VBP|VBD > (SQ !< VP)'"

    # clause (C)
    c = "'S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]'"

    # T-unit (T)
    t = "'S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]'"

    # dependent clause (DC)
    dc = "'SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])'"

    # complex T-unit (CT)
    ct = "'S|SBARQ|SINV|SQ [> ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]] << (SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]))'"

    # coordinate phrase (CP)
    cp = "'ADJP|ADVP|NP|VP < CC'"

    # complex nominal (CN)
    cn1 = "'NP !> NP [<< JJ|POS|PP|S|VBG | << (NP $++ NP !$+ CC)]'"
    cn2 = "'SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S] & [$+ VP | > VP]'"
    cn3 = "'S < (VP <# VBG|TO) $+ VP'"

    # fragment clause
    fc = "'FRAG > ROOT !<< (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])'"

    # fragment T-unit
    ft = "'FRAG > ROOT !<< (S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP])'"

    # list of patterns to search for
    return [s, vp, c, t, dc, ct, cp, cn1, cn2, cn3, fc, ft, vp_q]


def initialize_pattern_list_windows():
    """
    the following is a list of tregex patterns for various structures
    :return:
    """
    # sentence (S)
    s = "ROOT"

    # verb phrase (VP)
    vp = "VP > S|SINV|SQ"
    vp_q = "MD|VBZ|VBP|VBD > (SQ !< VP)"

    # clause (C)
    c = "S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]"

    # T-unit (T)
    t = "S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]"

    # dependent clause (DC)
    dc = "SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])"

    # complex T-unit (CT)
    ct = "S|SBARQ|SINV|SQ [> ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]] << (SBAR < (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]))"

    # coordinate phrase (CP)
    cp = "ADJP|ADVP|NP|VP < CC"

    # complex nominal (CN)
    cn1 = "NP !> NP [<< JJ|POS|PP|S|VBG | << (NP $++ NP !$+ CC)]"
    cn2 = "SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S] & [$+ VP | > VP]"
    cn3 = "S < (VP <# VBG|TO) $+ VP"

    # fragment clause
    fc = "FRAG > ROOT !<< (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])"

    # fragment T-unit
    ft = "FRAG > ROOT !<< (S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP])"

    # list of patterns to search for
    return [s, vp, c, t, dc, ct, cp, cn1, cn2, cn3, fc, ft, vp_q]


def get_word_count(parsed_filename):
    """
    Get the word count from the parsed_filename.
    :param parsed_filename:
    :return:
    """
    with open(parsed_filename, "r") as f:
        content = f.read()
    word_count = len(re.findall("\([A-Z]+\$? [^\)\(]+\)", content))
    return word_count


def run_standford_lex_parser(parser_path, i_filename, parsed_file):
    if sys.platform == 'win32':  # override the tregex shell script with a windows batch file for windows machines.
        command = ["java", "-mx150m", "-cp",
                   "L2SCA/stanford-parser-full-2014-01-04/stanford-parser.jar;L2SCA/stanford-parser-full-2014-01-04/stanford-parser-3.3.1-models.jar",
                   "edu.stanford.nlp.parser.lexparser.LexicalizedParser", "-outputFormat", "penn",
                   "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", i_filename, ">", parsed_file]
    else:
        command = parser_path + " " + i_filename + " > " + parsed_file
        
    a = subprocess.getoutput(command).split('\n')[-1].split()


def write_output_file(i_filename, w, patterncount, statistics_list):
    output = i_filename.split('/')[-1]
    # list of 24 comma-delimited fields
    fields = "Filename,W,S,VP,C,T,DC,CT,CP,CN,MLS,MLT,MLC,C/S,VP/T,C/T,DC/C,DC/T,T/S,CT/T,CP/T,CP/C,CN/T,CN/C"
    output += "," + str(w)
    for count in patterncount[:8]:
        output += "," + str(count)

    for ratio in statistics_list:
        output += "," + str("%.4F" % ratio)

    with open(i_filename + '.l2sca.out', 'w') as f:
        f.write(fields + "\n" + output + "\n")
    logger = logging.getLogger('autograder')
    logger.info(f'remove: {i_filename}+.l2sca.out')


def remove_temporary_parsed_file(parsed_file):
    # delete the temporary file holding the parse trees
    if os.path.exists(parsed_file) and os.getcwd() in os.path.abspath(parsed_file) and parsed_file.endswith('.parsed'):
        logger = logging.getLogger('autograder')
        logger.info(f'remove: {parsed_file}')
        os.remove(parsed_file)


def main(i_filename, parser_path="stanford-parser-full-2014-01-04/lexparser.sh", tregex_path="./tregex.sh", i_write_output_file=False):
    if sys.platform == 'win32':  # override the lexparser, use .bat in the case of windows.
        pattern_list = initialize_pattern_list_windows()
    else:
        pattern_list = initialize_pattern_list()

    assert os.path.isfile(i_filename), f'input file {i_filename} not found.'
    # name a temporary file to hold the parse trees of the input file
    parsed_file = i_filename + ".parsed"

    run_standford_lex_parser(parser_path, i_filename, parsed_file)  # parse the input file

    patterncount = []
    for pattern in pattern_list:
        if sys.platform == 'win32':  # override the tregex shell script with a windows batch file for windows machines.
            command = ["java", "-mx100m", "-classpath", "L2SCA/stanford-tregex.jar;", "edu.stanford.nlp.trees.tregex.TregexPattern", pattern,
                       parsed_file, "-C", "-o"]
        else:
            command = tregex_path + " " + pattern + " " + parsed_file + " -C -o"

        count = subprocess.getoutput(command).split('\n')[-1]
        patterncount.append(int(count))

    # update frequencies of complex nominals, clauses, and T-units
    patterncount[7] = patterncount[-4] + patterncount[-5] + patterncount[-6]
    patterncount[2] = patterncount[2] + patterncount[-3]
    patterncount[3] = patterncount[3] + patterncount[-2]
    patterncount[1] = patterncount[1] + patterncount[-1]

    w = get_word_count(parsed_file)

    # list of frequencies of structures other than words
    [s, vp, c, t, dc, ct, cp, cn] = patterncount[:8]

    # compute the 14 syntactic complexity indices
    mls = division(w, s)
    mlt = division(w, t)
    mlc = division(w, c)
    c_s = division(c, s)
    vp_t = division(vp, t)
    c_t = division(c, t)
    dc_c = division(dc, c)
    dc_t = division(dc, t)
    t_s = division(t, s)
    ct_t = division(ct, t)
    cp_t = division(cp, t)
    cp_c = division(cp, c)
    cn_t = division(cn, t)
    cn_c = division(cn, c)

    out = {'w': w, 's': patterncount[0], 'vp': patterncount[1], 'c': patterncount[2],
           't': patterncount[3], 'dc': patterncount[4], 'ct': patterncount[5], 'cp': patterncount[6],
           'cn': patterncount[7], 'MLS': mls, 'MLT': mlt, 'MLC': mlc, 'C/S': c_s, 'VP/T': vp_t, 'C/T': c_t,
           'DC/C': dc_c, 'DC/T': dc_t, 'T/S': t_s, 'CT/T': ct_t, 'CP/T': cp_t, 'CP/C': cp_c, 'CN/T': cn_t,
           'CN/C': cn_c}

    if i_write_output_file:
        statistics_list = [mls, mlt, mlc, c_s, vp_t, c_t, dc_c, dc_t, t_s, ct_t, cp_t, cp_c, cn_t, cn_c]
        write_output_file(i_filename, w, patterncount, statistics_list)

    remove_temporary_parsed_file(parsed_file)

    return out


if __name__ == '__main__':
    main(sys.argv[1])

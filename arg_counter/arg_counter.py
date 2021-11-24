#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from collections import Counter

from main import read_input_text


def load_word_list(filename):
    word_list = read_input_text(filename)
    unique_words = list(dict.fromkeys(word_list))
    clean_words = []
    for word in unique_words:
        clean_words.append(word.strip().lower())
    if '' in clean_words:
        clean_words.remove('')  # remove any empty strings.
    return clean_words


class ArgCounter:

    def __init__(self, word_list_filepath):
        self.word_list = load_word_list(word_list_filepath)

    def count_arguments_substring(self, i_text):
        count = 0
        items = []
        text = i_text.lower()
        for word in self.word_list:
            if word in text:
                count += 1
                items.append(word)
        counts = dict(Counter(items))
        return count, counts

    def count_arguments_single(self, i_text):
        text = i_text.lower()

        text_words = re.split("\W+", text)
        details = {w: text_words.count(w) for w in self.word_list}
        count = sum(details.values())
        return count, details

    def count_arguments_regex_substring(self, i_text):
        text = i_text.lower()
        p = re.compile('|'.join(re.escape(w) for w in self.word_list))
        items = p.findall(text)
        details = dict(Counter(items))
        count = sum(details.values())
        return count, details

    def count_arguments(self, i_text):
        text = i_text.lower()
        regex_string = "|".join(rf"\b{re.escape(word)}\b" for word in self.word_list)
        regex = re.compile(regex_string, re.IGNORECASE)
        items = regex.findall(text)
        details = dict(Counter(items))
        count = sum(details.values())
        return count, details


def main():
    # read word list
    ac = ArgCounter('./test/word_list.txt')
    # read input text
    input_text = "With regards to your mother, I told her that I have the giggles because I do. " \
                 "In regards to your father, I have a superiority complex. In addition, I kinda wanna" \
                 " disagree, but at the same time regarding cola. Additionally, not because I'm better." \
                 "addition addition "
    # a1, c1 = ac.count_arguments_substring(input_text)
    # a2, c2 = ac.count_arguments_single(input_text)
    # a3, c3 = ac.count_arguments_regex_substring(input_text)
    arg_count, counts = ac.count_arguments(input_text)

    print(f'{arg_count}\n{counts}')


if __name__ == '__main__':
    main()

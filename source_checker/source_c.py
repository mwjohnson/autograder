import re
import sys
from collections import Counter
import os
from main import read_input_text, check_mode, write_header_and_data_to_file


def ngram(source, i_text, n):
    count = 0
    # preps source and input texts for comparison
    items = []
    text = read_input_text(i_text)
    tokens2 = ''.join(text)
    tokens = re.split("\\s+", tokens2)
    source_text = read_input_text(source)
    source_tokens2 = ''.join(source_text)
    source_tokens = re.split("\\s+", source_tokens2)
    result = []
    source_result = []
    # prepare lists of n-grams for both source and input texts
    for word in range(len(tokens) - n + 1):
        temp = [tokens[j] for j in range(word, word + n)]
        result.append(" ".join(temp))

    for word2 in range(len(source_tokens) - n + 1):
        temp2 = [source_tokens[k] for k in range(word2, word2 + n)]
        source_result.append(" ".join(temp2))

    # check the lists of n-grams against each other
    for entry in source_result:
        if entry in result:
            count += 1
            items.append(entry)
    counts = (Counter(items))
    return count, counts


def prepare_all(input_text):
    # read source text
    original_text = './source_checker/original.txt'
    # read input file

    n = 3
    scores = []
    # provide 3-grams through 7-grams. Can be modified by amending above and/or below line.
    while n < 8:
        source_count, counts = ngram(original_text, input_text, n)
        scores.append(f'{source_count}')  # str(source_count)
        n = n + 1

    return scores


def main(input_path):
    input_filepath = os.path.join(os.getcwd(), input_path)
    mode = check_mode(input_filepath)

    if mode == 'file':
        result = prepare_all(input_path)
        print(f"Results for {result}")

    if mode == 'directory':
        scores = []
        for fdx, filename in enumerate(os.listdir(input_filepath)):
            if filename.endswith('.txt'):
                result = prepare_all(os.path.join(input_filepath, filename))
                result.insert(0, filename)
                scores.append(",".join(result) + '\n')

        header = 'filename,3-gram,4-gram,5-gram,6-gram,7-gram\n'
        write_header_and_data_to_file(header, scores, os.path.join(os.getcwd(),
                                                                   f'source_check_scores_{len(scores)}.csv'))


if __name__ == '__main__':
    assert sys.argv[1], 'input file parameter missing.'
    print(f'{sys.argv[1]}')
    main(sys.argv[1])

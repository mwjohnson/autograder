import random
import string
import sys
from math import sqrt, log
import nltk
import spacy
from nltk.stem import WordNetLemmatizer


# Returns the keys of dictionary d sorted by their values
def sort_by_value(d):
    items = d.items()
    backitems = [[v[1], v[0]] for v in items]
    backitems.sort()
    return [backitems[i][1] for i in range(0, len(backitems))]


# NDW for first z words in a sample
def getndwfirstz(z, lemmalist):
    ndwfirstztype = {}
    for lemma in lemmalist[:z]:
        ndwfirstztype[lemma] = 1
    return len(ndwfirstztype.keys())


# NDW expected random z words, 10 trials
def getndwerz(z, lemmalist):
    ndwerz = 0
    for i in range(10):
        ndwerztype = {}
        erzlemmalist = random.sample(lemmalist, z)
        for lemma in erzlemmalist:
            ndwerztype[lemma] = 1
        ndwerz += len(ndwerztype.keys())
    return ndwerz / 10.0


# NDW expected random sequences of z words, 10 trials
def getndwesz(z, lemmalist):
    ndwesz = 0
    for i in range(10):
        ndwesztype = {}
        startword = random.randint(0, len(lemmalist) - z)
        eszlemmalist = lemmalist[startword:startword + z]
        for lemma in eszlemmalist:
            ndwesztype[lemma] = 1
        ndwesz += len(ndwesztype.keys())
    return ndwesz / 10.0


# MSTTR
def getmsttr(z, lemmalist):
    samples = 0
    msttr = 0.0
    while len(lemmalist) >= z:
        samples += 1
        msttrtype = {}
        for lemma in lemmalist[:z]:
            msttrtype[lemma] = 1
        msttr += len(msttrtype.keys()) / float(z)
        lemmalist = lemmalist[z:]
    return msttr / samples


def isLetterNumber(character):
    if character in string.printable and character not in string.punctuation:
        return 1
    return 0


def isSentence(line):
    for character in line:
        if isLetterNumber(character):
            return 1
    return 0


def read_file():
    with open(sys.argv[1], 'r') as f:
        lemlines = f.readlines()
    return lemlines


def prepare_empty_results():
    return {
        'wordtypes': {}, 'wordtokens': 0,
        'swordtypes': {}, 'swordtokens': 0,

        'lextypes': {}, 'lextokens': 0,
        'slextypes': {}, 'slextokens': 0,

        'verbtypes': {}, 'verbtokens': 0, 'sverbtypes': {},

        'adjtypes': {}, 'adjtokens': 0,
        'advtypes': {}, 'advtokens': 0,
        'nountypes': {}, 'nountokens': 0,

        'lemmaposlist': [], 'lemmalist': []
    }


def process_wordrank(anc_all_filename="./lca/anc_all_count.txt"):
    # reads information from bnc wordlist
    adjdict = {}
    verbdict = {}
    noundict = {}
    worddict = {}

    with open(anc_all_filename, 'rb') as f:
        wordlist = f.readlines()

    pos_lookup = {}
    pos_dict = {}
    for word in wordlist:
        wordinfo = word.strip()
        if not wordinfo or b"Total words" in wordinfo:
            continue
        infolist = wordinfo.split()
        lemma = infolist[1]
        pos = infolist[2].decode('utf-8')
        frequency = int(infolist[3])
        worddict[lemma] = worddict.get(lemma, 0) + frequency
        if pos[0] == "J":
            adjdict[lemma] = adjdict.get(lemma, 0) + frequency
        elif pos[0] == "V":
            verbdict[lemma] = verbdict.get(lemma, 0) + frequency
        elif pos[0] == "N":
            noundict[lemma] = noundict.get(lemma, 0) + frequency
        pos_lookup[lemma] = pos

        if pos not in pos_dict:
            pos_dict[pos] = 1
    wordranks = sort_by_value(worddict)
    adjranks = sort_by_value(adjdict)
    nounranks = sort_by_value(noundict)
    verbranks = sort_by_value(verbdict)
    return wordranks, adjdict, pos_lookup


def process_lex_stats(word, lemma, pos, result, wordranks, adjdict):
    if pos not in string.punctuation and pos != "SYM":
        result['lemmaposlist'].append(lemma)
        result['lemmalist'].append(word)
        result['wordtokens'] += 1
        result['wordtypes'][word] = 1
        word_byte = str.encode(word)
        if word_byte not in wordranks[-2000:] and pos != "NN" or pos != "CD":
            result['swordtypes'][word] = 1
            result['swordtokens'] += 1
        if pos[0] == "N":
            result['lextypes'][word] = 1
            result['nountypes'][word] = 1
            result['lextokens'] += 1
            result['nountokens'] += 1
            if word_byte not in wordranks[-2000:]:
                result['slextypes'][word] = 1
                result['slextokens'] += 1
        elif pos[0] == "J":
            result['lextypes'][word] = 1
            result['adjtypes'][word] = 1
            result['lextokens'] += 1
            result['adjtokens'] += 1
            if word_byte not in wordranks[-2000:]:
                result['slextypes'][word] = 1
                result['slextokens'] += 1
        elif pos[0] == "R" and (word in adjdict or (word[-2:] == "ly" and word[:-2] in adjdict)):
            result['lextypes'][word] = 1
            result['advtypes'][word] = 1
            result['lextokens'] += 1
            result['advtokens'] += 1
            if word_byte not in wordranks[-2000:]:
                result['slextypes'][word] = 1
                result['slextokens'] += 1
        elif pos[0] == "V" and word not in ["be", "have"]:
            result['verbtypes'][word] = 1
            result['verbtokens'] += 1
            result['lextypes'][word] = 1
            result['lextokens'] += 1
            if word_byte not in wordranks[-2000:]:
                result['sverbtypes'][word] = 1
                result['slextypes'][word] = 1
                result['slextokens'] += 1

    return result


def tokenize_guy(text):
    text = text.strip()
    text = text.lower()
    return text.split()


def parse_guy(text, poslookup):
    word = text.split("_")[0]
    word = word.translate(str.maketrans('', '', string.punctuation))
    try:
        pos = poslookup[str.encode(word)]
    except KeyError as e:
        print(f'parse_guy, cannot parse: {word}')
        return None, None, None
    lemma = word
    return word, lemma, pos


def process_scores(i_filename, results):
    # adjust minimum sample size here
    standard = 50
    # 3.1 NDW, may adjust the values of "standard"
    ndw = ndwz = ndwerz = ndwesz = len(results['wordtypes'].keys())
    if len(results['lemmalist']) >= standard:
        ndwz = getndwfirstz(standard, results['lemmalist'])
        ndwerz = getndwerz(standard, results['lemmalist'])
        ndwesz = getndwesz(standard, results['lemmalist'])

    # 3.2 TTR
    msttr = ttr = len(results['wordtypes'].keys()) / float(results['wordtokens'])
    if len(results['lemmalist']) >= standard:
        msttr = getmsttr(standard, results['lemmalist'])

    verbtype_count = len(results['verbtypes'].keys())
    sophisticated_verb_count = len(results['sverbtypes'].keys())
    word_count = len(results['wordtypes'].keys())
    sword_count = len(results['swordtypes'].keys())
    wordtokens = results['wordtokens']
    swordtokens = results['swordtokens']
    lextokens = results['lextokens']
    slextokens = results['slextokens']

    scores = {"filename": i_filename, "wordtypes": word_count, "swordtypes": sword_count,
              "lextypes": len(results['lextypes'].keys()), "slextypes": len(results['slextypes'].keys()), "wordtokens": wordtokens,
              "swordtokens": swordtokens, "lextokens": lextokens, "slextokens": slextokens,
              "ld": float(lextokens) / wordtokens,  # 1. lexical density
              # 2.1 lexical sophistication
              "ls1": slextokens / float(lextokens), "ls2": sword_count / float(word_count),

              # 2.2 verb sophistication
              "vs1": sophisticated_verb_count / float(results['verbtokens']),
              "vs2": sophisticated_verb_count * sophisticated_verb_count / float(results['verbtokens']),
              "cvs1": sophisticated_verb_count / sqrt(2 * results['verbtokens']),

              "ndw": ndw, "ndwz": ndwz, "ndwerz": ndwerz, "ndwesz": ndwesz, "ttr": ttr, "msttr": msttr,
              "cttr": word_count / sqrt(2 * wordtokens), "rttr": word_count / sqrt(wordtokens),
              "logttr": log(word_count) / log(wordtokens),
              "uber": (log(wordtokens, 10) * log(wordtokens, 10)) / log(wordtokens / float(word_count), 10),
              # 3.3 verb diversity

              "vv1": verbtype_count / float(results['verbtokens']),
              "svv1": verbtype_count * verbtype_count / float(results['verbtokens']),
              "cvv1": verbtype_count / sqrt(2 * results['verbtokens']),

              # 3.4 lexical diversity
              "lv": len(results['lextypes'].keys()) / float(lextokens), "vv2": len(results['verbtypes'].keys()) / float(lextokens),
              "nv": len(results['nountypes'].keys()) / float(results['nountokens']), "adjv": len(results['adjtypes'].keys()) / float(lextokens),
              "advv": len(results['advtypes'].keys()) / float(lextokens),
              "modv": (len(results['advtypes'].keys()) + len(results['adjtypes'].keys())) / float(lextokens)}

    for key in scores.keys():
        if isinstance(scores[key], float):
            scores[key] = round(scores[key], 4)
    return scores


def main(lemlines, filename):
    # nltk.download('punkt')
    # nltk.download('averaged_perceptron_tagger')
    # nltk.download('wordnet')

    guy_results = prepare_empty_results()
    spacy_results = prepare_empty_results()
    nltk_results = prepare_empty_results()

    wordranks, adjdict, pos_lookup = process_wordrank()

    lemmatizer = WordNetLemmatizer()
    nlp = spacy.load("en_core_web_lg")

    for text in lemlines:

        # Process the guys' algorithm.
        guy_tokens = tokenize_guy(text)
        for idx, token in enumerate(guy_tokens):
            guy_word, guy_lemma, guy_tag = parse_guy(token, pos_lookup)
            if guy_word and guy_lemma and guy_tag:
                guy_results = process_lex_stats(guy_word, guy_lemma, guy_tag, guy_results, wordranks, adjdict)

        # Process Spacy model
        spacy_tokens = nlp(text)
        for idx, token in enumerate(spacy_tokens):
            spacy_word = spacy_tokens[idx].text
            spacy_tag = spacy_tokens[idx].tag_
            spacy_lemma = spacy_tokens[idx].lemma_
            spacy_results = process_lex_stats(spacy_word, spacy_lemma, spacy_tag, spacy_results, wordranks, adjdict)

        # Process nltk model
        nltk_word_tokens = nltk.word_tokenize(text)
        tags = nltk.pos_tag(nltk_word_tokens)
        for idx, token in enumerate(nltk_word_tokens):
            nltk_word = nltk_word_tokens[idx]
            nltk_tag = tags[idx][1]
            nltk_lemma = lemmatizer.lemmatize(nltk_word_tokens[idx])
            nltk_results = process_lex_stats(nltk_word, nltk_lemma, nltk_tag, nltk_results, wordranks, adjdict)

    guy_scores = process_scores(filename, guy_results)
    spacy_scores = process_scores(filename, spacy_results)
    nltk_scores = process_scores(filename, nltk_results)

    print(f'guy algo: {guy_scores}')
    print(f'spacy:    {spacy_scores}')
    print(f'nltk:     {nltk_scores}')

    return spacy_scores


if __name__ == '__main__':
    filename = sys.argv[1].split("/")[-1]
    final_result = main(read_file(), filename)
    print(final_result)

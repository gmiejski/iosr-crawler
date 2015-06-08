import os
import re
import operator


class NLPExtractor(object):
    def __init__(self):
        self.stop_words_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'stopwords.txt')
        self.stop_words_pattern = self.build_stop_word_regex()

    def build_stop_word_regex(self):
        """
        Creates stop word regex.

        :return: stop word pattern.
        """
        stop_word_list = self.load_stop_words()
        stop_word_regex_list = []
        for word in stop_word_list:
            word_regex = r'\b' + word + r'(?![\w-])'
            stop_word_regex_list.append(word_regex)
        stop_word_pattern = re.compile('|'.join(stop_word_regex_list),
                                       re.IGNORECASE)
        return stop_word_pattern

    def load_stop_words(self):
        """
        Utility function to load stop words from a file and return as a list of
        words.

        :return: list A list of stop words.
        """
        stop_words = []
        for line in open(self.stop_words_path):
            if line.strip()[0:1] != "#":
                for word in line.split():  # in case more than one per line
                    stop_words.append(word)
        return stop_words

    @staticmethod
    def is_number(word):
        """
        Checks whether word is a number.

        :param str word: Word to be checked.
        :return: True or False
        """
        try:
            float(word) if '.' in word else int(word)
            return True
        except ValueError:
            return False

    @staticmethod
    def separate_words(text, min_word_return_size):
        """
        Utility function to return a list of all words that are have a length
        greater than a specified number of characters.

        :param str text: The text that must be split in to words.
        :param int min_word_return_size: The minimum no of characters a word \
        must have to be included.
        :return: list of separated words.
        """
        splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
        words = []
        for single_word in splitter.split(text):
            current_word = single_word.strip().lower()
            # leave numbers in phrase, but don't count as words,
            # since they tend to invalidate scores of their phrases
            if len(current_word) > min_word_return_size and current_word != '' \
                    and not NLPExtractor.is_number(current_word):
                words.append(current_word)
        return words

    @staticmethod
    def split_sentences(text):
        """
        Utility function to return a list of sentences.

        :param str text: The text that must be split in to sentences.
        :return: sentences List of sentences created due to split.
        """
        sentence_delimiters = re.compile(
            u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
        sentences = sentence_delimiters.split(text)
        return sentences

    @staticmethod
    def generate_candidate_keywords(sentence_list, stopword_pattern):
        """
        Generates list of keywords candidates.

        :param list sentence_list: List of sentences to be processed.
        :param str stopword_pattern: Stop words pattern.
        :return: list of keywords
        """
        phrase_list = []
        for s in sentence_list:
            tmp = re.sub(stopword_pattern, '|', s.strip())
            phrases = tmp.split("|")
            for phrase in phrases:
                phrase = phrase.strip().lower()
                if phrase != "":
                    phrase_list.append(phrase)
        return phrase_list

    @staticmethod
    def calculate_word_scores(phrase_list):
        """
        Calculates words scores based on their frequency and degree.

        :param list phrase_list: List of phrases to be processed.
        :return: mapping between word and its score.
        """
        word_frequency = {}
        word_degree = {}
        for phrase in phrase_list:
            word_list = NLPExtractor.separate_words(phrase, 0)
            word_list_length = len(word_list)
            word_list_degree = word_list_length - 1
            for word in word_list:
                word_frequency.setdefault(word, 0)
                word_frequency[word] += 1
                word_degree.setdefault(word, 0)
                word_degree[word] += word_list_degree
        for item in word_frequency:
            word_degree[item] = word_degree[item] + word_frequency[item]

        word_score = {}
        for item in word_frequency:
            word_score.setdefault(item, 0)
            word_score[item] = word_degree[item] / (
                word_frequency[item] * 1.0)
        return word_score

    @staticmethod
    def generate_candidate_keyword_scores(phrase_list, word_score):
        """
        Generates scores for candidate keywords.

        :param list phrase_list: List of phrases to be processed.
        :param map word_score: Mapping between word and its score.
        :return: mapping between phrases and their scores.
        """
        keyword_candidates = {}
        for phrase in phrase_list:
            keyword_candidates.setdefault(phrase, 0)
            word_list = NLPExtractor.separate_words(phrase, 0)
            candidate_score = 0
            for word in word_list:
                candidate_score += word_score[word]
            keyword_candidates[phrase] = candidate_score
        return keyword_candidates

    def run(self, text):
        """
        Extracts keywords from the text.

        :param str text: Text to be processed.
        :return: list of keywords.
        """
        sentence_list = NLPExtractor.split_sentences(text)
        phrase_list = NLPExtractor.generate_candidate_keywords(
            sentence_list, self.stop_words_pattern)
        word_scores = NLPExtractor.calculate_word_scores(phrase_list)
        keyword_candidates = NLPExtractor.generate_candidate_keyword_scores(
            phrase_list,
            word_scores)
        sorted_keywords = sorted(keyword_candidates.iteritems(),
                                 key=operator.itemgetter(1), reverse=True)

        keywords = []
        for keyword, _ in sorted_keywords:
            keywords.extend(re.split(r'\s+', keyword))

        return keywords

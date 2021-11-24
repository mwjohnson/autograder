import unittest

from arg_counter.arg_counter import ArgCounter


class TestArgCounter(unittest.TestCase):

    def setUp(self) -> None:
        self.ac = ArgCounter('./arg_counter/test/test_word_list_1.txt')
        self.input_text = "With regards to your mother, I told her that I have the giggles because I do. " \
                          "In regards to your father, I have a superiority complex. In addition, I kinda wanna" \
                          " disagree, but at the same time regarding cola. Additionally, not because I'm better." \
                          "addition addition "

    def test_count_arguments(self):
        # read input text
        arg_count, details = self.ac.count_arguments(self.input_text)

        expected_arg_count = 8
        expected_details = {'because': 2, 'in regards to': 1, 'in addition': 1, 'regarding': 1, 'additionally': 1, 'addition': 2}

        self.assertEqual(arg_count, expected_arg_count, f'arg_count: {arg_count} does not equal expected_arg_count: {expected_arg_count}')
        self.assertEqual(details, expected_details, f'details: {details} does not equal expected_details: {expected_details}')

    def test_abcd(self):
        pass
        # a1, c1 = self.ac.count_arguments_substring(input_text)
        # a2, c2 = self.ac.count_arguments_single(input_text)
        # a3, c3 = self.ac.count_arguments_regex_substring(input_text)


if __name__ == '__main__':
    unittest.main()

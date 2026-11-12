import re

# TODO: look at changing it out for rapidfuzz, partial ration
import Levenshtein


# https://github.com/zarifaziz/ocr-consensus/blob/main/src/ocr_extraction/consensus_pipeline.py
# https://www.geeksforgeeks.org/python/introduction-to-python-levenshtein-module/
# https://www.flagright.com/post/jaro-winkler-vs-levenshtein-choosing-the-right-algorithm-for-aml-screening


class ResultProcessor:
    def __init__(self):
        self.employees = {
            "Mikael Omlid": 1,
            "Marco Illein": 2,
            "Sebastian Gunther": 3,
            "Wiebe de Rijk": 4,
            "Jordi Torrecillas": 5,
            "Floris Hoogstijn": 6,
            "Tom Muir": 7,
            "Tengel Aas Sandtro": 8,
            "Albert Einstein": 9,
            "Isaac Newton": 10,
        }
        self.candidate_comparison_storage = {}

    def process_text_extraction_output_debug(self, result):
        self.candidate_comparison_storage.clear()
        for current_candidate in self.employees:
            # using Levenshtein.ratio() instead of instead Levenshtein.jaro-winkler(),
            # because jaro-winkler emphazises on prefix weighting, but the prefix can get irrelevant in the context of scanning the whole document
            self.candidate_comparison_storage[current_candidate] = Levenshtein.ratio(
                result, current_candidate
            )
        # https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
        best_match_name, best_match_score = max(
            self.candidate_comparison_storage.items(), key=lambda k: k[1]
        )
        print(f"The best candidate seems to be: {best_match_name}")
        print(f"With a similarity of: {best_match_score:.2%}")

    def process_text_extraction_output(self, result):
        self.candidate_comparison_storage.clear()
        for current_candidate in self.employees:
            # using Levenshtein.ratio() instead of instead Levenshtein.jaro-winkler(),
            # because jaro-winkler emphazises on prefix weighting, but the prefix can get irrelevant in the context of scanning the whole document
            self.candidate_comparison_storage[current_candidate] = Levenshtein.ratio(
                result, current_candidate
            )
        # https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
        best_match_name, best_match_score = max(
            self.candidate_comparison_storage.items(), key=lambda k: k[1]
        )
        return self.employees[best_match_name]

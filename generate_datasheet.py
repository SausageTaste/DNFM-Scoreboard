import os
from typing import List

import pytesseract as tes


tes.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

SRC_ROOT_PATH = r"C:\Users\woos8\Desktop\Refined"
OUTPUT_FOL_PATH = r"C:\Users\woos8\Desktop\CSV files"


def __get_integers_from_str(text: str):
    for x in text.split("\n"):
        x = x.replace('x', '1')
        x = x.replace(',', '')
        x = x.replace('‘', '')
        x = x.replace('I', '1')
        x = x.replace(' ', '')
        x = x.replace('o', '0')
        x = x.replace('O', '0')
        x = x.replace('s', '8')

        if not x:
            continue

        try:
            integer_value = int(x)
        except ValueError:
            # print(repr(x), repr(text))
            continue
        else:
            yield integer_value


class ScoreMap:
    def __init__(self):
        self.__dict = dict()

    def __getitem__(self, rank: int):
        return self.get_data(rank)

    def get_data(self, rank: int) -> List[int]:
        assert isinstance(rank, int)

        try:
            return self.__dict[rank]
        except KeyError:
            self.__dict[rank] = []
            return self.__dict[rank]

    def get_selected_score(self, rank: int):
        score_list = set(self[rank])

        if 0 == len(score_list):
            return None
        if 1 == len(score_list):
            return next(iter(score_list))
        else:
            if rank > 1:
                last_value = self.get_selected_score(rank - 1)
            else:
                last_value = 9999999999
            if last_value is None:
                last_value = 9999999999

            return self.__select_max_that_doesnt_exceed(score_list, last_value)

    def make_report_text(self) -> str:
        output = ""

        for i in range(1, self.__get_max_rank() + 1):
            score_set = set(self[i])
            output += f"{i:>3}: "

            if 1 == len(score_set):
                output += f"ok {self.get_selected_score(i)} -> {self[i]}\n"
            elif 0 == len(score_set):
                output += "null\n"
            else:
                output += f"error {self.get_selected_score(i)} -> {self[i]}\n"

        return output

    def make_csv_data(self) -> str:
        output_csv_data = ""

        for i in range(1, 101):
            selected_score = self.get_selected_score(i)
            if selected_score is None:
                output_csv_data += f"{i},\n"
            else:
                output_csv_data += f"{i},{selected_score}\n"

        return output_csv_data

    def __get_max_rank(self):
        return max(self.__dict.keys())

    @staticmethod
    def __select_max_that_doesnt_exceed(numbers: iter, upper_bound: int) -> int:
        number_list = list(numbers)
        number_list.sort(reverse=True)

        for x in number_list:
            if x <= upper_bound:
                return x

        raise RuntimeError()


def __iter_rank_score_image_path_pair(data_image_fol_path: str):
    for x in os.listdir(data_image_fol_path):
        if not x.endswith("_score.png"):
            continue

        score_image_path = os.path.join(data_image_fol_path, x)
        assert os.path.isfile(score_image_path)

        rank_image_name_ext = x.rstrip("_score.png") + "_rank.png"
        rank_image_path = os.path.join(data_image_fol_path, rank_image_name_ext)
        assert os.path.isfile(rank_image_path)

        yield rank_image_path, score_image_path


def __build_score_map(data_image_fol_path: str) -> ScoreMap:
    score_map = ScoreMap()
    for rank_image_path, score_image_path in __iter_rank_score_image_path_pair(data_image_fol_path):
        str_ranks = tes.image_to_string(rank_image_path, lang='ENG', config='--psm 10')
        str_scores = tes.image_to_string(score_image_path, lang='ENG', config='--psm 10')
        rank_values = list(__get_integers_from_str(str_ranks))
        score_values = list(__get_integers_from_str(str_scores))
        if len(rank_values) != len(score_values):
            continue

        for j in range(len(rank_values)):
            rank = rank_values[j]
            score_map[rank].append(score_values[j])

    return score_map


def __do_for_one(data_image_fol_path: str):
    score_map = __build_score_map(data_image_fol_path)

    output_report_data = score_map.make_report_text()
    output_file_path = os.path.join(OUTPUT_FOL_PATH, f"{os.path.split(data_image_fol_path)[-1]}.txt")
    with open(output_file_path, "w") as file:
        file.write(output_report_data)

    output_csv_data = score_map.make_csv_data()
    output_file_path = os.path.join(OUTPUT_FOL_PATH, f"{os.path.split(data_image_fol_path)[-1]}.csv")
    with open(output_file_path, "w") as file:
        file.write(output_csv_data)

    print("Done:", output_file_path)


def main():
    try:
        os.mkdir(OUTPUT_FOL_PATH)
    except FileExistsError:
        pass

    for x in os.listdir(SRC_ROOT_PATH):
        item_path = os.path.join(SRC_ROOT_PATH, x)
        if os.path.isdir(item_path):
            try:
                __do_for_one(item_path)
            except RuntimeError:
                print("Failed:", item_path)


if "__main__" == __name__:
    main()

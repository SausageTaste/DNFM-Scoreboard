import os

import pytesseract as tes


tes.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

DATA_IMAGE_FOL_PATH = r"C:\Users\woos8\Videos\DNFM\엘마 2022.04.17\refine_output"


def __get_integers_from_str(text: str):
    for x in text.split("\n"):
        x = x.replace(',', '')
        x = x.replace('‘', '')
        x = x.replace('I', '1')
        x = x.replace(' ', '')

        try:
            integer_value = int(x)
        except ValueError:
            continue
        else:
            yield integer_value


def __make_ranking_list(score_map: dict):
    ranking_list = []

    for i in range(1, 101):
        try:
            score_list = set(score_map[i])
            if 1 != len(score_list):
                ranking_list.append(None)
            else:
                ranking_list.append(next(iter(score_list)))
        except KeyError:
            ranking_list.append(None)

    assert 100 == len(ranking_list)
    return ranking_list


def __assert_ranking_list_validity(ranking_list: list):
    last_score = 999999

    for x in ranking_list:
        if x is None:
            continue

        if last_score < x:
            raise RuntimeError()
        else:
            last_score = x


def __make_csv_data(ranking_list: list):
    output_csv_data = ""

    for i in range(100):
        if ranking_list[i] is None:
            output_csv_data += f"{i + 1},\n"
        else:
            output_csv_data += f"{i + 1},{ranking_list[i]}\n"

    return output_csv_data


def __iter_rank_score_image_path_pair():
    for x in os.listdir(DATA_IMAGE_FOL_PATH):
        if not x.endswith("_score.png"):
            continue

        score_image_path = os.path.join(DATA_IMAGE_FOL_PATH, x)
        assert os.path.isfile(score_image_path)

        rank_image_name_ext = x.rstrip("_score.png") + "_rank.png"
        rank_image_path = os.path.join(DATA_IMAGE_FOL_PATH, rank_image_name_ext)
        assert os.path.isfile(rank_image_path)

        yield rank_image_path, score_image_path


def __print_score_map(score_map: dict):
    for i in range(1, max(score_map.keys()) + 1):
        if i in score_map.keys():
            if 1 == len(set(score_map[i])):
                print(f"{i:>3}: ok {score_map[i]}")
            else:
                print(f"{i:>3}: error {score_map[i]}")
        else:
            print(f"{i:>3}: null")


def __build_score_map():
    score_map = {}
    for rank_image_path, score_image_path in __iter_rank_score_image_path_pair():
        str_ranks = tes.image_to_string(rank_image_path, lang='ENG', config='--psm 6')
        str_scores = tes.image_to_string(score_image_path, lang='ENG', config='--psm 6')
        rank_values = list(__get_integers_from_str(str_ranks))
        score_values = list(__get_integers_from_str(str_scores))
        if len(rank_values) != len(score_values):
            continue

        for j in range(len(rank_values)):
            rank = rank_values[j]
            if rank not in score_map.keys():
                score_map[rank] = []
            score_map[rank].append(score_values[j])

    return score_map


def main():
    score_map = __build_score_map()
    __print_score_map(score_map)
    ranking_list = __make_ranking_list(score_map)
    __assert_ranking_list_validity(ranking_list)
    output_csv_data = __make_csv_data(ranking_list)

    output_file_path = os.path.join(DATA_IMAGE_FOL_PATH, "output.csv")
    with open(output_file_path, "w") as file:
        file.write(output_csv_data)
    print(output_file_path)


if "__main__" == __name__:
    main()

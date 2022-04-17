import os

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


def __make_csv_data(ranking_list: list):
    output_csv_data = ""

    for i in range(100):
        if ranking_list[i] is None:
            output_csv_data += f"{i + 1},\n"
        else:
            output_csv_data += f"{i + 1},{ranking_list[i]}\n"

    return output_csv_data


def __make_report_str(score_map: dict):
    output = ""

    for i in range(1, max(score_map.keys()) + 1):
        if i in score_map.keys():
            if 1 == len(set(score_map[i])):
                output += f"{i:>3}: ok {score_map[i]}\n"
            else:
                output += f"{i:>3}: error {score_map[i]}\n"
        else:
            output += f"{i:>3}: null\n"

    return output


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


def __build_score_map(data_image_fol_path: str):
    score_map = {}
    for rank_image_path, score_image_path in __iter_rank_score_image_path_pair(data_image_fol_path):
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


def __do_for_one(data_image_fol_path: str):
    score_map = __build_score_map(data_image_fol_path)
    ranking_list = __make_ranking_list(score_map)

    output_report_data = __make_report_str(score_map)
    output_file_path = os.path.join(OUTPUT_FOL_PATH, f"{os.path.split(data_image_fol_path)[-1]}.txt")
    with open(output_file_path, "w") as file:
        file.write(output_report_data)

    output_csv_data = __make_csv_data(ranking_list)
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

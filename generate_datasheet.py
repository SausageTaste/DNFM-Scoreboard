import os

import pytesseract as tes


tes.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

DATA_IMAGE_FOL_PATH = r"C:\Users\woos8\Videos\DNFM\DNFM\refine_output"


def __get_integers_from_str(text: str):
    for x in text.split("\n"):
        try:
            x = x.replace(',', '')
            integer_value = int(x)
        except ValueError:
            continue
        else:
            yield integer_value


def __make_ranking_list(score_map):
    ranking_list = []

    for i in range(1, 101):
        try:
            score_list = score_map[i]
            if 1 != len(score_list):
                ranking_list.append(None)
            else:
                ranking_list.append(next(iter(score_list)))
        except KeyError:
            ranking_list.append(None)

    assert 100 == len(ranking_list)
    return ranking_list


def __is_ranking_list_valid(ranking_list: list):
    last_score = 999999

    for x in ranking_list:
        if x is None:
            continue

        if last_score < x:
            return False
        else:
            last_score = x

    return True


def __make_csv_data(ranking_list: list):
    output_csv_data = ""

    for i in range(100):
        if ranking_list[i] is None:
            output_csv_data += f"{i + 1},\n"
        else:
            output_csv_data += f"{i + 1},{ranking_list[i]}\n"

    return output_csv_data


def main():
    score_map = {}
    for i in range(9999):
        name_image_path = os.path.join(DATA_IMAGE_FOL_PATH, f"{i:0>3}_name.png")
        score_image_path = os.path.join(DATA_IMAGE_FOL_PATH, f"{i:0>3}_score.png")

        if not os.path.isfile(name_image_path):
            break
        if not os.path.isfile(score_image_path):
            break

        str_names = tes.image_to_string(name_image_path, lang='ENG', config='--psm 4 -c preserve_interword_spaces=1')
        str_scores = tes.image_to_string(score_image_path, lang='ENG', config='--psm 4 -c preserve_interword_spaces=1')
        name_values = list(__get_integers_from_str(str_names))
        score_values = list(__get_integers_from_str(str_scores))
        if len(name_values) != len(score_values):
            continue

        for j in range(len(name_values)):
            name = name_values[j]
            if name not in score_map.keys():
                score_map[name] = set()
            score_map[name].add(score_values[j])

    ranking_list = __make_ranking_list(score_map)
    assert __is_ranking_list_valid(ranking_list)
    output_csv_data = __make_csv_data(ranking_list)

    with open(os.path.join(DATA_IMAGE_FOL_PATH, "output.csv"), "w") as file:
        file.write(output_csv_data)


if "__main__" == __name__:
    main()

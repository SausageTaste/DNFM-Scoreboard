import os

import matplotlib.pyplot as plt


SRC_ROOT_PATH = r"C:\Users\woos8\Desktop\CSV files"
OUTPUT_FOL_PATH = r"C:\Users\woos8\Desktop\Analyzed"


def __generate_data_from_csv(csv_file_path: str):
    with open(csv_file_path, "r") as file:
        for x in file.readlines():
            x = x.strip('\n')
            rank_str, score_str = x.split(',')

            if "" == score_str:
                yield int(rank_str), None
            else:
                yield int(rank_str), int(score_str)


def __check_ranking_list_validity(score_list: list):
    last_score = 999999

    for x in score_list:
        if x is None:
            continue

        if last_score < x:
            return False
        else:
            last_score = x

    return True


def __calc_sample_variance(sample_data: list, sample_mean: float):
    summation = 0
    for x in sample_data:
        summation += (x - sample_mean)**2
    return summation / (len(sample_data) - 1)


def __make_output_file_name(csv_file_path: str):
    path = os.path.relpath(csv_file_path, SRC_ROOT_PATH)
    path, _ = os.path.splitext(path)
    path = path.replace("\\", "-")
    path = path.replace("/", "-")
    return path


def __make_pure_score_list(csv_file_path: str):
    score_list = []
    for rank, score in __generate_data_from_csv(csv_file_path):
        if score is not None:
            score_list.append(score)
    return score_list


def __save_mountain_scatter(csv_file_path, output_file_path, title, score_average):
    x_axis = []
    y_axis = []

    plt.cla()
    plt.title(title, fontname="Malgun Gothic")
    plt.ylim((1850, 2300))
    plt.axhline(y=score_average, alpha=0.5)
    for rank, score in __generate_data_from_csv(csv_file_path):
        if score is None:
            plt.axvline(x=rank, color="red", alpha=0.5)
        else:
            x_axis.append(rank)
            y_axis.append(score)
    plt.scatter(x_axis, y_axis, s=1)
    plt.savefig(output_file_path, dpi=300)


def main():
    try:
        os.mkdir(OUTPUT_FOL_PATH)
    except FileExistsError:
        pass

    for item_name_ext in os.listdir(SRC_ROOT_PATH):
        if not item_name_ext.endswith(".csv"):
            continue

        item_path = os.path.join(SRC_ROOT_PATH, item_name_ext)
        if not os.path.isfile(item_path):
            continue

        item_name, _ = os.path.splitext(item_name_ext)
        pure_score_list = __make_pure_score_list(item_path)
        if not __check_ranking_list_validity(pure_score_list):
            print(f"Not a valid dataset: {item_path}")

        score_average = sum(pure_score_list) / len(pure_score_list)
        score_variance = __calc_sample_variance(pure_score_list, score_average)

        __save_mountain_scatter(item_path, f'{OUTPUT_FOL_PATH}/scatter_{item_name}.png', item_name, score_average)


if __name__ == '__main__':
    main()

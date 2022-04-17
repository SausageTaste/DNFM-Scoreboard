import os

SRC_ROOT_PATH = r"C:\Users\woos8\Desktop\CSV files"


def __generate_data_from_csv(csv_file_path: str):
    with open(csv_file_path, "r") as file:
        for x in file.readlines():
            x = x.strip('\n')
            rank_str, score_str = x.split(',')

            if "" == score_str:
                yield int(rank_str), None
            else:
                yield int(rank_str), int(score_str)


def __calc_sample_variance(sample_data: list, sample_mean: float):
    summation = 0
    for x in sample_data:
        summation += (x - sample_mean)**2
    return summation / (len(sample_data) - 1)


def __do_for_one(csv_file_path: str):
    score_list = []
    for rank, score in __generate_data_from_csv(csv_file_path):
        if score is not None:
            score_list.append(score)

    score_average = sum(score_list) / len(score_list)
    score_variance = __calc_sample_variance(score_list, score_average)
    print(score_average, score_variance)


def main():
    for x in os.listdir(SRC_ROOT_PATH):
        item_path = os.path.join(SRC_ROOT_PATH, x)
        if os.path.isfile(item_path):
            __do_for_one(item_path)


if __name__ == '__main__':
    main()

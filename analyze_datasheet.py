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


def __do_for_one(csv_file_path: str):
    print(csv_file_path)

    score_list = []
    for rank, score in __generate_data_from_csv(csv_file_path):
        if score is not None:
            score_list.append(score)

    if not __check_ranking_list_validity(score_list):
        raise RuntimeError(f"Not a valid dataset: {csv_file_path}")

    score_average = sum(score_list) / len(score_list)
    score_variance = __calc_sample_variance(score_list, score_average)

    print(f"\tmean: {score_average}")
    print(f"\tvariance: {score_variance}")


def main():
    for x in os.listdir(SRC_ROOT_PATH):
        item_path = os.path.join(SRC_ROOT_PATH, x)

        if not os.path.isfile(item_path):
            continue
        if not x.endswith(".csv"):
            continue

        __do_for_one(item_path)


if __name__ == '__main__':
    main()

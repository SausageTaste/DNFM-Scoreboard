
CSV_FILE_PATH = r"C:\Users\woos8\Videos\DNFM\엘마 2022.04.17\refine_output\output.csv"


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


def main():
    score_list = []
    for rank, score in __generate_data_from_csv(CSV_FILE_PATH):
        if score is not None:
            score_list.append(score)

    score_average = sum(score_list) / len(score_list)
    score_variance = __calc_sample_variance(score_list, score_average)
    print(score_average, score_variance)


if __name__ == '__main__':
    main()

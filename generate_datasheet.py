import os
import json
from typing import List, Dict, TextIO


SRC_ROOT_PATH = r"C:\Users\woos8\Desktop\Detected"
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


class ScoreMapRecord:
    def __init__(self):
        self.scores = []
        self.rank_str = []
        self.score_str = []

    def __str__(self):
        return f'ScoreMapRecord{{ scores: {self.scores}, rank_str: {self.rank_str}, score_str: {self.score_str} }}'

    def is_complete(self):
        if not len(self.scores):
            return False
        if not len(self.rank_str):
            return False
        if not len(self.score_str):
            return False
        return True


class ScoreMap:
    def __init__(self):
        self.__dict: Dict[int, ScoreMapRecord] = dict()

    def __getitem__(self, rank: int):
        assert isinstance(rank, int)

        try:
            return self.__dict[rank]
        except KeyError:
            self.__dict[rank] = ScoreMapRecord()
            return self.__dict[rank]

    def get_selected_score(self, rank: int):
        score_list = set(self[rank].scores)

        if rank > 1:
            last_value = self.get_selected_score(rank - 1)
        else:
            last_value = 9999999999
        if last_value is None:
            last_value = 9999999999

        if 0 == len(score_list):
            return None
        if 1 == len(score_list):
            selected = next(iter(score_list))
            if selected > last_value:
                return None
            else:
                return selected
        else:
            return self.__select_max_that_doesnt_exceed(score_list, last_value)

    def make_csv_data(self) -> str:
        output_csv_data = ""

        for i in range(1, 101):
            selected_score = self.get_selected_score(i)
            if selected_score is None:
                output_csv_data += f"{i},\n"
            else:
                output_csv_data += f"{i},{selected_score}\n"

        return output_csv_data

    def get_max_rank(self):
        return max(self.__dict.keys())

    @staticmethod
    def __select_max_that_doesnt_exceed(numbers: iter, upper_bound: int) -> int:
        number_list = list(numbers)
        number_list.sort(reverse=True)

        for x in number_list:
            if x <= upper_bound:
                return x

        raise RuntimeError()


class TextSourceRecord:
    def __init__(self):
        self.rank = None
        self.score = None
        self.file_path = None

    def __str__(self):
        return f'TextSourceRecord{{rank: {repr(self.rank)}, score: {repr(self.score)}, file: {repr(self.file_path)}}}'


class TextSourceDB:
    def __init__(self):
        self.__data: Dict[int, TextSourceRecord] = {}

    def __iter__(self):
        return iter(self.__data.values())

    def give_rank_str(self, file_index: int, possibly_rank: str):
        self.__get_record(file_index).rank = possibly_rank

    def give_score_str(self, file_index: int, possibly_score: str):
        self.__get_record(file_index).score = possibly_score

    def give_file_path(self, file_index: int, file_path: str):
        self.__get_record(file_index).file_path = file_path

    def __get_record(self, file_index: int):
        assert isinstance(file_index, int)
        if file_index not in self.__data.keys():
            self.__data[file_index] = TextSourceRecord()
        return self.__data[file_index]


def __load_detected_data_json(json_file_path: str):
    with open(json_file_path, "r", encoding="utf8") as file:
        json_data = json.load(file)

    db = TextSourceDB()

    for x in json_data:
        if x["file_name"].endswith("_rank"):
            file_index = int(x["file_name"].rstrip("_rank"))
            db.give_rank_str(file_index, x["image_content"])
            db.give_file_path(file_index, x["file_path"])
        elif x["file_name"].endswith("_score"):
            file_index = int(x["file_name"].rstrip("_score"))
            db.give_score_str(file_index, x["image_content"])
        else:
            raise RuntimeError()

    return db


def __build_score_map(db: TextSourceDB):
    score_map = ScoreMap()
    error_records = []

    for record in db:
        rank_values = list(__get_integers_from_str(record.rank))
        score_values = list(__get_integers_from_str(record.score))

        if 0 == len(rank_values):
            error_records.append(record)
            continue
        elif 1 == len(rank_values) and 1 == len(score_values):
            rank = rank_values[0]
            score_record = score_map[rank]
            score_record.scores.append(score_values[0])
            score_record.rank_str.append(record.rank)
            score_record.score_str.append(record.score)
        else:
            raise RuntimeError()

    return score_map, error_records


def __make_report_file(file: TextIO, score_map: ScoreMap, error_records: List[TextSourceRecord]):
    for i in range(1, score_map.get_max_rank() + 1):
        record = score_map[i]
        selected_score = score_map.get_selected_score(i)

        if selected_score is None:
            file.write(f'{i:0>3} ERROR\n')
        elif 1 != len(set(record.scores)):
            file.write(f'{i:0>3} WARNING\n')
        else:
            file.write(f'{i:0>3}\n')

        file.write(f'\trank strings:   {record.rank_str}\n')
        file.write(f'\tscore strings:  {record.score_str}\n')
        file.write(f'\tscores:         {record.scores}\n')
        file.write(f'\tselected score: {selected_score}\n')

    file.write(f'\n')

    for x in error_records:
        file.write(f'{x.file_path}\n')
        file.write(f'\trank:  {repr(x.rank)}\n')
        file.write(f'\tscore: {repr(x.score)}\n')


def __gen_json_path():
    for loc, folders, files in os.walk(SRC_ROOT_PATH):
        for file_name_ext in files:
            if not file_name_ext.endswith(".json"):
                continue

            file_path = os.path.normpath(os.path.join(loc, file_name_ext))
            yield file_path


def __make_output_file_path(json_file_path: str):
    output = os.path.relpath(json_file_path, SRC_ROOT_PATH)
    output = output.rstrip(".json")
    output = output.replace("\\", "-")
    output = output.replace("/", "-")
    return os.path.join(OUTPUT_FOL_PATH, output)


def __do_for_one(json_file_path: str):
    output_file_loc_name = __make_output_file_path(json_file_path)
    db = __load_detected_data_json(json_file_path)
    score_map, error_records = __build_score_map(db)

    with open(f'{output_file_loc_name}.txt', "w", encoding="utf8") as file:
        __make_report_file(file, score_map, error_records)

    output_csv_data = score_map.make_csv_data()
    output_file_path = output_file_loc_name + ".csv"
    with open(output_file_path, "w", encoding="utf8") as file:
        file.write(output_csv_data)

    print("Done:", output_file_path)


def main():
    try:
        os.mkdir(OUTPUT_FOL_PATH)
    except FileExistsError:
        pass

    for json_file_path in __gen_json_path():
        __do_for_one(json_file_path)


if "__main__" == __name__:
    main()

import os
import json
import time
import multiprocessing as mp

import pytesseract as tes

tes.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'


SRC_ROOT_PATH = r"C:\Users\woos8/Desktop\Refined"
OUTPUT_FOL_PATH = r"C:\Users\woos8\Desktop\Detected"


def __make_output_file_name(fol_path: str):
    path = os.path.relpath(fol_path, SRC_ROOT_PATH)
    path = path.replace("\\", "-")
    path = path.replace("/", "-")
    path += ".json"

    return path


def __gen_png_files(folder_path: str):
    for x in os.listdir(folder_path):
        if x.endswith(".png"):
            yield x


def __gen_work_loc():
    for loc, folders, files in os.walk(SRC_ROOT_PATH):
        if not len(files):
            continue

        yield loc


def __do_for_one(loc: str):
    output_file_path = os.path.join(OUTPUT_FOL_PATH, __make_output_file_name(loc))
    json_data = []
    start_time = time.time()

    for file_name_ext in __gen_png_files(loc):
        file_name, file_ext = os.path.splitext(file_name_ext)
        file_path = os.path.normpath(os.path.join(loc, file_name_ext))
        image_content = tes.image_to_string(file_path, lang='ENG', config='--psm 10')

        json_data.append({
            "file_name": file_name,
            "file_path": file_path,
            "image_content": image_content,
        })

    if not len(json_data):
        print(f'\tNo png image found')
        return

    with open(output_file_path, "w", encoding="utf8") as file:
        json.dump(json_data, file, indent=4)
    print(f'Done "{output_file_path}" ({time.time() - start_time:.2f} sec)')


def main():
    try:
        os.mkdir(OUTPUT_FOL_PATH)
    except FileExistsError:
        pass

    start_time = time.time()
    loc_list = list(__gen_work_loc())
    with mp.Pool() as p:
        p.map(__do_for_one, loc_list)

    print(f"All done in {time.time() - start_time:.2f} sec")


if "__main__" == __name__:
    main()

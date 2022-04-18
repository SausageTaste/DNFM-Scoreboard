import os
import json
import time

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


def main():
    try:
        os.mkdir(OUTPUT_FOL_PATH)
    except FileExistsError:
        pass

    for loc, folders, files in os.walk(SRC_ROOT_PATH):
        if not len(files):
            continue

        print(f'Start: "{loc}"')
        output_file_path = os.path.join(OUTPUT_FOL_PATH, __make_output_file_name(loc))
        print(f"\tOutput file path: \"{output_file_path}\"")
        json_data = []
        start_time = time.time()

        for file_name_ext in files:
            file_name, file_ext = os.path.splitext(file_name_ext)
            file_path = os.path.normpath(os.path.join(loc, file_name_ext))
            image_content = tes.image_to_string(file_path, lang='ENG', config='--psm 10')

            json_data.append({
                "file_name": file_name,
                "file_path": file_path,
                "image_content": image_content,
            })

        with open(output_file_path, "w", encoding="utf8") as file:
            json.dump(json_data, file, indent=4)
        print(f'\tFinished in {time.time() - start_time:2.f} seconds')


if "__main__" == __name__:
    main()

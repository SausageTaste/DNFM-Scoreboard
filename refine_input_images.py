import os

from PIL import Image


SRC_IMAGE_FOLDER_PATH = r"C:\Users\woos8\Videos\DNFM\아수라 2022.04.17"

TOP_CROP_Y = 0.25
BOTTOM_CROP_Y = 0.77

LEFT_MOST_CROP_X = 0.15
RIGHT_MOST_CROP_X = 0.85
BETWEEN_RANK_AND_FACE_X = 0.1


def __crop_ranking_area(image: Image):
    return image.crop((
        round(image.width * 179 / 1280),
        round(image.height * 167 / 720),
        round(image.width * 1251 / 1280),
        round(image.height * 585 / 720)
    ))


def main():
    output_folder_path = os.path.join(SRC_IMAGE_FOLDER_PATH, "refine_output")
    try:
        os.mkdir(output_folder_path)
    except FileExistsError:
        pass

    for index, item_name_ext in enumerate(os.listdir(SRC_IMAGE_FOLDER_PATH)):
        item_path = os.path.join(SRC_IMAGE_FOLDER_PATH, item_name_ext)
        if not os.path.isfile(item_path):
            continue

        image = Image.open(item_path)
        image = __crop_ranking_area(image)

        image.save(os.path.join(output_folder_path, f"{index:0>3}.png"), format="png")


if "__main__" == __name__:
    main()

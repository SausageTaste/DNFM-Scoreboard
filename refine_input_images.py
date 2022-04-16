import os

from PIL import Image


SRC_IMAGE_FOLDER_PATH = r"C:\Users\woos8\Videos\DNFM\DNFM"

TOP_CROP_Y = 0.25
BOTTOM_CROP_Y = 0.77

LEFT_MOST_CROP_X = 0.285
RIGHT_MOST_CROP_X = 0.85


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
        image = image.crop((
            LEFT_MOST_CROP_X * image.width,
            TOP_CROP_Y * image.height,
            RIGHT_MOST_CROP_X * image.width,
            BOTTOM_CROP_Y * image.height
        ))

        image_part_name = image.crop((
            0,
            0,
            0.5 * image.width,
            image.height
        ))

        image_part_score = image.crop((
            0.5 * image.width,
            0,
            image.width,
            image.height
        ))

        image_part_name.save(os.path.join(output_folder_path, f"{index:0>3}_name.png"))
        image_part_score.save(os.path.join(output_folder_path, f"{index:0>3}_score.png"))


if "__main__" == __name__:
    main()

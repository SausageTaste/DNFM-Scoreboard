import os
import time
import multiprocessing as mp

from PIL import Image, ImageOps


SRC_ROOT_PATH = r"C:\Users\woos8\Desktop\Banners"
OUTPUT_FOL_PATH = r"C:\Users\woos8\Desktop\Refined"


# https://stackoverflow.com/a/42054155
def __change_contrast(img, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))
    def contrast(c):
        value = 128 + factor * (c - 128)
        return round(max(0, min(255, value)))
    return img.point(contrast)


def __binarize_image(image: Image) -> Image:
    image = ImageOps.invert(image)
    image = __change_contrast(image, 100)
    image = image.convert("L")
    image = image.point(lambda p: 255 if p > 255//2 else 0)
    image = image.convert('1')
    return image


def __do_for_one(src_image_folder_path: str):
    output_folder_path = os.path.join(OUTPUT_FOL_PATH, os.path.split(src_image_folder_path)[-1])
    try:
        os.mkdir(output_folder_path)
    except FileExistsError:
        pass

    for index, item_name_ext in enumerate(os.listdir(src_image_folder_path)):
        item_path = os.path.join(src_image_folder_path, item_name_ext)
        if not os.path.isfile(item_path):
            continue

        one_banner = Image.open(item_path)

        rank_part = one_banner.crop((
            round(one_banner.width * 9 / 1072),
            0,
            round(one_banner.width * 100 / 1072),
            one_banner.height
        ))
        rank_part = __binarize_image(rank_part)
        rank_part.save(os.path.join(output_folder_path, f"{index:0>4}_rank.png"), format="png")

        score_part = one_banner.crop((
            round(one_banner.width * 797 / 1072),
            0,
            round(one_banner.width * 918 / 1072),
            one_banner.height
        ))
        score_part = __binarize_image(score_part)
        score_part.save(os.path.join(output_folder_path, f"{index:0>4}_score.png"), format="png")


def main():
    try:
        os.mkdir(OUTPUT_FOL_PATH)
    except FileExistsError:
        pass

    start_time = time.time()
    work_list = []
    for x in os.listdir(SRC_ROOT_PATH):
        item_path = os.path.join(SRC_ROOT_PATH, x)
        if os.path.isdir(item_path):
            work_list.append(item_path)

    with mp.Pool() as p:
        p.map(__do_for_one, work_list)

    print(f"All done in {time.time() - start_time:.2f} sec")


if "__main__" == __name__:
    main()

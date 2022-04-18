import os
import multiprocessing as mp

from PIL import Image
import matplotlib.pyplot as plt


SRC_ROOT_PATH = r"C:\Users\woos8\Desktop\Captures"
OUTPUT_FOL_PATH = r"C:\Users\woos8\Desktop\Banners"


def __crop_ranking_area(image: Image) -> Image:
    return image.crop((
        round(image.width * 179 / 1280),
        round(image.height * 167 / 720),
        round(image.width * 1251 / 1280),
        round(image.height * 585 / 720)
    ))


def __iter_image_average_colors_in_column(image: Image, x_coord: int):
    for y in range(image.height):
        pixel = image.getpixel((x_coord, y))
        assert 3 == len(pixel)
        yield sum(pixel) / len(pixel)


def __find_min_max(iterator: iter):
    item_list = list(iterator)
    return min(item_list), max(item_list)


def __find_cut_points(image: Image):
    x_coord = image.width * 1019 / 1072
    average_colors = list(__iter_image_average_colors_in_column(image, x_coord))
    min_average_color, max_average_color = __find_min_max(average_colors)
    mid_average_color = (min_average_color + max_average_color) * 0.5

    y_points_higher_than_mid = []
    for y, average_color in enumerate(average_colors):
        if average_color > mid_average_color:
            y_points_higher_than_mid.append(y)

    point_distances = []
    for i in range(len(y_points_higher_than_mid) - 1):
        point_distances.append(y_points_higher_than_mid[i + 1] - y_points_higher_than_mid[i])

    mid_distance = sum(__find_min_max(point_distances)) / 2
    discrete_points = []
    for i, point_dist in enumerate(point_distances):
        if point_dist > mid_distance:
            discrete_points.append(i + 1)
    discrete_points.insert(0, 0)
    discrete_points.append(None)

    cut_y_points = []
    for i in range(len(discrete_points) - 1):
        index_from = discrete_points[i]
        index_to = discrete_points[i + 1]
        adjacent_y_points = y_points_higher_than_mid[index_from:index_to]
        average_y_point = sum(adjacent_y_points) / len(adjacent_y_points)
        cut_y_points.append(round(average_y_point))

    return cut_y_points


def __save_cut_point_plot(image: Image, cut_y_points: list, output_file_path: str):
    x_axis = [xx for xx in range(image.height)]
    y_axis = []
    for y in range(image.height):
        pixel = image.getpixel((image.width * 1019 / 1072, y))
        average_color = sum(pixel) / len(pixel)
        y_axis.append(average_color)

    plt.cla()
    plt.plot(x_axis, y_axis, color="blue")
    for y in cut_y_points:
        plt.axvline(x=y, color="red")
    plt.savefig(output_file_path)


def __make_output_folder_path(src_image_folder_path: str):
    output = os.path.relpath(src_image_folder_path, SRC_ROOT_PATH)
    output = output.replace('\\', '-')
    output = output.replace('/', '-')
    return os.path.join(OUTPUT_FOL_PATH, output)


def __do_for_one_image(src_image_path: str, output_image_path_prefix: str):
    image = Image.open(src_image_path)
    image = __crop_ranking_area(image)
    # image.save(os.path.join(output_folder_path, f"{index:0>3}.png"), format="png")

    cut_y_points = __find_cut_points(image)
    if 0 != cut_y_points[0]:
        cut_y_points.insert(0, 0)
    cut_y_points.append(image.height)
    # __save_cut_point_plot(image, cut_y_points, os.path.join(output_folder_path, f"{index:0>3}_fig.png"))

    for i in range(len(cut_y_points) - 1):
        y_from = cut_y_points[i]
        y_to = cut_y_points[i + 1]
        one_banner = image.crop((0, y_from, image.width, y_to))
        if one_banner.height * 418 < image.height * 85:  # one_banner.height / image.height < 85 / 418
            continue
        one_banner.save(f"{output_image_path_prefix}{i:0>3}.png", format="png")


def __do_for_one(src_image_folder_path: str):
    output_folder_path = __make_output_folder_path(src_image_folder_path)
    try:
        os.mkdir(output_folder_path)
    except FileExistsError:
        pass

    for index, item_name_ext in enumerate(os.listdir(src_image_folder_path)):
        item_path = os.path.join(src_image_folder_path, item_name_ext)
        if not os.path.isfile(item_path):
            continue

        __do_for_one_image(item_path, os.path.join(output_folder_path, f"{index:0>3}_"))

    print(f"Done: {output_folder_path}")


def main():
    try:
        os.mkdir(OUTPUT_FOL_PATH)
    except FileExistsError:
        pass

    loc_list = []
    for loc, folders, files in os.walk(SRC_ROOT_PATH):
        if len(files):
            loc_list.append(loc)

    with mp.Pool() as p:
        p.map(__do_for_one, loc_list)


if "__main__" == __name__:
    main()

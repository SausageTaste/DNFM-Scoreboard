import os

import cv2


def __do_for_one_video(video_file_path: str, num_of_output: int):
    video = cv2.VideoCapture(video_file_path)
    if not video.isOpened():
        return

    output_folder_path = os.path.splitext(video_file_path)[0]
    try:
        os.mkdir(output_folder_path)
    except FileExistsError:
        pass

    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    # fps = video.get(cv2.CAP_PROP_FPS)
    mod = max(1, round(length / num_of_output))

    count = 0
    while True:
        ret, image = video.read()
        if not ret:
            return
        if 0 != int(video.get(1)) % mod:
            continue

        output_file_path = os.path.join(output_folder_path, f"frame_{count:0>3}.png")
        if not cv2.imwrite(output_file_path, image):
            raise RuntimeError()
        count += 1


def main():
    root_path = r"C:\Users\woos8\Videos\Captures"
    for x in os.listdir(root_path):
        file_path = os.path.join(root_path, x)
        if os.path.isfile(file_path):
            print(file_path)
            __do_for_one_video(file_path, 120)


if __name__ == '__main__':
    main()

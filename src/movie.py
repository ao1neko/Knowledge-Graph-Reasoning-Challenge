
import cv2
import os
from pathlib import Path
import argparse



def save_all_frames(video_path, dir_path, basename, ext='png'):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return

    os.makedirs(dir_path, exist_ok=True)
    base_path = os.path.join(dir_path, basename)

    digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))

    n = 0
    while True:
        ret, frame = cap.read()
        if ret:
            if n % 100 == 0:
                cv2.imwrite('{}_{}.{}'.format(base_path, str(n).zfill(digit), ext), frame)
            n += 1
        else:
            return



def main(PROJECT_PATH:Path):
    MOVIE_PATH = PROJECT_PATH / Path("movie/original")
    CONVERTED_PATH = PROJECT_PATH / Path("movie/converted")
    
    for genre_path in MOVIE_PATH.iterdir():
        tmp_genre = genre_path.name
        for scene_path in genre_path.iterdir():
            tmp_scene = scene_path.name
            for movie_path in (scene_path / "movies").iterdir():
                try: 
                    tmp_movie = movie_path.stem.replace(' ', '_')
                    save_all_frames(str(movie_path), CONVERTED_PATH / tmp_scene / tmp_movie, "")
                except:
                    continue
if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--PROJECT_PATH", type=str)
    args = arg_parser.parse_args()
    main(args.PROJECT_PATH)
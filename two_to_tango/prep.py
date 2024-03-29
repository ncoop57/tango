# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_prep.ipynb (unless otherwise specified).

__all__ = ['get_rand_imgs', 'vid_from_frames', 'Video', 'VideoDataset', 'get_rico_imgs', 'read_video_data',
           'get_non_duplicate_corpus', 'generate_setting2', 'get_all_texts']

# Cell
import concurrent.futures
import csv
import cv2
import ffmpeg
import json
import ntpath
import numpy
import os
import pprint
import pytesseract
import random

import matplotlib.pyplot as plt
import more_itertools as mit
import pandas as pd

from collections import defaultdict, OrderedDict
from pathlib import Path
from PIL import Image
from .utils import *
from shutil import copyfile
from tqdm.auto import tqdm

# Cell
def get_rand_imgs(vid_path, max_msecs, n = 10):
    vid = cv2.VideoCapture(str(vid_path))

    imgs = []
    while len(imgs) < n:
        msec = random.randrange(1_000, max_msecs, 1_000)
        vid.set(cv2.CAP_PROP_POS_MSEC, msec)

        success, img = vid.read()
        if success:
            imgs.append(img)

    return imgs

# Cell
def vid_from_frames(frames, output = None, fr = 30):
    """Generate video from list of frame paths."""
    if not output: output = frames.parent

    try:
        stream = ffmpeg.input(frames/'%04d.jpg')
        stream = ffmpeg.output(stream, str(output/"gen_vid.mp4"), r = fr)
        out, err = ffmpeg.run(stream)
    except Exception as e:
        print("Error occured:", e)

# Cell
class Video:
    def __init__(self, vid_path, fr = None, overwrite = False):
        self.vid_path = vid_path
        self.fr = eval(ffmpeg.probe(vid_path)["streams"][0]["avg_frame_rate"])
        if fr is not None:
            self.fr = fr
            self.vid_path = self._fix_framerate(vid_path, fr, overwrite)

        self.video = cv2.VideoCapture(str(self.vid_path))

    def show_frame(self, i):
        plt.imshow(self[i])
        plt.show()

    def _fix_framerate(self, vid_path, fr, overwrite):
        """
            Fixes each video in the list of video paths to a certain frame rate.
        """
        output_path = str(vid_path) if overwrite else str(vid_path.parent/f'{vid_path.stem}_fixed_{fr}.mp4')
        stream = ffmpeg.input(vid_path)
        stream = ffmpeg.output(stream, output_path, r = fr)
        stream = ffmpeg.overwrite_output(stream)
        out, err = ffmpeg.run(stream)

        return Path(output_path)

    def __len__(self):
        return int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

    def __getitem__(self, i):
        if i >= len(self) or i < 0:
            raise Exception(f'Frame index is not in the proper range (0, {len(self) - 1}).')
        self.video.set(cv2.CAP_PROP_POS_FRAMES, i)
        suc, frame = self.video.read()
        if not suc: return None
        return Image.fromarray(frame)

# Cell
class VideoDataset:
    def __init__(self, videos):
        self.videos = videos
        self.labels = None
        self.data = None

    def label_from_paths(self):
        self.labels = defaultdict(
            lambda: defaultdict(dict)
        )
        for vid in self.videos:
            self.labels[vid.vid_path.parent.parent.name][vid.vid_path.parent.name][vid.vid_path.parent.parent.parent.name] = vid

        return self

    def get_labels(self):
        return list(self.labels.keys())

    @staticmethod
    def from_path(path, extract_frames = False, fr = None, overwrite = False):
        videos = []
        fixed_vid_paths = sorted(path.rglob(f"*fixed_{fr}.mp4"))
        if len(fixed_vid_paths) > 0 and fr is not None:
            for vid_path in fixed_vid_paths:
                videos.append(Video(vid_path, overwrite = overwrite))
        else:
            vid_paths = list(filter(lambda x: "fixed" not in str(x), sorted(path.rglob('*.mp4'))))
            for vid_path in vid_paths:
                videos.append(Video(vid_path, fr = fr, overwrite = overwrite))

        return VideoDataset(videos)

    def __getitem__(self, label):
        return self.labels[label]

# Cell
def get_rico_imgs(path, n = None):
    rico_path = path/'rico-images/data'
    img_paths = sorted(rico_path.glob('*.jpg'))
    if n == None: n = len(img_paths)

    return [Image.open(img) for img in random.sample(img_paths, n)]

# Cell
def read_video_data(file_path):
    with open(file_path) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        data = list(csv_reader)

        idx_data = {}
        apps, bugs, app_bugs, users = set(), set(), set(), set()
        for row in data:
            app = row['app']
            bug = row['bug']
            app_bug = row['app_bug']
            user = row['final_assignment']

            apps.add(app)
            bugs.add(bug)
            app_bugs.add(app_bug)
            users.add(user)

            if app not in idx_data:
                idx_data[app] = {}
            bugs_for_app = idx_data[app]
            if bug not in bugs_for_app:
                bugs_for_app[bug] = []
            users_for_bug = bugs_for_app[bug]
            users_for_bug.append((user, app_bug + "-" + user))

    result = {
        'idx_data': idx_data,
        'apps': apps,
        'bugs': bugs,
        'app_bugs': app_bugs,
        'users': users,
        'data': data,
    }
    return result

def get_non_duplicate_corpus(bugs, bug_idx, app_bugs, br_idx, bugs_to_exclude=[]):
    if bug_idx == 0:
        other_bugs = bugs[bug_idx + 1:len(bugs)]
    elif bug_idx == len(bugs) - 1:
        other_bugs = bugs[0:bug_idx]
    else:
        other_bugs = bugs[bug_idx + 1:len(bugs)]
        other_bugs.extend(bugs[0:bug_idx])

    assert len(other_bugs) == 9, "The list of non-duplicate bugs is different than 9"
    # print(other_bugs)
    bug_reports = []
    for bug in other_bugs:
        if bug not in bugs_to_exclude:
            bug_report = app_bugs[bug][br_idx]
            bug_reports.append(bug_report[1])
    return bug_reports

def generate_setting2(data, out_path):
    Path(out_path).mkdir(parents=True, exist_ok=True)
    apps = data['apps']
    idx_data = data['idx_data']

    retrieval_runs = []
    run_id = 1

    # for each app
    for app in apps:

        app_data = idx_data[app]
        pprint.pprint(app_data)

        # for each bug
        bugs = list(idx_data[app].keys())
        for bug_idx in range(len(bugs)):
            bug = bugs[bug_idx]
            bug_reports = idx_data[app][bug]

            # for each other bug
            other_bugs_idxes = [i for i in range(len(bugs)) if i != bug_idx]
            for bug_idx2 in other_bugs_idxes:

                next_bug = bugs[bug_idx2]
                next_bug_reports = idx_data[app][next_bug]

                # for each bug report
                for br_idx in range(3):
                    query = bug_reports[br_idx][1]

                    duplicate_corpus = [bug_reports[(br_idx + 1) % 3][1], bug_reports[(br_idx + 2) % 3][1]]
                    ground_truth = duplicate_corpus.copy()
                    duplicate_corpus.extend([l[1] for l in next_bug_reports])

                    # for each user
                    for br_idx2 in range(3):
                        # get the non-duplicate corpus for each user and all other bugs except current one
                        non_duplicate_corpus = get_non_duplicate_corpus(bugs, bug_idx, app_data, br_idx2, [next_bug])

                        retrieval_job = {
                            'run_id': run_id,
                            'query': query,
                            'corpus_size': len(duplicate_corpus) + len(non_duplicate_corpus),
                            'dup_corpus': duplicate_corpus,
                            'non_dup_corpus': non_duplicate_corpus,
                            'gnd_trh': ground_truth
                        }
                        run_id += 1
                        retrieval_runs.append(retrieval_job)

    write_json_line_by_line(retrieval_runs, out_path/'setting2.json')

# Cell
def get_all_texts(vid_ds, out_path, fps):
    Path(out_path).mkdir(parents=True, exist_ok=True)

    video_output_path = os.path.join(out_path, "text_" + str(fps))
    Path(video_output_path).mkdir(parents=True, exist_ok=True)

    videos = [vid.vid_path for vid in vid_ds.videos]
    for video_path in videos:
        video_path_obj = Path(video_path)

        file_name = ntpath.basename(video_path).split(".")[0]
        video_name = file_name + "-" + str(video_path_obj.parent.parent.parent.stem)

        frame_path = os.path.join(out_path, "frames_" + str(fps), video_name)
        Path(frame_path).mkdir(parents=True, exist_ok=True)

        frames = find_file("*.jpeg", frame_path)
        if not frames:
            extract_frames(video_path_obj, frame_path, fps)
        frames = find_file("*.jpeg", frame_path)

        frames_text = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            futures = []
            for frame in frames:
                futures.append(executor.submit(process_frame, frame))
            for future in concurrent.futures.as_completed(futures):
                frames_text.append(future.result())

        frames_text = sorted(frames_text, key=lambda t: t["f"])

        video_name = video_name.replace("_fixed_30", "")
        out_file = os.path.join(video_output_path, video_name + '.json')
        write_json_line_by_line(frames_text, out_file)

        print("done: " + video_name)
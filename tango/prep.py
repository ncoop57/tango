# AUTOGENERATED! DO NOT EDIT! File to edit: dev/00_prep.ipynb (unless otherwise specified).

__all__ = ['fix_frame_rate', 'chunk_videos', 'get_rand_imgs', 'vid_from_frames', 'save_detected_frames',
           'gen_vids_from_v2s', 'run_phase1_v2s', 'Video', 'VideoDataset']

# Cell
import cv2
import ffmpeg
import json
import numpy
import os
import random
import pytesseract
import scenedetect

import matplotlib.pyplot as plt
import more_itertools as mit

from collections import defaultdict
from pathlib import Path

# scenedetect
from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import is_ffmpeg_available, split_video_ffmpeg

from shutil import copyfile

# Cell
def fix_frame_rate(video_paths, fr = 30):
    """
        Fixes each video in the list of video paths to a certain frame rate

        Returns a list of paths to the new fixed frame rate videos
    """
    fixed_paths = []
    for vp in video_paths:
        try:
            stream = ffmpeg.input(vp)
            stream = ffmpeg.output(stream, str(vp.parent/"fixed.mp4"), r = fr)
            stream = ffmpeg.overwrite_output(stream)
            out, err = ffmpeg.run(stream)

            fixed_paths.append(vp.parent/"fixed.mp4")
        except Exception as e:
            print("Error occured:", e)

    return fixed_paths

# Cell
def chunk_videos(vid_paths):
    """Chunks videos into different scenes based on their content for later processing."""

    for vp in vid_paths:
        try:
            # Setup the different managers for chunking the scenes.
            video_manager = VideoManager([str(vp)])
            stats_manager = StatsManager()
            scene_manager = SceneManager(stats_manager)

            # Add ContentDetector algorithm (constructor takes detector options like threshold).
            scene_manager.add_detector(ContentDetector())
            base_timecode = video_manager.get_base_timecode()

            # Set downscale factor to improve processing speed (no args means default).
            video_manager.set_downscale_factor()

            # Set the duration to be however long the video is and start the video manager.
            video_manager.set_duration()
            video_manager.start()

            # Perform scene detection on video_manager and grab the scenes.
            scene_manager.detect_scenes(frame_source=video_manager)
            scene_list = scene_manager.get_scene_list(base_timecode)

            # If the output dir of the chunked videos does not exist, create it.
            if not (vp.parent/"chunks").exists():
                (vp.parent/"chunks").mkdir()

            # Split the video into chunks based on the scene list and save to the "chunks" folder.
            split_video_ffmpeg([vp], scene_list,
                               str(vp.parent/"chunks/$VIDEO_NAME-$SCENE_NUMBER.mp4"),
                               "chunk"#, arg_override = args
                              )
            with open("stats.csv", 'w') as stats_file:
                stats_manager.save_to_csv(stats_file, base_timecode)
        finally:
            # Close out the video_manager.
            video_manager.release()

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
def save_detected_frames(detection_path, output_path, delta = 10):
    """
        Grab list of frames that contain touch indicators in them.
        Can adjust how many frames before and after start and end of touch indicators
        for context of interaction by adjusting delta.
    """
    output_path.mkdir(exist_ok = True)

    with open(detection_path.parent/'detected_frames/detected-frames.json') as f:
        detections = json.load(f)
    frames = [d['screenId'] for d in detections]

    groups = [list(group) for group in mit.consecutive_groups(frames)]
    for g in groups:
        s, e = g[0], g[-1]
        frames.extend(list(range(s - delta, s)))
        frames.extend(list(range(e + 1, e + delta + 1)))
    frames = sorted(list(set(frames)))
    frames = [f for f in frames if f >= 1]

    for i, frame in enumerate(frames):
        try:
            copyfile(detection_path.parent/f'extracted_frames/{frame:04}.jpg', output_path/f'{i:04}.jpg')
        except:
            continue

# Cell
def gen_vids_from_v2s(vids_path):
    for vid in sorted(vids_path.glob('*/detected_frames')):
        save_detected_frames(vid, vid.parent/'touch_indicated_frames')
        vid_from_frames(vid.parent/'touch_indicated_frames', vid.parent)

# Cell
def run_phase1_v2s(v2s_path, model_path):
    # python scripts/detection_v2s.py --object_path . --model_path /tf/data/v2s/android-video-based-record-replay/Code/Video2Scenario/data/model/saved_model_n6p/frozen_inference_graph_n6.pb
#     print(f'python {v2s_path/"scripts/detection_v2s.py"} --object-path {v2s_path} --model_path {model_path}')
    os.system(f'python {v2s_path/"scripts/detection_v2s.py"} --object-path {v2s_path} --model_path {model_path}') # need to remove this eventually as it is extremely hacky

# Cell
class Video:
    def __init__(self, vid_path, fr = None, overwrite = False):
        self.video = cv2.VideoCapture(str(vid_path))
        self.vid_path = vid_path
        self.fr = eval(ffmpeg.probe(vid_path)["streams"][0]["avg_frame_rate"])
        if fr is not None:
            self.fr = fr
            self.vid_path = self._fix_framerate(vid_path, fr, overwrite)

#     def save_frames(self, path):
#         for i, frame in enuemrate(frames):
#             cv2.imwrite(path/f'{i:04}.jpg', frame)

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

        return output_path

#     def extract_frames(self, out_path):
#         self.out_path = out_path
#         self.out_path.mkdir(parents=True, exist_ok=True)
#         vid = cv2.VideoCapture(str(self.vid_path))

#         count = 0
#         success, img = vid.read()
#         while success:
#             cv2.imwrite(str(out_path/f'{count:04}.jpg'), img)
#             success, img = vid.read()
#             count += 1

    def __len__(self):
        return int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

    def __getitem__(self, i):
        if i >= len(self) or i < 0:
            raise Exception(f'Frame index is not in the proper range (0, {len(self) - 1}).')
        self.video.set(cv2.CAP_PROP_POS_FRAMES, i)
        _, frame = self.video.read()
        return frame

# Cell
class VideoDataset:
    def __init__(self, videos):
        self.videos = videos
        self.labels = None
        self.data = None

    def label_from_paths(self):
        self.labels = defaultdict(lambda: defaultdict(list))
        for vid in self.videos:
            self.labels[vid.vid_path.parent.parent.name][vid.vid_path.parent.name].append(vid)

        return self

    def get_labels(self):
        return list(self.labels.keys())

    @staticmethod
    def from_path(path, extract_frames = False, fr = None, overwrite = False):
        vid_paths = sorted(path.rglob('*.mp4'))
        videos = []
        for vid_path in vid_paths:
#             out_path = vid_path.parent/f'{vid_path.stem}_extracted_frames' if extract_frames else None
            videos.append(Video(vid_path, fr, overwrite))

        return VideoDataset(videos)

    def __getitem__(self, label):
        return self.labels[label]
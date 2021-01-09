# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/05_cli.ipynb (unless otherwise specified).

__all__ = ['logger', 'URLs', 'download', 'VWORDS', 'N_IMGS', 'N_FRAMES_TO_KEEP', 'FPS', 'BEST_DL_MODELS',
           'BEST_IR_MODELS', 'reproduce', 'tango']

# Cell
import logging
import pickle
import pprint
import random
import requests
import subprocess
import time
import zipfile

from fastcore.script import call_parse, Param
from pathlib import Path
from .prep import *
from .features import *
from .eval import *
from .model import *
from .approach import *
from .combo import *
from tqdm.auto import tqdm

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Cell
URLs = {
    "reproduction_package": "",
}

# Cell
@call_parse
def download(
    out_path: Param("The output path to save and unzip all files.", str)
):
    out_path = Path(out_path)
    out_path.mkdir(parents=True, exist_ok=True)

    logging.info(f"Downloading and extracting datasets and models to {str(out_path)}.")
    r = requests.get(URLs["reproduction_package"])
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(out_path / "reproduction_package")

# Cell
# all hyperparameters used
VWORDS = [1_000, 5_000, 10_000]
N_IMGS = 15_000
N_FRAMES_TO_KEEP = [1, 5]
FPS = 30

BEST_DL_MODELS= [
    "SimCLR-1000vw-5ftk-bovw", "SimCLR-5000vw-5ftk-bovw_lcs",
    "SimCLR-5000vw-5ftk-bovw_weighted_lcs", "SimCLR-1000vw-5ftk-bovw_weighted_lcs"
]
BEST_IR_MODELS = [
    "ocr+ir--1ftk-all_text", "ocr+ir--5ftk-all_text",
    "ocr+ir--5ftk-unique_frames", "ocr+ir--5ftk-unique_words"
]

# Cell
def _generate_vis_results(vid_ds, out_path, art_path, vis_model):
    if vis_model == "SimCLR":
        simclr = SimCLRModel.load_from_checkpoint(
            checkpoint_path = str(
                art_path/"models"/"SimCLR"/"checkpointepoch=98.ckpt"
            )
        ).eval()
        model = SimCLRExtractor(simclr)
        sim_func = simclr_frame_sim
    else:
        model = SIFTExtractor(cv2.xfeatures2d.SIFT_create(nfeatures = 10))
        sim_func = sift_frame_sim

    logging.info(f"Computing rankings and calculating metrics for {vis_model} visual model.")
    for vw in tqdm(VWORDS):
        for ftk in tqdm(N_FRAMES_TO_KEEP):
            evaluation_metrics = {}
            cb_path = art_path/"models"/vis_model/f"cookbook_{vis_model}_{vw}vw.model"
            codebook = pickle.load(open(cb_path, "rb"))
            start = time.time()
            vid_ds_features = gen_extracted_features(vid_ds, model, FPS, ftk)
            end = time.time()
            feature_gen_time = end - start

            df, bovw_vid_ds_sims = gen_bovw_similarity(
                vid_ds, vid_ds_features, model, codebook, vw, ftk
            )
            lcs_vid_ds_sims = gen_lcs_similarity(
                vid_ds, vid_ds_features, sim_func, model, codebook, df, vw, ftk
            )
            rankings = approach(
                vid_ds, vid_ds_features, bovw_vid_ds_sims, lcs_vid_ds_sims, model, sim_func,
                codebook, df, vw, fps = FPS, ftk = ftk,
            )

            for k, v in rankings.items():
                evaluation_metrics[k] = evaluate(rankings[k])

            id_name = f"user_{N_IMGS}n_{vw}vw_{FPS}fps_{ftk}ftk"
            results_path = out_path/"results"/vis_model
            results_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Saving rankings and metrics to {str(results_path)}.")
            with open(results_path/f"rankings_{id_name}.pkl", "wb") as f:
                pickle.dump(rankings, f, protocol=pickle.HIGHEST_PROTOCOL)

            with open(results_path/f"evalhttp://localhost:8888/notebooks/main/nbs/05_cli.ipynb#uation_metrics_{id_name}.pkl", 'wb') as f:
                pickle.dump(evaluation_metrics, f, protocol=pickle.HIGHEST_PROTOCOL)

# Cell
def _generate_txt_results(vid_ds, out_path, art_path, vis_model):
    logging.info("Computing rankings and calculating metrics for textual model.")
    csv_file_path = art_path/"user_assignment.csv"
    settings_path = out_path/"evaluation_settings"
    settings_path.mkdir(parents=True, exist_ok=True)
    video_data = read_video_data(csv_file_path)
    generate_setting2(video_data, settings_path)
    convert_results_format(out_path/"results", settings_path, out_path, [vis_model])

    # Check if files already exist and skip if they do because it takes a long time
    txt_out_path = out_path/"extracted_text"
    for ftk in N_FRAMES_TO_KEEP:
        if not (txt_out_path/f"text_{ftk}").exists():
            get_all_texts(vid_ds, txt_out_path, fps = ftk)

    txt_path = art_path/"models"/"OCR+IR"
    subprocess.check_output(
        ["sh", "build_run.sh", str(txt_out_path), str(settings_path)],
        cwd=str(txt_path),
    )

# Cell
@call_parse
def reproduce(
    down_path: Param("The directory where all the files will be downloaded and extracted to.", str),
    out_path: Param("The output path to place all results in.", str),
    vis_model: Param("The type of visual model. Can be either SimCLR or SIFT, taking ~6h or >24h, respectively, for all apps on our machine with 755G of RAM and 72 CPUs.", str)
):
    """Function for reproducing all results related to this tool's paper"""
    random.seed(42)
    download(down_path)
    down_path = Path(down_path)
    out_path = Path(out_path)
    art_path = down_path/"tango_reproduction_package"/"artifacts"

    logging.info("Loading videos.")
    vid_ds = VideoDataset.from_path(
        art_path/"videos", fr = FPS
    ).label_from_paths()

    _generate_vis_results(vid_ds, out_path, art_path, vis_model)
    _generate_txt_results(out_path, art_path, vis_model)

    combo_out_path = out_path/"combined"
    dl_ranking_path = out_path/"user_rankings_weighted_all"/"all_rankings.csv"
    ir_rankings_path = txt_path/"tango_txt_rankings"/"all_rankings.json"

    tango_combined(combo_out_path, dl_ranking_path, ir_rankings_path, settings_path, BEST_DL_MODELS, BEST_IR_MODELS)
    pass

# Cell
@call_parse
def tango(
    q_path:Param("Path to the query video", str),
    cor_path:Param("Path to the corpus", str),
    cb_path:Param("Path to the codebook", str),
    vis_path:Param("Path to SimCLR checkpoint", str),
    fps:Param("FPS to set the vidoes to", int) = 30,
    approach:Param("Approach to use: vis, txt, comb", str) = 'vis'
):
    q_path = Path(q_path)
    cor_path = Path(cor_path)
    cb_path = Path(cb_path)
    vis_path = Path(vis_path)

    q_vid = Video(q_path, fps)
    codebook = pickle.load(open(cb_path, 'rb'))
    simclr = SimCLRModel.load_from_checkpoint(checkpoint_path = str(vis_path)).eval()
    model = SimCLRExtractor(simclr)

    vid_ds = VideoDataset.from_path(cor_path).label_from_paths()
    sorted_rankings = compute_sims(q_vid, vid_ds, model, codebook, 1_000, fps, 5)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(sorted_rankings)
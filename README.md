# Tango 🕺💃
> Tango is a research tool for automatically detecting duplicate video-based bug reports by combining visual and textual information present in the videos.


[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4453765.svg)](https://doi.org/10.5281/zenodo.4453765)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/two-to-tango)](https://pypi.org/project/two-to-tango/)
[![PyPI Status](https://badge.fury.io/py/two-to-tango.svg)](https://badge.fury.io/py/two-to-tango)
[![PyPI Status](https://pepy.tech/badge/two-to-tango)](https://pepy.tech/project/two-to-tango)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ncoop57/tango/blob/main/LICENSE)

## Data



We provide all of our data, models, and results. You can download the zip here: https://doi.org/10.5281/zenodo.4439661

In this data package, you will find two folders: `artifacts` and `outputs`

`artifacts` contains the videos we collected in our user study, the model files for the different models we evaluated, and the detailed results that we generated (See `Detailed Results` section for more information). The `videos` folder is broken down by user, where each user has a folder contain the apps they were given to create videos for. Each of the apps contain folders that denote the bug they generated a report for. Finally, instead these bug folders there is the actual video-based bug report as an mp4 file. The `user_assignment.csv` just contains the finalized assignments of users to corresponding bug reports.

In the `models` folder, you will find the two models we evaluated (SIFT, SimCLR, and OCR+IR). In each folder you will find the corresponding trained codebook files that we generated for SIFT and SimCLR. These codebook files are pickle files that contain the binary representation of the trained codebooks. Additionally, in the SimCLR folder, you will find a checkpoint and pytorch model file that contains all the necessary information for reloading our trained SimCLR model. For the `OCR+IR` folder, you will find all of the code for the OCR+IR model as well as the intermediate output for this particular model, other models' outputs are stored in the `outputs` folder.

The `outputs` folder contains all of the intermediate outputs of our code, except for OCR+IR. In the `results` folder, you will find all of the raw rankings and metrics for the SIFT and SimCLR model for all combinations of video-based bug reports per app. **NOTE: SIFT is missing the 10k raw ranking and metrics, but will be provided in a future version.** `evaluation_setting` contains a json file that contains all of the duplicate detection tasks we used for evaluating our models, i.e. `setting 2` (See paper for more details). `user_rankings_weighted_all` and `user_results_weighted_all` contain converted version of the raw rankings and metrics for the SIFT and SimCLR model to match `setting 2`. `extracted_text` contains the output of running the OCR model, i.e. the frames of the videos and the text from each frame. Lastly, `combined` contains the results of the combined tango approach.

## Reproduce Results
The prefered method to reproduce our paper's results is to use Docker. Please install [Docker](https://docs.docker.com/get-docker/) if you do not already have it install.

```bash
git clone https://github.com/ncoop57/tango.git
cd tango
```

**Reproduce via Docker:**
```bash
cd docker_build
docker build -f Dockerfile.prod -t tango .
cd ..
docker run -v <out_path>:/data tango <vis_model>
```
* **out_path**: The absolute path on your machine you want all files to be saved to
* **vis_model**: The type of visual model. Can be either SimCLR or SIFT, taking ~6 hours or >2 weeks, respectively, for all apps on our machine with 755G of RAM and 72 CPUs.

**Reproduce without Docker:**
```bash
pip install two-to-tango
tango_reproduce <down_path> <out_path> <vis_model>
```
* **down_path**: The directory where all the files will be downloaded and extracted to.
* **out_path**: The output path to place all results in.
* **vis_model**: The type of visual model. Can be either SimCLR or SIFT, taking ~6 hours or >2 weeks, respectively, for all apps on our machine with 755G of RAM and 72 CPUs.

## Detailed Results

You can find a spreadsheet containing the results for all of the different configurations we tested at `tango_reproduction_package/artifacts/detailed_results.xlsx`.

In this excel file, we have multiple sheets. `overall` shows the performance of the different model configurations averaged across all apps. `overall_comb` shows the combined performance of the visual and textual model configurations averaged across all apps. Additionally, `per-app` and `per-app-comb` has the performance of the single and combined model configurations per app, respectively. Lastly, we provide the overall performance in sheet `overall_user_study` and `overall_user_study_comb` of the single and combined model configurations on the settings (used only APOD app) given to the users for evaluating how much time and effort tango can save developers.

All sheets show the performance in terms of mRR (`avg_rr`), the standard deviation of recipical rank, median (`med_rr`), and quartile 1 and 3 (`q#_rr`). The same is true for mAP (`avg_ap`). We also show the performance in terms of average rank including standard deviation, and quartiles. Lastly, we providing HIT@1-5, 7, and 10 (`h#`).

Sheets that contain the `weight` column have information regarding how much weight is given to the visual and textual information. A value of `0.1` means that the textual information received a weight of `0.1` while the visual information was given a weight of `0.9`. For values containing two numbers, e.g. `0.1-0.0`, refers to the weighting scheme introduced in the paper for when there may be high overlap in vocabulary between duplicate and non-duplicates (See paper for more details). If an app does not have high overlap, then a weight of `0.1` is used for the textual information, else the textual information is not considered, i.e., weight of `0.0`.

## Install

**From pypi:**

`pip install two-to-tango`

**From source:**
```bash
git clone https://github.com/ncoop57/tango.git
cd tango
pip install .
```

## How to use

**Download Data CLI Tool**

`tango_download <out_path>`
* **out_path**: The output path to save and unzip all files.

**Duplicate Detection CLI Tool**

`tango <query_path> <corpus_path> <simclr_path>`
* **query_path**: The path to a video you want to detect duplicates for.
 * Example: `<out_path>/tango_reproduction_package/artifacts/cli_videos/U1/APOD/CC1/APOD-CC1_fixed_30.mp4`
* **corpus_path**: The path to a video you want to detect duplicates for.
 * Example: `<out_path>/tango_reproduction_package/artifacts/cli_videos`
* **simclr_path**: The path to a video you want to detect duplicates for.
 * Example: `<out_path>/tango_reproduction_package/artifacts/models/SimCLR`

Example Output:
```python
OrderedDict([   (('APOD', 'CC1', 'U1'), 0.9838350837260246),
                (('APOD', 'CC1', 'U12'), 0.9193482983504456),
                (('APOD', 'CC1', 'U2'), 0.3723964243572911),
                (('APOD', 'CC6', 'U12'), 0.3718521026630344),
                (('APOD', 'CC9', 'U12'), 0.36803837161265085),
                (('APOD', 'CC6', 'U8'), 0.33589710905277315),
                (('APOD', 'CC4', 'U12'), 0.3118613303188616),
                (('APOD', 'CC9', 'U5'), 0.2718403622668689),
                (('APOD', 'CC4', 'U7'), 0.25082093055745974),
                (('APOD', 'CC9', 'U9'), 0.22580393621884165),
                (('APOD', 'CC5', 'U12'), 0.1768510685792533),
                (('APOD', 'CC6', 'U7'), 0.1682816804179776),
                (('APOD', 'CC4', 'U8'), 0.13915926428362999),
                (('APOD', 'CC2', 'U2'), 0.1354447367818957),
                (('APOD', 'CC3', 'U2'), 0.12004454785432789),
                (('APOD', 'CC5', 'U7'), 0.11235793525631509),
                (('APOD', 'CC5', 'U8'), 0.10867946897348428),
                (('APOD', 'CC7', 'U8'), 0.09014217805772731),
                (('APOD', 'RB', 'U1'), 0.08324154319710894),
                (('APOD', 'CC8', 'U12'), 0.08179046960502091),
                (('APOD', 'CC8', 'U5'), 0.07290831091450554),
                (('APOD', 'RB', 'U5'), 0.07194441953180176),
                (('APOD', 'CC3', 'U12'), 0.06729098674201965),
                (('APOD', 'CC7', 'U7'), 0.06326635817907807),
                (('APOD', 'CC7', 'U12'), 0.05922061313241868),
                (('APOD', 'CC8', 'U10'), 0.05328420969145727),
                (('APOD', 'CC2', 'U12'), 0.04707548776015297),
                (('APOD', 'CC3', 'U1'), 0.04342630487280919),
                (('APOD', 'CC2', 'U1'), 0.04211602057931267),
                (('APOD', 'RB', 'U12'), 0.029766244020504186)])
```

If you would like to do this on your own data, look at the `tango_reproduction_package/artifacts/cli_videos` directory structure for how you need to formate your data to work with `tango`

## Training SimCLR
For training the SimCLR model we used the [RICO dataset](https://interactionmining.org/rico) and [this](https://github.com/dthiagarajan/simclr_pytorch) repository for training a SimCLR model using Pytorch Lightning

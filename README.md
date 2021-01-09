# Tango
> Tango is a research tool for automatically detecting duplicate video-based bug reports by combining visual and textual information present in the videos.


**Note: We provide all results. However, for the rankings, we provide all of them except for the visual information models, which we only provide the best performing one (SimCLR-bovw-5fps-1,000vw). We will provide the rest of the rankings for the visual information models upon acceptance**

## Data



We provide all of our data, models, and results. You can download the zip here: https://drive.google.com/file/d/1VFxzNXlldGDoCkyNeiLrrHCnAPaqJPpH/view?usp=sharing

In this data package, you will find two folders: `artifacts` and `outputs`

`artifacts` contains the videos we collected in our user study, the model files for the different models we evaluated, and the detailed results that we generated (See `Detailed Results` section for more information). The `videos` folder is broken down by user, where each user has a folder contain the apps they were given to create videos for. Each of the apps contain folders that denote the bug they generated a report for. Finally, instead these bug folders there is the actual video-based bug report as an mp4 file. The `user_assignment.csv` just contains the finalized assignments of users to corresponding bug reports.

In the `models` folder, you will find the two models we evaluated (SIFT, SimCLR, and OCR+IR). In each folder you will find the corresponding trained codebook files that we generated for SIFT and SimCLR. These codebook files are pickle files that contain the binary representation of the trained codebooks. Additionally, in the SimCLR folder, you will find a checkpoint and pytorch model file that contains all the necessary information for reloading our trained SimCLR model. For the `OCR+IR` folder, you will find all of the code for the OCR+IR model as well as the intermediate output for this particular model, other models' outputs are stored in the `outputs` folder.

The `outputs` folder contains all of the intermediate outputs of our code, except for OCR+IR. In the `results` folder, you will find all of the raw rankings and metrics for the SIFT and SimCLR model for all combinations of video-based bug reports per app. `evaluation_setting` contains a json file that contains all of the duplicate detection tasks we used for evaluating our models, i.e. `setting 2` (See paper for more details). `user_rankings_weighted_all` and `user_results_weighted_all` contain converted version of the raw rankings and metrics for the SIFT and SimCLR model to match `setting 2`. `extracted_text` contains the output of running the OCR model, i.e. the frames of the videos and the text from each frame. Lastly, `combined` contains the results of the combined tango approach.

## Reproduce Results
The prefered method to reproduce our paper's results is to use Docker. Please install [Docker](https://docs.docker.com/get-docker/) if you do not already have it install.

Reproduce via Docker:
```bash
docker build -f Dockerfile.prod -t tango .
docker run -d -u $(id -u):$(id -g) -v <out_path>:/data tango <vis_model>
```
* **out_path**: The directory on your machine you want all files to be saved to
* **vis_model**: The type of visual model. Can be either SimCLR or SIFT, taking ~6h or >24h, respectively, for all apps on our machine with 755G of RAM and 72 CPUs.

Reproduce without Docker:
```bash
pip install tango
tango_reproduce <down_path> <out_path> <vis_model>
```
* **down_path**: The directory where all the files will be downloaded and extracted to.
* **out_path**: The output path to place all results in.
* **vis_model**: The type of visual model. Can be either SimCLR or SIFT, taking ~6h or >24h, respectively, for all apps on our machine with 755G of RAM and 72 CPUs.

We have created our reproduction package using Docker. Please install [Docker](https://docs.docker.com/get-docker/) if you do not already have it install.

Steps to Reproduce:
1. Download the repository: `git clone https://github.com/two-to-tango/tango.git`
2. Download the data from our gdrive: https://drive.google.com/file/d/1VFxzNXlldGDoCkyNeiLrrHCnAPaqJPpH/view?usp=sharing
3. Unzip the data file
2. Navigate to the root of the repo and run the start script, passing in the location of the data folder: `./start <data_path>`
3. Once the docker container has finished spinning up, jump into it: `docker exec -it tango bash`
4. Change directory into the main folder (`cd main`) and install tango locally: `pip install -e .`
5. Locate the Jupyter Notebook token by running the following command inside the docker container: `jupyter notebook list`
6. Open a browser to `localhost:8888` and paste the token into the correct field
7. Navigate to `main/nbs/06_results.ipynb` and follow the rest of the instructions provided in that notebook

## Detailed Results

You can find a spreadsheet containing the results for all of the different configurations we tested at `tango_reproduction_package/artifacts/detailed_results.xlsx`.

In this excel file, we have multiple sheets. `overall` shows the performance of the different model configurations averaged across all apps. `overall_comb` shows the combined performance of the visual and textual model configurations averaged across all apps. Additionally, `per-app` and `per-app-comb` has the performance of the single and combined model configurations per app, respectively. Lastly, we provide the overall performance in sheet `overall_user_study` and `overall_user_study_comb` of the single and combined model configurations on the settings (used only APOD app) given to the users for evaluating how much time and effort tango can save developers.

All sheets show the performance in terms of mRR (`avg_rr`), the standard deviation of recipical rank, median (`med_rr`), and quartile 1 and 3 (`q#_rr`). The same is true for mAP (`avg_ap`). We also show the performance in terms of average rank including standard deviation, and quartiles. Lastly, we providing HIT@1-5, 7, and 10 (`h#`).

Sheets that contain the `weight` column have information regarding how much weight is given to the visual and textual information. A value of `0.1` means that the textual information received a weight of `0.1` while the visual information was given a weight of `0.9`. For values containing two numbers, e.g. `0.1-0.0`, refers to the weighting scheme introduced in the paper for when there may be high overlap in vocabulary between duplicate and non-duplicates (See paper for more details). If an app does not have high overlap, then a weight of `0.1` is used for the textual information, else the textual information is not considered, i.e., weight of `0.0`.

## Install

#### From pypi:

`pip install tango`

#### From source:
```bash
git clone https://github.com/ncoop57/tango.git
cd tango
pip install .
```

## How to use

`tango <query_vid_path> <corpus_path> <codebook_path> <simclr_checkpoint_path>`

Example Output:
```
OrderedDict([   (('APOD', 'CC1', 'U2'), 1.0),
                (('APOD', 'CC1', 'U1'), 0.7101319783997799),
                (('APOD', 'CC3', 'U2'), 0.19613202363022775),
                (('APOD', 'RB', 'U1'), 0.1261138231868554),
                (('APOD', 'CC2', 'U2'), 0.11940588516361622),
                (('APOD', 'CC3', 'U1'), 0.07206934454930929),
                (('APOD', 'CC2', 'U1'), 0.03426603336985401)])
```

#### Download our dataset and artifacts:

`tango_download <out_path>`
* **out_path**: The output path to save and unzip all files.

## Training SimCLR
For training the SimCLR model we used the [RICO dataset](https://interactionmining.org/rico) and [this](https://github.com/dthiagarajan/simclr_pytorch) repository for training a SimCLR model using Pytorch Lightning

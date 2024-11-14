# Generation

This folder contains scripts and utilities for generating and evaluating data related to the project. The scripts are designed to handle various tasks such as data generation, inference, and evaluation of model outputs.

## Folder Structure

- `DSA3101_datagen.py`: Script for generating data based on predefined prompts and scenarios.
- `DSA3101_inference_model.py`: Script for running inference on generated data and evaluating the results.
- `DSA3101_batchmarker.py`: Script for evaluating pairs of ground truth and prediction files across folders.
- `DSA3101_marker.py`: Contains classes and functions for evaluating named entity recognition (NER) and relationships.
- `prediction_triplet.py`: Script for converting prediction JSON files into triplet format for further analysis.

## Scripts

### DSA3101_datagen.py

This script generates data based on predefined prompts and scenarios. It uses asynchronous calls to generate multiple queries concurrently.

#### Usage
```sh
python DSA3101_datagen.py 
```
### DSA3101_inference_model.py
This script runs inference on the generated data and evaluates the results. It uses a language model to generate responses and extracts JSON from the responses.

#### Usage
```sh
python DSA3101_inference_model.py
```
### DSA3101_batchmarker.py
This script evaluates pairs of ground truth and prediction files across two folders, averaging metrics across all pairs.

#### Usage
```sh
python DSA3101_batchmarker.py
```

### Requirements
Make sure to install the required Python packages before running the scripts:
```sh
pip install -r requirements.txt
```




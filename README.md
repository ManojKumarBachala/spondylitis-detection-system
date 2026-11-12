# AI-Based Detection and Classification of Spondylitis Using Deep Neural Networks

An M.Tech research prototype that uses a convolutional neural network (CNN) to
classify spine X-ray images as Normal or Spondylitis.

> **Research demo only.** This model is not clinically validated and must not be
> used to diagnose, treat, or rule out a medical condition. Consult a qualified
> clinician for medical advice. Do not upload identifiable or real patient
> records.

## Run locally

Use Python 3.12. From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py runserver
```

Open <http://127.0.0.1:8000>. Image uploads are decoded and processed in memory;
the application does not save them. The repository intentionally excludes the
original X-ray dataset, test images, local databases, and virtual environments.

## Model and dataset

The pre-trained model used by the demo is `model/cnn_weights.hdf5`. The original
dataset is not redistributed here. Its source is
[The Vertebrae X-ray Images on Kaggle](https://www.kaggle.com/datasets/yasserhessein/the-vertebrae-xray-images);
review that dataset's terms before downloading or using it.

## Deploy on Render

This repository includes a Render Blueprint in `render.yaml`. Use
[Deploy to Render](https://render.com/deploy?repo=https://github.com/ManojKumarBachala/spondylitis-detection-system)
and connect the GitHub repository. The Blueprint generates a Django secret key
and deploys a single Django web service; no database or user accounts are
required.

The free Render instance can sleep when idle and has limited memory. TensorFlow
model loading may exceed free-tier resources; if Render reports an out-of-memory
failure, use a larger instance only after reviewing its current price.

## Privacy

- Uploaded images are limited to 8 MiB and processed in memory.
- The application does not retain uploaded images or collect account details.
- Raw X-ray datasets, sample uploads, credentials, local databases, and
  environment files are excluded from Git.

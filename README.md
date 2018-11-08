[![Build Status](https://travis-ci.org/CODAIT/max-workshop-app-python.svg?branch=master)](https://travis-ci.org/CODAIT/max-workshop-app-python)

# MAX Object Detector Web App (Lite) - Python

A simplified python version of the [MAX Object Detector Web App](https://github.com/IBM/MAX-Object-Detector-Web-App) for use in MAX workshops.

This repository's default branch, `initial`, contains **TODOs** meant to be completed while following the
[MAX Developer Tutorial](https://github.com/CODAIT/max-developer-tutorial).
A working version of the app without the **TODOs** can be found on the `solution` branch.

> This is the python version of this Web App, you can also check out the [NodeJS version](https://github.com/CODAIT/max-workshop-app-nodejs)

# Steps

## Run Locally

**Start the Model API**

1. [Deploy the Model](#1-deploy-the-model)
2. [Experiment with the API (Optional)](#2-experiment-with-the-api-optional)

**Start the Web App**

1. [Get a local copy of the repository](#1-get-a-local-copy-of-the-repository)
2. [Install dependencies](#2-install-dependencies)
3. [Start the web app server](#3-start-the-web-app-server)
4. [Configure ports (Optional)](#4-configure-ports-optional)
5. [Try out the full version (Optional)](#5-try-out-the-full-version-optional)

### Start the Model API

> NOTE: The set of instructions in this section are a modified version of the ones found on the
[Object Detector Project Page](https://github.com/IBM/MAX-Object-Detector)

#### 1. Deploy the Model

To run the docker image, which automatically starts the model serving API, run:

```
$ docker run -it -p 5000:5000 codait/max-object-detector
```

This will pull a pre-built image from Docker Hub (or use an existing image if already cached locally) and run it.
If you'd rather build and run the model locally, or deploy on a Kubernetes cluster, you can follow the steps in the
[model README](https://github.com/IBM/MAX-Object-Detector/#steps).

#### 2. Experiment with the API (Optional)

The API server automatically generates an interactive Swagger documentation page.
Go to `http://localhost:5000` to load it. From there you can explore the API and also create test requests.

Use the `model/predict` endpoint to load a test image and get predicted labels for the image from the API.
The coordinates of the bounding box are returned in the `detection_box` field, and contain the array of normalized
coordinates (ranging from 0 to 1) in the form `[ymin, xmin, ymax, xmax]`.

The [model assets folder](https://github.com/IBM/MAX-Object-Detector/tree/master/assets)
contains a few images you can use to test out the API, or you can use your own.

You can also test it on the command line, for example:

```
$ curl -F "image=@assets/dog-human.jpg" -XPOST http://localhost:5000/model/predict
```

You should see a JSON response like that below:

```json
{
  "status": "ok",
  "predictions": [
      {
          "label_id": "1",
          "label": "person",
          "probability": 0.944034993648529,
          "detection_box": [
              0.1242099404335022,
              0.12507188320159912,
              0.8423267006874084,
              0.5974075794219971
          ]
      },
      {
          "label_id": "18",
          "label": "dog",
          "probability": 0.8645511865615845,
          "detection_box": [
              0.10447660088539124,
              0.17799153923988342,
              0.8422801494598389,
              0.732001781463623
          ]
      }
  ]
}
```

You can also control the probability threshold for what objects are returned using the `threshold` argument like below:

```
$ curl -F "image=@assets/dog-human.jpg" -XPOST http://localhost:5000/model/predict?threshold=0.5
```

The optional `threshold` parameter is the minimum `probability` value for predicted labels returned by the model.
The default value for `threshold` is `0.7`.

### Start the Web App

#### 1. Get a local copy of the repository

Clone the web app repository locally. In a terminal, run the following command:

```
$ git clone https://github.com/CODAIT/max-workshop-app-python.git
```

Change directory into the repository base folder:

```
$ cd max-workshop-app-python
```

#### 2. Install dependencies

Before running this web app you must install its dependencies:

```
$ pip install -r requirements.txt
```

#### 3. Start the web app server

You then start the web app by running:

```
$ python app.py
```

You can then access the web app at: [`http://localhost:8090`](http://localhost:8090)

#### 4. Configure ports (Optional)

If you want to use a different port or are running the model API at a different location you can change them with command-line options:

```
$ python app.py --port=[new port] --model=[endpoint url including protocol and port]
```

#### 5. Try out the full version (Optional)

The latest release of the full web app is deployed with the model API above and is available at [`http://localhost:5000/app`](http://localhost:5000/app).

The full version includes more features like filtering the detected objects based on their labels or a threshold for the prediction accuracy.

> NOTE: The full version is written in NodeJS not Python and will have slight differences in the UI

# Links

* [MAX Object Detector Web App](https://github.com/IBM/MAX-Object-Detector-Web-App)
* [Model Asset eXchange (MAX)](https://developer.ibm.com/code/exchanges/models/)
* [Center for Open-Source Data & AI Technologies (CODAIT)](https://developer.ibm.com/code/open/centers/codait/)

# License
[Apache 2.0](LICENSE)


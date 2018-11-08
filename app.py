#
# Copyright 2018 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from flask import Flask, render_template, request
import argparse
import requests
import cv2
import logging
import numpy as np
import os
import glob
from pprint import pformat
from random import randint

# setup logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# parse port and model endpoint args
parser = argparse.ArgumentParser(description='MAX Object Detector (Lite)')
parser.add_argument('--port', type=int, nargs='?', default=8090,
                    help='port to run the web app on')
parser.add_argument('--ml-endpoint', nargs='?', metavar='URL',
                    default='http://localhost:5000', help='model api server')
args = parser.parse_args()

app = Flask(__name__)


def image_resize(img_array):
    """Resize the image before processing. This is required for consistency
    since the bounding box and label are drawn relative to the image size."""
    height, width, _ = np.shape(img_array)
    img_resize = cv2.resize(img_array, (1024, int(1024 * height / width)))
    img_height, img_width, _ = np.shape(img_resize)
    return img_resize, img_height, img_width


def draw_label_box(prediction, image, img_width, img_height):
    """Draw the given label and bounding box on the given image"""
    label = prediction['label']
    ymin, xmin, ymax, xmax = prediction['detection_box']
    (left, right, top, bottom) = (int(xmin * img_width),
                                  int(xmax * img_width),
                                  int(ymin * img_height),
                                  int(ymax * img_height))

    font = cv2.FONT_HERSHEY_DUPLEX
    text_width, text_height = cv2.getTextSize(label, font, 0.8, 1)[0]

    cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
    cv2.rectangle(image, (left, top),
                  (left + text_width, top + int(text_height * 1.4)),
                  (0, 255, 0), -1)
    cv2.putText(image, label, (left, top + text_height),
                font, 0.8, (0, 0, 0), 1)


@app.route('/', methods=['POST', 'GET'])
def root():

    # removing all previous files in folder before start processing
    output_folder = 'static/img/temp/'
    for file in glob.glob(output_folder + '*'):
        os.remove(file)

    # on POST handle upload
    if request.method == 'POST':

        # get file details
        file_data = request.files.get('file')
        if file_data is None:
            err_msg = 'No input image was provided.'
            logging.error(err_msg)
            return render_template('index.html', error_msg=err_msg)

        # read image from string data
        file_request = file_data.read()
        # convert string data to numpy array
        np_inp_image = np.fromstring(file_request, np.uint8)
        # convert numpy array to image
        img = cv2.imdecode(np_inp_image, cv2.IMREAD_UNCHANGED)
        try:
            # resize image to consistent size
            (image_processed,
             img_processed_height,
             img_processed_width) = image_resize(img)
        except Exception:
            err_msg = 'Error processing image, try uploading a different image'
            logging.error(err_msg)
            return render_template('index.html', error_msg=err_msg)

        # encode image
        _, image_encoded = cv2.imencode('.jpg', img)

        # Required inference request parameter: image (JPG/PNG encoded)
        files = {
            'image': image_encoded.tostring(),
            'Content-Type': 'multipart/form-data',
        }

        # Optional inference parameter: threshold (default: 0.7, range [0,1])
        data = {'threshold': '0.5'}

        model_url = args.ml_endpoint.rstrip('/') + '/model/predict'

        # Send image file form to model endpoint for prediction
        try:
            results = requests.post(url=model_url, files=files, data=data)
        except Exception as e:
            err_msg_temp = 'Prediction request to {} failed: {}'
            err_msg = err_msg_temp.format(model_url, 'Check log for details.')
            logging.error(err_msg_temp.format(model_url, str(e)))
            return render_template("index.html", error_msg=err_msg)

        # surface any prediction errors to user
        if results.status_code != 200:
            err_msg = ('Prediction request returned status code {} '
                       + 'and message {}').format(results.status_code,
                                                  results.text)
            logging.error(err_msg)
            return render_template('index.html', error_msg=err_msg)

        # extract prediction from json return
        output_data = results.json()

        # log output in debug
        logging.debug('\n' + pformat(output_data))

        result = output_data['predictions']

        if len(result) == 0:
            msg = 'No objects detected, try uploading a new image'
            return render_template('index.html', error_msg=msg)
        else:
            # draw the labels and bounding boxes on the image
            for i in range(len(result)):
                draw_label_box(result[i], image_processed,
                               img_processed_width, img_processed_height)

            # save the output image to return
            file_name = (str(randint(0, 999999)) + '.jpg')
            output_name = output_folder + '/' + file_name
            cv2.imwrite(output_name, image_processed)

        return render_template('index.html', image_name=output_name)

    else:
        # on GET return index.html
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=args.port)

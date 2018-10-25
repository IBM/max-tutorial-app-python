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
import numpy as np
import os
import glob
from random import randint

# parse port and model endpoint args
parser = argparse.ArgumentParser(description='MAX Object Detector (Lite)')
parser.add_argument('--port', type=int, nargs='?', default=8090,
                    help='port to run the web app on')
parser.add_argument('--ml-endpoint', nargs='?', metavar='URL',
                    default='http://localhost:5000', help='model api server')
args = parser.parse_args()

app = Flask(__name__)


def image_resize(img_array):
    """Resize the image for processing"""
    height, width, _ = np.shape(img_array)
    img_resize = cv2.resize(img_array, (1024, int(1024 * height / width)))
    img_height, img_width, _ = np.shape(img_resize)
    return img_resize, img_height, img_width


@app.route('/', methods=['POST', 'GET'])
def root():

    # removing all previous files in folder before start processing
    output_folder = 'static/img/temp/'
    for file in glob.glob(output_folder + '*'):
        os.remove(file)

    # on POST handle upload
    if request.method == 'POST':

        # get file details
        file_data = request.files['file']
        # file_name = file_data.filename
        # read images from string data
        file_request = file_data.read()
        # convert string data to numpy array
        np_inp_image = np.fromstring(file_request, np.uint8)
        # convert numpy array to image
        img = cv2.imdecode(np_inp_image, cv2.IMREAD_UNCHANGED)
        (image_processed,
         img_processed_height,
         img_processed_width) = image_resize(img)
        # encode image
        _, image_encoded = cv2.imencode('.jpg', img)
        # send this as an input for prediction
        my_files = {
            'image': image_encoded.tostring(),
            'Content-Type': 'multipart/form-data',
            'accept': 'application/json'
        }

        model = args.ml_endpoint.rstrip('/') + '/model/predict?threshold=0.5'
        results = requests.post(url=model, files=my_files)

        # extract prediction from json return
        output_data = results.json()
        result = output_data['predictions']

        if len(result) <= 0:
            msg = "No objects detected, try uploading a new image"
            return render_template("index.html", error_msg=msg)
        else:
            # draw the labels and bounding boxes on the image
            for i in range(len(result)):
                label = result[i]['label']
                ymin, xmin, ymax, xmax = result[i]['detection_box']
                (left, right, top, bottom) = (int(xmin * img_processed_width),
                                              int(xmax * img_processed_width),
                                              int(ymin * img_processed_height),
                                              int(ymax * img_processed_height))

                font = cv2.FONT_HERSHEY_DUPLEX
                txt_width, txt_height = cv2.getTextSize(label, font, 0.8, 1)[0]

                cv2.rectangle(image_processed, (left, top),
                              (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(image_processed, (left, top),
                              (left + txt_width, top + int(txt_height * 1.4)),
                              (0, 255, 0), -1)
                cv2.putText(image_processed, label, (left, top + txt_height),
                            font, 0.8, (0, 0, 0), 1)

            # save the output image to return
            file_name = (str(randint(0, 999999)) + '.jpg')
            output_name = output_folder + '/' + file_name
            cv2.imwrite(output_name, image_processed)

        return render_template("index.html", image_name=output_name)
                             
    else:
        # on GET return index.html
        return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=args.port)
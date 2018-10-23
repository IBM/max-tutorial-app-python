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
import requests
import cv2
import numpy as np
import os
import glob
from random import randint

app = Flask(__name__)



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
        img_processed_height, img_processed_width, _ = np.shape(img)
        # encode image
        _, image_encoded = cv2.imencode('.jpg', img)
        # send this as an input for prediction
        my_files = {
            'image': image_encoded.tostring(),
            'Content-Type': 'multipart/form-data',
            'accept': 'application/json'
        }

        result_age = requests.post('http://localhost:5000/model/predict',
                                   files=my_files, json={"key": "value"})

        # extracting prediction
        output_data = result_age.json()
        result = output_data['predictions']

        label_confidence = []

        if len(result) <= 0:
            msg = "No object detected, try uploading a new image"
            return render_template("index.html", error_msg=msg)
        else:
            for i in range(len(result)):
                #
                label_id = str(result[i]['label_id'])
                label = result[i]['label']
                probability = result[i]['probability']
                prob_percent = ("%.2f%%" % (100 * probability))
                bounding_box = result[i]['detection_box']
                #
                ymin, xmin, ymax, xmax = bounding_box
                (left, right, top, bottom) = (xmin * img_processed_width, xmax * img_processed_width,
                              ymin * img_processed_height, ymax * img_processed_height)
                
                #
                font = font=cv2.FONT_HERSHEY_SIMPLEX
                cv2.rectangle(img, (int(left),int(top)), (int(right) ,int(bottom)),(0, 255, 0), 2)
                cv2.putText(img, label, (int(left - 5), int(top - 5)), font,1,(255, 255, 255),2)
                cv2.putText(img, label, (int(left - 5), int(top - 5)), font,1,(0, 0, 0),1)
                
                #
                detection_info = label_id + ' - ' + label + ' - ' + prob_percent
                label_confidence.append(detection_info)
                
            #output
            file_name = (str(randint(0, 999999)) + '.jpg') 
            output_name = output_folder + '/' + file_name
            cv2.imwrite(output_name, img)

        return render_template("index.html", image_name=output_name,result= label_confidence)
                             
    else:
        # on GET return index.html
        return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, port=8000)

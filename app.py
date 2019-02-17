import os
import sys
import time

from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2
from flask import Flask, jsonify, request, flash, redirect
from flask_cors import CORS
from werkzeug import secure_filename

import config

UPLOAD_FOLDER = 'campnav-pics'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in set(["png", "jpg", "jpeg"])


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/api', methods=["POST"])
def root():
    if 'photo' not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files['photo']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as target:
        content = target.read()
    response = get_prediction(content)
    name = "None"
    score = 0
    if response is not None:
        for result in response.payload:
            name = result.display_name
            score = result.classification.score
    return jsonify(name=name, score=score)


def get_prediction(content, project_id='campnav-ml', model_id='ICN6519510554659396321'):
    automl_v1beta1.AutoMlClient.from_service_account_json(
        'campnav-ml-04191219f11a.json')
    prediction_client = automl_v1beta1.PredictionServiceClient()
    name = 'projects/{}/locations/us-central1/models/{}'.format(
        project_id, model_id)
    payload = {'image': {'image_bytes': content}}
    params = {}
    request = prediction_client.predict(name, payload, params)
    return request


if __name__ == '__main__':
    # app.debug = True
    app.secret_key = 'hackcewit2019'
    app.cors_headers = 'Content-Type'
    app.run(host='0.0.0.0')

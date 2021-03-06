import base64
from io import BytesIO
from GeneraterImage import GenerateImage
from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
from PIL import Image
import pandas as pd
import tensorflow as tf
import keras
from keras.models import load_model

# configuration
DEBUG = True
PRODUCTION = False

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app)

# to use it when loading the model
def auc(y_true, y_pred):
	auc = tf.metrics.auc(y_true, y_pred)[1]
	keras.backend.get_session().run(tf.local_variables_initializer())
	return auc

# load the model, and pass in the custom metric function
global graph, model
graph = tf.get_default_graph()
model = load_model('model.h5', custom_objects={'auc': auc})

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/api', methods=['GET', 'POST'])
def api_version():
	return jsonify(name="SawandeeTukwan",
				   version="1.0.0")

@app.route('/api/randomImage', methods=['GET'])
def randomImage():
	size = request.args.get('size')
	encode = request.args.get('encode') if request.args.get('encode') else 'jpeg'
	url = "https://loremflickr.com/%s/%s/flower" % (size, size)
	image_obj = GenerateImage(url, size)
	image_obj.addText()
	image_de = serveImage(image_obj.img, encode)
	return jsonify(base64=base64.b64encode(image_de).decode('utf-8'),
				   type=encode,
				   size=[size, size])

@app.route('/api/customImage', methods=['GET'])
def customImage():
	msg = request.args.get('msg')
	size = request.args.get('size')
	encode = request.args.get('encode') if request.args.get('encode') else 'jpeg'
	url = "https://loremflickr.com/%s/%s/flower" % (size, size)
	image_obj = GenerateImage(url, size)
	image_obj.addText(msg)
	image_de = serveImage(image_obj.img, encode)
	return jsonify(base64=base64.b64encode(image_de).decode('utf-8'),
				   type=encode,
				   size=[size, size])

@app.route("/predict", methods=["GET","POST"])
def predict():
	size = request.args.get('size')
	label_arr = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
	img = GenerateImage("https://loremflickr.com/%s/%s/flower" % (size, size), size)
	img = np.array(img).reshape(-1, 500, 500, 3)
	result = model.predict(img.reshape(-1, 500, 500, 3))
	result_class = label_arr[np.argmax(result)]

def serveImage(image, encode):
    img_io = BytesIO()
    image.save(img_io, encode)
    img_io.seek(0)
    return img_io.getvalue()

if __name__ == '__main__':
    app.run()

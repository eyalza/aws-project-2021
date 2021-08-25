#!flask/bin/python
import json
from flask import Flask, Response, request
from helloworld.flaskrun import flaskrun
from flask_cors import CORS
import requests
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
import simplejson as json
import uuid



application = Flask(__name__)

CORS(application, resources={r"/*": {"origins": "*"}}) 

@application.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

@application.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)
    





# DYNAMODB - READ ORDERS
# curl -i -X POST -H "Content-Type: application/json" -d '{"uid": "1"}' http://localhost:8000/get_orders

@application.route('/get_orders', methods=['POST'])
def get_orders():
    data = request.get_json()
    uid = data['uid']    
    print(uid)
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('orders')
    response = table.scan(FilterExpression = Attr('uid').eq(uid))
    orders = response['Items']

    return Response(json.dumps(orders), mimetype='application/json', status=200)


# DYNAMODB - ADD ORDER
# curl -i -X POST -H "Content-Type: application/json" -d '{"uid": "1"}' http://localhost:8000/add_order

@application.route('/add_order', methods=['POST'])
def add_order():
    data = request.get_json()
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('orders')
    order_id = (str(uuid.uuid4()))
    data['order_id'] = order_id
    print(order_id)
    table.put_item(Item=data)
    
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)


# DYNAMODB - DELETE ORDER
# curl -i -X POST -H "Content-Type: application/json" -d '{"order_id": "c011f8a5-9ea8-4733-b44e-498cae9c5a00"}' http://localhost:8000/delete_order

@application.route('/delete_order', methods=['POST'])
def delete_order():
    data = request.get_json()
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('orders')
    order_id = data['order_id']

    response = table.delete_item(
        Key={
            'order_id': order_id,
        }
    )

    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

# DYNAMODB - EDIT ORDER
# curl -i -X POST -H "Content-Type: application/json" -d '{"order_id": "05957e8c-d4b4-45e8-bb9c-99eb04a6695sa", "uid": 5}' http://localhost:8000/edit_order
@application.route('/edit_order', methods=['POST'])
def edit_order():
    data = request.get_json()
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('orders')
    table.put_item(Item=data)
    
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)


# S3 - UPLOAD IMAGE
@application.route('/upload_image', methods=['POST'])
def upload_image():
    bucket = 'jce-aws-project-images'
    image_car = request.files['image_car']
    s3 = boto3.resource('s3', region_name='us-east-1')
    path  = "%s.jpg" %  (str(uuid.uuid4()))
    
    s3.Bucket(bucket).upload_fileobj(image_car, path, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'}) 
    img_url = 'https://jce-aws-project-images.s3.amazonaws.com/'+ path
    
    return {"img_url": img_url}
 
 
 
 # REKOGNITION - 

@application.route('/analyze_image', methods=['POST'])
def analyze_image():
    data = request.get_json()
    image_url = data['image_url']
    key = image_url.replace("https://jce-aws-project-images.s3.amazonaws.com/", "")

    bucket = 'jce-aws-project-images'
    s3 = boto3.resource('s3', region_name = 'us-east-1')
    image = s3.Object(bucket, key) # Get an Image from S3
    img_data = image.get()['Body'].read() # Read the image

    rekognition = boto3.client("rekognition", region_name = 'us-east-1')
    
    response = rekognition.detect_text(Image={'Bytes':img_data})
    detected_text = response['TextDetections'][0]['DetectedText']
    confidence = response['TextDetections'][0]['Confidence']

    print(detected_text)
    print(confidence)


    return json.dumps({"detected_text": detected_text, "confidence": confidence})


   
if __name__ == '__main__':
    flaskrun(application)


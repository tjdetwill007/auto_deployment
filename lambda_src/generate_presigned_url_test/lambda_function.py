import boto3
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_cors import CORS
import urllib.parse
app = Flask(__name__)
CORS(app)

@app.route('/get_pre=<filename>',methods=['GET'])
def lambda_handler(filename):
    filename=filename
    print(filename)
    client = boto3.client('s3')
    response = client.generate_presigned_url(ClientMethod='put_object', Params={'Bucket': 'testbucket1sept2023', 'Key': filename, 'ContentType':"application/x-zip-compressed"}, ExpiresIn=3600)
    print(response)
    return {"statusCode":200,"body":response}
if __name__ == '__main__':
    app.run(debug=True)

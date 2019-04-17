# Importing Libraries
from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)

def URL():
    return "192.168.111.143"


def URL_API():
    return "http://192.168.111.143:5001"


# Default Route to Web page of the UI
@app.route('/index.html')
def my_form():
    return render_template('/var/www/html/index.html')

# POST request
@app.route('/', methods=['POST'])
def test():
    # check if request is an POST
    if request.method == 'POST':
        zoekopdracht = request.form['search1']
        f = os.popen("hdfs dfs -cat output1/part-r-00000 | grep " + zoekopdracht)
        now = f.read()
    return now

# IP of the host the Logger runs on(Change IP to the IP of your VM), app runs in Debug Mode
# Don't forget to also change the IP in index.html
if __name__ == '__main__':
    app.run(host=URL(), port=5000, debug=True)


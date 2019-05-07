# Importing Libraries
from flask import Flask, request, render_template
import requests
import os
from jinja2 import Template

app = Flask(__name__, template_folder='/var/www/html/templates')

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
        zoekopdracht = request.form['name']
        if os.geteuid() == 0:
            f = os.popen("runuser -l  hadoop -c 'hdfs dfs -cat output4/part-00000 | grep '" + zoekopdracht)

        else:
            f = os.popen('hdfs dfs -cat output4/part-00000 | grep ' + zoekopdracht)
        fnames = f.read()
        fnames = fnames.replace('[', '')
        fnames = fnames.replace(']', '')
        fnames = fnames.replace("'", '')
        aantal = len(fnames.split())
#    return '{}{}'.format(fnames, aantal)
#    return render_template('search.html', len = len(fnames), fnames = fnames)
    return render_template('result.html', aantal=aantal, fnames=fnames)

@app.route('/upload', methods=['POST'])
def upload():
    APP_ROOT = os.path.dirname(os.path/abspath(__file__))
    if request.method == 'POST':
        target = os.path.join(APP_ROOT, 'text/')
        print(target)

        if not os.path.isdir(target):
            os.mkdir(target)

        for file in request.files.getlist('file'):
            print(file)
            filename = file.filename
            destination = (target+filename)
            print(destination)
            destination = destination.replace(" ", '_')
            file.save(destination)
            if os.geteuid() == 0:
                os.popen("runuser -l  hadoop -c 'hdfs dfs -copyFromLocal '"+ destination +"' input/'")
                #os.remove(destination)
            else:
                os.popen('hdfs dfs -copyFromLocal '+ destination +' input/')
                #os.remove(destination)
            
    return render_template ('complete.html')

@app.after_request 
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 
'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 
'GET,PUT,POST,DELETE,OPTIONS')
  return response# IP of the host the Logger runs on(Change IP to the IP of your VM), app runs in Debug Mode

# Don't forget to also change the IP in index.html
if __name__ == '__main__':
    app.run(host=URL(), port=5000, debug=True)

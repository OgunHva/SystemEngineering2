# Importing Libraries
from flask import Flask, request, render_template
import requests
import os
import subprocess
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
        cmd = ["hadoop jar /home/hadoop/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.1.2.jar" + " \-file /home/hadoop/hduser/mapper.py" + " \-mapper 'python3 mapper.py'" + " \-file /home/hadoop/hduser/reducer.py" + " \-reducer 'python3 reducer.py'" + " \-input input/*" + " \-output output" + " \-cmdenv WORD_INPUT=" + zoekopdracht]
        subprocess.call(cmd, shell=True)
        
        if os.geteuid() == 0:
            f = os.popen("runuser -l  hadoop -c 'hdfs dfs -cat output/part-00000 | grep '" + zoekopdracht)

        else:
            f = os.popen('hdfs dfs -cat output/part-00000 | grep ' + zoekopdracht)
        fnames = f.read()
        fnames = fnames.replace('[', '')
        fnames = fnames.replace(']', '')
        fnames = fnames.replace("'", '')
        fnames_split = fnames.split()
        fnames_split.sort()
        aantal = len(fnames.split())
    os.popen("hdfs dfs -rm -r output")
    return render_template('result_search.html', aantal=aantal, fnames_split=fnames_split)

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
    return render_template ('complete_upload.html')

# POST request
@app.route('/dashboard', methods=['POST'])
def dashboard():
    if request.method =='POST':
#        btn_showdata = request.form['data']
        if os.geteuid() == 0:
            s = os.popen("runuser -l hadoop -c 'hdfs dfs -count input'")
        else:
            s = os.popen('hdfs dfs -count input')
        m = s.read()
        aantal_bestanden_list = m.split()
        aantal_bestanden = aantal_bestanden_list[1]
#    return render_template('result_dashboard.html', aantal_bestanden=aantal_bestanden)
    return render_template('result_dashboard.html', aantal_bestanden=aantal_bestanden)
#    return aantal_bestanden

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

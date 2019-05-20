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

def createlist(search_word, the_lines):
    the_list = []
    search = search_word.lower()
    for line in the_lines:
        line = line.replace(":", "")
        index = line.find(search)
        if (index != -1):
            line = str(line).split()
            for x in line[1:]:
                if x not in the_list:
                    the_list.append(x)
    return(the_list)


def createsearch(word):
    word = word.split()
    for x in range(len(word)):
        if x == 0:
            words = word[x]
        elif x % 2 == 0:
            words = words + " " + word[x]
        else:
            words = words + " " + word[x].upper()
    return(words)

# Default Route to Web page of the UI
@app.route('/index.html')
def my_form():
    return render_template('/var/www/html/index.html')

# POST request
@app.route('/', methods=['POST'])
def test():
    # check if request is an POST
    if request.method == 'POST':
        var = 0        
        zoekopdracht = request.form['name']
        zoekopdracht = createsearch(zoekopdracht)
        zoekopdracht = zoekopdracht.split()
        if os.geteuid() == 0:
            f = os.popen("runuser -l  hadoop -c 'hdfs dfs -cat output/part-00000'")

        else:
            f = os.popen('hdfs dfs -cat output/part-00000')

        outputfile = f.readlines()
        for search_word in zoekopdracht:
            if search_word == "AND":
                var = 1
            elif search_word == "OR":
                var = 2
            elif search_word == "NOT":
                var = 3
            else:
                if var == 1:
                    list_and = createlist(search_word, outputfile)
                    list_full = list(set(list_full) & set(list_and))
                elif var == 2:
                    list_or = createlist(search_word, outputfile)
                    list_full = list(set(list_full) - set(list_or))
                    list_full = list_full + list_or
                elif var == 3:
                    list_not = createlist(search_word, outputfile)
                    list_full = list(set(list_full) - set(list_not))
                elif var == 4:
                    list_dif = createlist(search_word, outputfile)
                    list_full = list(set(list_full) ^ set(list_dif))
                else:
                    list_full = createlist(search_word, outputfile)
        print(list_full)
        list_full.sort()
        aantal = len(list_full)
        list_full = str(list_full)
        list_full = list_full.replace('[', '')
        list_full = list_full.replace(']', '')
        list_full = list_full.replace("'", '')
    return render_template('result_search.html', aantal=aantal, fnames_split=list_full)

    
# Upload request
@app.route('/upload', methods=['POST'])
def upload():
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
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
            if os.path.isfile(destination):
                print("File already excists")
                return render_template('complete_upload.html', uitkomst="File already excists")
                continue
            else:
                file.save(destination)
            cmd1 = ["hdfs dfs -copyFromLocal " + destination + " input/"]
            cmd2 = ["hdfs dfs -rm -r output"]
            subprocess.call(cmd1, shell=True)
            try:
                subprocess.call(cmd2, shell=True)
            except:
                print("Output already removed")
        cmd3 = ["hadoop jar /home/hadoop/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.1.2.jar -file /home/hadoop/test/mapperV5.py  -mapper 'python mapperV5.py' -file /home/hadoop/test/reducerV5.py -reducer 'python reducerV5.py' -input input/* -output output/"]
        subprocess.Popen(cmd3, shell=True)
    return render_template('complete_upload.html', uitkomst="Upload successful!!" sub="Please wait a minute befor searching as we process your added text file(s)")
    

# POST request
@app.route('/dashboard', methods=['POST'])
def dashboard():
    if request.method =='POST':
#        btn_showdata = request.form['data']
        if os.geteuid() == 0:
            s = os.popen("runuser -l hadoop -c 'hdfs dfs -count input'")
            l = os.popen("runuser -l hadoop -c 'hdfs dfsadmin -report | grep Live'")
        else:
            s = os.popen('hdfs dfs -count input')
            l = os.popen('hdfs dfsadmin -report | grep Live')
        m = s.read()
        live_nodes = l.read()
        aantal_bestanden_list = m.split()
        aantal_bestanden = aantal_bestanden_list[1]
#    return render_template('result_dashboard.html', aantal_bestanden=aantal_bestanden)
    return render_template('result_dashboard.html', aantal_bestanden=aantal_bestanden, live_nodes=live_nodes)
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

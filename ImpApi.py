# Importing Libraries
import pymongo
from pymongo import MongoClient
from flask import Flask, request, render_template, jsonify
import json
import zipfile
from werkzeug.utils import secure_filename
from bson import Binary, Code
from bson.json_util import loads, dumps
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def mongo():
    # Connect to MongoDB(Database implementation)
    client = MongoClient('localhost', 27017)
    db = client['implementation']
    return db


def URL():
    return "192.168.43.3"


def URL_API():
    return "https://192.168.43.3:5001"


# Default Route to Web page of the UI
@app.route('/')
def my_form():
    return render_template('index.html')


# Get Request to get the latest directory that needs to be scanned
@app.route('/scanner/<hostname>', methods=['GET'])
def show_hostname(hostname):
    # Validate request is an GET request
    if request.method == 'GET':
        # Get hostname from url
        queryHostname = hostname
        # Connect to MongoDB(Database implementation)
        db = mongo()
        # Query to collection posts to find latest entry with hostname that's provided in URL, sort based on ID.
        # remove all unneeded information from the query
        inhoud = json.dumps(
            db.hosts.find_one({'Hostname': queryHostname},
                              {'_id': False, 'Hostname': False},
                              sort=[('_id', pymongo.DESCENDING)]))
    return jsonify(json.loads(inhoud))


# GET request to get all the hosts and directories
@app.route('/logger/hosts', methods=['GET'])
def hostnames():
    # Validate request is an GET request
    if request.method == 'GET':
        # Connect to MongoDB(Database implementation)
        db = mongo()
        # Create list to store output in
        inhoud = []
        # Store the database query
        dbQuery = db.hosts.find({}, {'_id': False})
        # For loop to loop through host and directories in the database query
        for host in dbQuery:
            inhoud.append(host)
        # Store the output message
        getOutput = json.dumps({"hosts": inhoud})
    return jsonify(json.loads(getOutput))


# POST request from scanner to upload zip file with json data
@app.route('/scanner/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Connect to MongoDB(Database implementation)
        db = mongo()

        # Get file from POST
        f = request.files['file']

        # Store form data in hostname
        hostname = request.form.to_dict()

        # Save zip file from POST
        f.save('/var/www/upload/logger/' + secure_filename(f.filename))

        # Unzip zip file and store in folder
        zip = zipfile.ZipFile('/var/www/upload/logger/scanner.zip', 'a')
        zip.extractall('/var/www/upload/logger/')
        zip.close()

        # Store data.json in data for further processing
        with open('/var/www/upload/logger/data.json') as json_file:
            data = json.load(json_file)

        # Count to track amount of loops, inspect is an list to store files for further inspection
        count = 0
        inspect = []

        # For loop
        for line in data[hostname['hostname']]:
            # store all the information of json object from data.json
            file = data[hostname['hostname']][count]
            # store filename of the file in the json object
            filename = file['filename']

            # Get the information of the file from the mongoDB Database, remove id and get the latest.
            dbfile = json.dumps(db.hashedFiles.find_one({'filename': filename},
                                                        {'_id': False}, sort=[('_id', pymongo.DESCENDING)]))

            # Check if file exists in database otherwise insert it into database and
            # into list of files that need inspection
            if dbfile is "null" or filename != loads(dbfile)['filename']:
                inspect.append({"filename": file['filename'], "hash": file['hash'],
                                "Date scanned": file['Date scanned'],
                                "Date Last Modified": file['Date Last Modified']})
                db.hashedFiles.insert_one(file)
            # When file exists in database check if hash is not the same, then add it to  inspection list.
            else:
                if data[hostname['hostname']][count]['hash'] != loads(dbfile)['hash']:
                    inspect.append({"filename": file['filename'], "hash": file['hash'],
                                    "Date scanned": file['Date scanned'],
                                    "Date Last Modified": file['Date Last Modified']})
                    db.hashedFiles.insert_one(file)
            # add 1 to count
            count += 1

        # create final json object with hostname of the system and the files came from and files that need inspection
        final_json = {"Hostname": hostname['hostname'], hostname['hostname']: inspect}
        # Create json file from final json
        with open('/var/www/upload/logger/inspect.json', 'w') as outfile:
            json.dump(final_json, outfile)

        # Put inspect.json in zip file
        zip = zipfile.ZipFile('/var/www/upload/logger/logger.zip', 'w')
        zip.write('/var/www/upload/logger/inspect.json', arcname='inspect.json')
        zip.close()

        # Define URL, Data and File that needs to be posted to API
        # url = 'https://httpbin.org/post'
        url = URL_API() + '/analyzer'
        data = {'archive': 'Zipped Archive of scanned files', "hostname": hostname['hostname']}
        files = {'file': ('logger.zip', open('/var/www/upload/logger/logger.zip', 'rb'), 'application/zip')}

        # Post to API
        r = requests.post(url, data=data, files=files, verify='../cert.pem')
        print(r.text)

    return jsonify({"message": "Scanned files stored in database and compared to previously stored value. "
                               "Files with different hash send to analyzer."})


@app.route('/analyzer/upload', methods=['POST'])
def analyzer():
    # check if request is an POST
    if request.method == 'POST':
        # Connect to MongoDB(Database implementation)
        db = mongo()

        # Get data from POST
        data = json.loads(request.data)

        # Store Hostname, Whitelist and Blacklist separate
        hostname = data['hostname']
        whitelist = data['whitelist']
        blacklist = data['blacklist']

        # Store insert for db of blacklist and whitelist
        dbBlacklist = {"blacklist": blacklist}
        dbWhitelist = {"whitelist": whitelist}

        # if there is data in blacklist to store it in the database
        if blacklist:
            # Check if there is data in the database
            if db.blacklist.find_one():
                # Get the list of blacklisted files from the database and store it in list
                dbQuery = db.blacklist.find_one({}, {'_id': False})
                list = dbQuery['blacklist']
                # For loop to get whitelisted extensions
                for file in list:
                    # Check if extensions from web page exists in database
                    for bfile in blacklist:
                        if json.dumps(bfile) not in json.dumps(list):
                            # update database with new list
                            myquery = json.loads(json.dumps(db.blacklist.find_one({}, {'_id': False})))
                            db.blacklist.update_one(myquery, {
                                "$addToSet": {"blacklist": json.loads(json.dumps(bfile))}
                            })
                        else:
                            print("Duplicate")
            # if there is no data in database store info from analyzer
            else:
                db.blacklist.insert_one(json.loads(json.dumps(dbBlacklist)))

        # Check if the is data in whitelist
        if whitelist:
            # check if there is data in the database
            if db.whitelist.find_one():
                # store data in list
                list = db.whitelist.find_one({}, {'_id': False})['whitelist']
                # for loop of the files in whitelist
                for file in whitelist:
                    # Check if file from whitelist exist in database otherwise insert it in database
                    if json.dumps(file) not in json.dumps(list):
                        # Get id of object in the database
                        myquery = db.whitelist.find_one({}, {'whitelist': False})
                        # add file from whitelist to array in database
                        db.whitelist.update(myquery, {
                            "$addToSet": {"whitelist": json.loads(json.dumps(file))}
                        })
            # If there is no data in database insert whitelist
            else:
                db.whitelist.insert_one(json.loads(json.dumps(dbWhitelist)))

    return jsonify({"message": "Whitelist and blacklist stored in the database"})


# GET request to get all blacklisted files
@app.route('/logger/blacklist', methods=['GET'])
def blacklist():
    # Check if request is an GET
    if request.method == 'GET':
        # Connect to MongoDB(Database implementation)
        db = mongo()
        # List to store blacklisted files
        inhoud = []

        # For loop to get all blacklisted files from database
        for post in db.blacklist.find({}, {'_id': False}):
            # For loop to loop through files in blacklist
            for pp in post['blacklist']:
                # Append files to inhoud
                inhoud.append(pp)

    return jsonify({"blacklist": inhoud})


# GET request to get whitelisted files based on hostname
@app.route('/logger/whitelist/<hostname>', methods=['GET'])
def whitelist(hostname):
    # Check if method is an GET
    if request.method == 'GET':
        # Store hostname from URL
        QueryHostname = hostname

        # Connect to MongoDB(Database implementation)
        db = mongo()

        # List to store whitelisted files
        inhoud = []

        # For loop to get all whitelisted files based on hostname from the database
        for post in db.whitelist.find({'hostname': QueryHostname}, {'_id': False, "hostname": False}):
            # store whitelisted file in inhoud
            inhoud.append(json.dumps(post['whitelist'][0]['filename']).replace('"', ''))

    return jsonify({"whitelist": inhoud})


# GET request to get all whitelisted files from all hosts
@app.route('/logger/whitelist', methods=['GET', 'POST'])
def totalWhitelist():
    # Check if method is GET
    if request.method == 'GET':
        # Connect to MongoDB(Database implementation)
        db = mongo()
        # List to store blacklisted files
        inhoud = []

        # For loop to get all whitelisted files from database
        for post in db.whitelist.find({}, {'_id': False}):
            # For loop to loop through files in whitelist
            for pp in post['whitelist']:
                # Append files to inhoud
                inhoud.append(pp)
        return jsonify({"whitelist": inhoud})
    if request.method == 'POST':
        # Connect to MongoDB(Database implementation)
        db = mongo()

        # Get POST data in json format
        post = request.json

        # Get Directory and hostname from POST data
        directory = json.loads(json.dumps(post['body']))['filename']
        hostname = json.loads(json.dumps(post['body']))['hostname']

        # Store input from post in correct format
        dbWhitelist = {"whitelist": [{"filename": directory, "hostname": hostname}]}
        post = {"filename": directory, "hostname": hostname}

        # Check if there is data in database
        if db.whitelist.find_one():
            # Store data from the database in a list
            list = db.whitelist.find_one({}, {'_id': False})['whitelist']
            # Check if input from post exist in database
            if json.dumps(post) not in json.dumps(list):
                # Get id of object in the database
                myquery = db.whitelist.find_one({}, {'whitelist': False})
                # add input from post to array in database
                db.whitelist.update(myquery, {
                    "$addToSet": {"whitelist": json.loads(json.dumps(post))}
                })
            # Generate output message
            postOutput = {"message": "Added: " + json.dumps(directory) + "of " + json.dumps(hostname) + "to whitelist"}
            return jsonify(postOutput)
        # If there is no data in the database insert input from post
        else:
            db.whitelist.insert_one(json.loads(json.dumps(dbWhitelist)))
            # Generate output message
            postOutput = {"message": "Added" + json.dumps(post)}
            return jsonify(postOutput)


# GET and POST request to get whitelisted extensions and post extensions that needs to be whitelisted
@app.route('/logger/extensions', methods=['GET', 'POST'])
def extensions():
    # Check if method is an GET
    if request.method == 'GET':
        # Connect to MongoDB(Database implementation)
        db = mongo()
        # Store output
        getOutput = db.extensions.find_one({}, {'_id': False})
        return jsonify(getOutput)

    # Check if method is an POST
    if request.method == 'POST':
        # Connect to MongoDB(Database implementation)
        db = mongo()
        # Store extensions from web page
        post = json.loads(json.dumps(request.json['body']))

        # Check if database already has whitelisted extensions
        if db.extensions.find_one():
            dbQuery = db.extensions.find_one({}, {'_id': False})
            list = dbQuery['extension']
            # For loop to get whitelisted extensions
            for fileExtension in list:
                # Check if extensions from web page exists in database
                if post not in list:
                    # get the old database
                    myquery = json.loads(json.dumps(dbQuery))
                    # update the old databse with the new extension
                    db.extensions.update_one(myquery, {
                        "$addToSet": {"extension": json.loads(json.dumps(post))}
                    })
                    # Store the output message
                    postOutput = {"message": "Added: " + post}

                else:
                    # Store the output message
                    postOutput = {"message": "Input is an duplicate"}

        # if there is no data in database store the post
        else:
            db.extensions.insert_one(json.loads(json.dumps({"extension": [post]})))
            # store the output message
            postOutput = {"message": "Inserted: " + post}
        return jsonify(postOutput)


# POST request
@app.route('/ui/hosts', methods=['POST'])
def test():
    # check if request is an POST
    if request.method == 'POST':
        # Connect to MongoDB(Database implementation)
        db = mongo()
        # Get POST data in json format
        post = request.json

        # Get Directory and hostname from POST data
        directory = json.loads(json.dumps(post['body']))['directory']
        hostname = json.loads(json.dumps(post['body']))['host']
        # store hostname and directory in JSON format
        post = json.loads(json.dumps({"Hostname": hostname, "Location": directory}))
        # Insert post into MongoDB collection posts
        db.hosts.insert_one(post)
        # Return OK to browser on success
        return jsonify({"message": "Hostname and directory stored in the database"})


# IP of the host the Logger runs on(Change IP to the IP of your VM), app runs in Debug Mode
# Don't forget to also change the IP in index.html
if __name__ == '__main__':
    app.run(host=URL(), port=5000, debug=True, ssl_context=('../cert.pem', '../key.pem'))

 #!/usr/bin/env python

import os
import sys

list = []

file_type ="txt"
search_str = os.environ["WORD_INPUT"]

for line in sys.stdin:
    line = line.strip() #Remove white spaces in line of text
    line = line.lower() #Convert line to lower case
    index = line.find(search_str) #Search for string in line
        if (index != -1): #If found:
            #file_name = os.getenv('map_input_file')
            filepath = os.environ["map_input_file"] #Get file path
            file_name = os.path.split(filepath)[-1] #Get file name from path
            if file_name not in list: #If the file isnt in the list already:
                list.append(file_name) #Add file to list
for name in list: 
    print(list)
	

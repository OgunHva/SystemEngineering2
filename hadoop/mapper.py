 #!/usr/bin/env python

import os
import sys

list = []

search_path = "sys.stdin"
file_type ="txt"
search_str = os.environ["WORD_INPUT"]

for line in sys.stdin:
	line = line.strip()
	index = line.find(search_str)
		if (index != -1):
			#file_name = os.getenv('map_input_file')
			filepath = os.environ["map_input_file"]
			file_name = os.path.split(filepath)[-1]
			if file_name not in list:
				list.append(file_name)
for name in list:
    print(list)
	

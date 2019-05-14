from flask import Flask, request, render_template
import requests
import os
from jinja2 import Template


zoekwoord = "randy"
os.popen("hadoop jar /home/hadoop/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.1.2.jar \-file /home/hadoop/hduser/mapper4.py \-mapper 'python3 mapper4.py' \-file /home/hadoop/hduser/reducer4.py \-reducer 'python3 reducer4.py' \-input input2/* \-output output11/ \-cmdenv WORD_INPUT=" + zoekwoord)

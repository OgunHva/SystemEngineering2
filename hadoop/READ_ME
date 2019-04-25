hadoop jar /home/hadoop/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.1.2.jar \
-file /home/hadoop/test/mapperV3.py  \
-mapper 'python mapperV3.py' \
-file /home/hadoop/test/reducerV3.py \
-reducer 'python reducerV3.py' \
-input input/* \
-output output/ \
-cmdenv WORD_INPUT=poison

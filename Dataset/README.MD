# How to create simple text file dataset
[Download one of the .gz textfiles from IMDB](http://ftp.sunet.se/mirror/archive/ftp.sunet.se/pub/tv+movies/imdb/)
```
Extract the .gz file
In linux use the split command to split the file into multiple files (change "$FileName" to your filename)
```
$ `split -l 1000 -d --additional-suffix=.txt $FileName file`
```
You can change the length of the text from the variable "1000"
```

#!/bin/bash

i=0
while read line
do
	array[ $i ]="$line"        
	(( i++ ))
done < <(ls)

myarray=( "${array[@]}" )
echo ${myarray[@]}

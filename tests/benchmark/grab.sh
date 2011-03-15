#!/bin/bash
URL=$1
echo -e "$URL\n"  
NAME=`echo $URL | cut -d/ -f 4`
mkdir data 
cd data 
mkdir $NAME
cd $NAME 
wget -q $URL -O data

cat data | grep sync.next | cut -d' ' -f 10,12 > timestamps.txt
cat data | grep slides | grep title | grep -v sync | cut -d' ' -f 9,14,16 > slides_urls.txt
VIDEO=`cat data | grep mms | sed s#^.*mms#mms#g  | sed -e 's#wmv.*$#wmv#g'`
echo $VIDEO
mimms -r $VIDEO     
rm data 

sed -i -e 's/,\ \"/ /g' slides_urls.txt
sed -i -e 's/\",//g' slides_urls.txt
mkdir slides
python ../build_index.py $VIDEO slides_urls.txt | tee index






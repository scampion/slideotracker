#!/bin/python 
import sys
import urllib
import os
name = sys.argv[1]
video_url = sys.argv[2]
slides_urls = sys.argv[3]

print name + os.sep + os.path.split(video_url)[-1] 
for l in open(slides_urls):
    t, id, url = l.split()
    filename = 'slides' + os.sep + os.path.split(url)[-1]
    urllib.urlretrieve(url, filename)
    print name + os.sep + filename

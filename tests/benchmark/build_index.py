#!/bin/python 
import sys
import urllib
import os
video_url = sys.argv[1]
slides_urls = sys.argv[2]

print os.path.split(video_url)[-1] 
for l in open(slides_urls):
    t, id, url = l.split()
    filename = 'slides' + os.sep + os.path.split(url)[-1]
    urllib.urlretrieve(url, filename)
    print filename

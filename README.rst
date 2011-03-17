.. SlideoTracker documentation master file, created by
   sphinx-quickstart on Fri Feb 11 14:12:24 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============
This software enables to synchronize slides with the corresponding video recording 

*slideotracker = slides + video + tracking* 

Source code
===========

.. warning:: Available soon 

INRIA Gforge project : https://gforge.inria.fr/projects/slideotracker

Screencast
==========

.. raw:: html

  <iframe title="YouTube video player" width="640" height="390" src="http://www.youtube.com/embed/74yZJ63h-Ow" frameborder="0" allowfullscreen></iframe>

Usage
=====

.. 

  Usage: slideotracker.py [options]

  Options:
  -h, --help            show this help message and exit
  -i index, --index=index
                        index file is a simple text file, the first line in
                        the video path, others lines are paths on slide images
                        (use ImageMagick, to convert pdf in several images)
  -p PRECISION, --precision=PRECISION
                        precision in number of frame (default 25)
  -o OUTFILE, --out=OUTFILE
                        output file name, by default results.js
  -f FORMAT, --format=FORMAT
                        output file format js (default),csv
  -d, --debug           debug trace


Example 
-------

.. 
  <iframe title="YouTube video player" width="640" height="390" src="http://www.youtube.com/embed/74yZJ63h-Ow" frameborder="0" allowfullscreen></iframe>

Usage
=====

.. 

  Usage: slideotracker.py [options]

  Options:
  -h, --help            show this help message and exit
  -i index, --index=index
                        index file is a simple text file, the first line in
                        the video path, others lines are paths on slide images
                        (use ImageMagick, to convert pdf in several images)
  -p PRECISION, --precision=PRECISION
                        precision in number of frame (default 25)
  -o OUTFILE, --out=OUTFILE
                        output file name, by default results.js
  -f FORMAT, --format=FORMAT
                        output file format js (default),csv
  -d, --debug           debug trace


Example 
-------

.. code-block:: bash

  #extract pdf pages to jpeg using ImageMagick
  mkdir /tmp/mypdf/
  convert <your.pdf> /tmp/mypdf/slide.jpg
  #build a index file 
  echo './path/to/my/video.ogv' > /tmp/index
  ls -1 /tmp/mypdf/slide* >>/tmp/index
  #Run the tracker  
  python slideotracker.py -i /tmp/index -o results.txt

try also :
  python slideotracker.py -i tests/data/short_test.txt

Results in Javascript format :

slides=[0, 1, 2];

frames=[500, 850, 950];
 

Results in CSV format :

#slide_number;star_frame;end_frame

0;0;500

1;500;850

2;850;950

...
..
.

Display results in HTML5
========================
Open the following file with your browser 

slideotracker/player.html?mediafile=data/video.ogv&slidedir=data/slides&fps=25

Dependencies
============

  * Scikit-Learn 
  * OpenCV 2.1 

TODO/Roadmap
============

  * geometric robustification ... in progress
  * optimize time computing
  * documentation / How it works 

 
Copyright
=========
GNU AFFERO GENERAL PUBLIC LICENSE v3

Credits
=======
  * Images used for the logo : Dropline Nuovo! from http://art.gnome.org/themes/icon
  * RMLL 2010 video for the data test


Dependancies
============
 * python-opencv = 2.0
 * scikit-learn > 0.4.3 
 


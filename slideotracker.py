# SlideoTracker : synchronising slides and video conference
# Copyright (C) 2010 Sebastien Campion

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Contact : sebastien.campion@gmail.com or seb@scamp.fr
import numpy as np
import re 
import os
import logging
from featextractor import FeatExtractor
from tracker import Tracker

def save(outfile, track_results, precision, format):
    '''
    Save method in JavaScript or CSV
    '''
    o = open(outfile,'w')
    if format == 'js' :
        frames = precision*np.array(track_results.keys())
        frames = [int(i) for i in frames]
        o.writelines('slides=%s;\n' % str(track_results.values()))
        o.writelines('frames=%s;\n' % frames )

    elif format == 'csv' :
        o.writelines("#slide_number;star_frame;end_frame\n")
        current_frame = 0 
        for sn,fn in track_results.items():
            sn,sf,ef = sn,precision*current_frame,precision*fn
            o.writelines("%i;%i;%i\n" % (sn,sf,ef))
            current_frame = fn 
    else:
        raise NotImplementedError('Output format %s not available' % format)
    o.close()

def parse_index(index):
    index_file  = open(index)
    video_path = index_file.readline().rstrip()
    slides_paths = dict([(i, path.rstrip()) 
                         for i, path in enumerate(index_file)])
    return video_path, slides_paths 

if __name__ == '__main__':
    from optparse import OptionParser
    import pickle 

    parser = OptionParser()
    parser.add_option('-i', '--index', action='store', type='string', 
                      dest="index", metavar="index", 
                      help="index file is a simple text file, the first line in the video path, others lines are paths on slide images (use ImageMagick, to convert pdf in several images)")
    parser.add_option("-p", "--precision", action="store", type='int',
                      dest='precision', default=25,
                      help='precision in number of frame (default 25)')
    parser.add_option("-o", "--out", action="store", dest='outfile',
                      help='output file name, by default results.js ',
                      default='results.js')
    parser.add_option("-f", "--format", action="store", dest='format',
                      help='output file format js (default),csv ', default='js')
    parser.add_option("-d", "--debug", action="store_true", dest='debug',
                      help='debug trace', default=False) 
    (options, args) = parser.parse_args()

    logger = logging.getLogger('slideotracker')
    if options.debug : 
        dgf  = os.path.basename(options.index)
        dgf += '-'+str(options.precision)
        logging.basicConfig(filename=dgf+'.log',level=logging.DEBUG)

    ############################################################################
    # Extract features 
    videopath, slidefiles = parse_index(options.index)

    fe = FeatExtractor()#debug=options.debug)
    logger.info('Compute slides features, in progress')
    slidefeats = fe.get_slides_feats(slidefiles)
    logger.info('Compute video features, in progress')
    videofeats = fe.get_video_feats(videopath, options.precision)

    if options.debug :
        pickle.dump(slidefeats, open(dgf+'.sf','w'))
        pickle.dump(videofeats, open(dgf+'.vf','w'))

    ############################################################################
    # Start slide tracking 
        
    logger.info('Start slide tracking process')
    tr = Tracker(slidefeats, videofeats, options.precision)
    matrix, frames_index = tr.track()
    track_results = tr.geohash_filter(matrix, frames_index)
    
    if options.debug :
        pickle.dump(matrix, open(dgf+'.mat', 'w'))
        pickle.dump(track_results, open(dgf+'.res','w'))
    
    save(options.outfile, track_results, 
         options.precision, format=options.format)
        
    




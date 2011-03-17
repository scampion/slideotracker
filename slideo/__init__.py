from slideotracker import SlideoTracker
import os

def parse_index(index):
    abspath = os.path.abspath(os.path.dirname(index))
    index_file = open(index)    
    video_path = os.path.join(abspath, index_file.readline().rstrip())
    slides_paths = dict([(i, os.path.join(abspath, path.rstrip()))
                         for i, path in enumerate(index_file)])
    return video_path, slides_paths


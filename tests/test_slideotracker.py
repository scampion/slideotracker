import unittest
import logging
import os
from slideo import slideotracker as st

logging.basicConfig(level=logging.DEBUG)

class TestMain(unittest.TestCase):
    def setUp(self):
        self.index = 'tests/data/short_test.txt'

    def test_parse_index(self):
        video, slides = st.parse_index(self.index)        
        print len(slides), 'nb slide'
        print video 
        self.assertTrue(video.endswith('svideo.avi') and 
                        len(slides) == 4) 

class TestSlideoTracker(unittest.TestCase):
    def setUp(self):
        self.index = 'tests/data/test.txt'
        videopath, slidepath = st.parse_index(self.index)
        self.slideo = st.SlideoTracker(videopath, slidepath, frame_rate=25,
                                       debug=True)

        #self.index = 'tests/data/index/short_test.txt'
        #videopath, slidepath = st.parse_index(self.index)
        #self.slideo = st.SlideoTracker(videopath, slidepath, frame_rate=50)
        
    def test_video_feats(self):
        for frame_id, (fkp, fvt), frame in self.slideo._video_feats():
            if frame_id > 50:
                break 
        self.assertTrue(frame_id == 75)

    def test_video_track(self):
        self.slideo.track()

            
        
#    def test_image_feats(self):
#        self.fe._get_image_feats('tests/data/frame-0001.jpg', 100)

#     def test_slides_feats(self):
#         self.fe.get_slides_feats(self.sfiles, hessian=1000)

#     def test_video_feats(self):
#         videofeats = self.fe.get_video_feats(self.videopath, 100)
#         print len(videofeats)
#         self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()


import unittest
import cv
import logging
import os
from featextractor import FeatExtractor
import slideotracker as st

logging.basicConfig(level=logging.DEBUG)

class TestFeaturesExtractions(unittest.TestCase):
    def setUp(self):
        self.fe = FeatExtractor(debug=True)
        self.sfiles = {0: 'tests/data/slide-0.jpg',
                       1: 'tests/data/slide-1.jpg'}
        self.videopath = 'tests/data/video.ogv'

    def test_image_feats(self):
        self.fe._get_image_feats('tests/data/frame-0001.jpg', 100)

    def test_slides_feats(self):
        self.fe.get_slides_feats(self.sfiles, hessian=1000)

    def test_video_feats(self):
        videofeats = self.fe.get_video_feats(self.videopath, 100)
        print len(videofeats)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()


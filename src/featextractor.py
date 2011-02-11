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
import cv
import numpy as np 
import logging

class FeatExtractor:   
    def __init__(self, debug = False  ):
        self.debug = debug
        self.log = logging.getLogger("FeatExtractor")

    def get_video_feats(self, videopath, step, hessian = 100):
        '''
        Compute video features 
        return a dictionary 
        [key = frame_number | value = (keypoints, vectors)]
        ''' 
        log = logging.getLogger("FeatExtractor.get_video_feats")
        results = {}

        video = cv.CreateFileCapture(videopath)
        frame = cv.QueryFrame(video)  
        frame_gray = cv.CreateImage(cv.GetSize(frame), frame.depth, 1)
        fn = 0 
        while frame :  
            cv.ConvertImage(frame, frame_gray)
            kp, vt= cv.ExtractSURF(frame_gray, None, cv.CreateMemStorage(),
                                  (1, hessian, 3, 1))

            log.debug('frame id %06d' % fn)
            if self.debug :
                self.save(frame_gray, kp, vt, '/tmp/frame-%d.jpg' % fn)
            results[fn] = self.__cv2numpy(kp, vt)
            for i in range(step):
                frame = cv.QueryFrame(video)  
                fn += 1 
        return results 

    def get_slides_feats(self, slidesfiles, hessian=1000):
        '''
        Compute slides features 
        return a dictionary 
        [key = slide_number | value = (keypoints, vectors)]
        ''' 
        return dict([ (id, self._get_image_feats(fp, hessian))
                     for id, fp in slidesfiles.items()])

    def _get_image_feats(self, filepath, hessian_threshold):
        im = cv.LoadImage(filepath, 1)
        im_gray = cv.CreateImage(cv.GetSize(im), im.depth, 1)
        cv.ConvertImage(im, im_gray)
        kp, vt= cv.ExtractSURF(im_gray, None, cv.CreateMemStorage(),
                               (1, hessian_threshold, 3, 1))        
        if self.debug :
            self.save(im_gray, kp, vt, filepath+'-debug.jpg')

        return self.__cv2numpy(kp, vt)
        
    
    def __cv2numpy(self, kp, vt):        
        kp = np.array([ (x, y, l, s, d, h) for (x, y), l, s, d, h in kp ])
        #kp.dtype = self.keypoint_type
        return kp, np.array(vt)

    def save(self, cv_img, keypoints, descriptors, outfile):
        '''
        Save image with associted keypoints
        ''' 
        import pickle
        pickle.dump(descriptors, open(outfile+'.vt','wb'))
        pickle.dump(keypoints, open(outfile+'.kp','wb')) 
        font = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 0.4, 0.4)
        for i, ((x, y), laplacian, size, dir, hessian) in enumerate(keypoints):
            cv.Circle(cv_img,(x, y), 2, cv.CV_RGB(255, 0, 0))
            cv.PutText(cv_img, str(i), (x+3, y+3), font,cv.RGB(255,0,0))
            cv.SaveImage(outfile, cv_img)



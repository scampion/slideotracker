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
from __future__ import division
import numpy as np
import os
import logging
import cv
from scikits.learn import neighbors as knn
import homography

np.set_printoptions(suppress=True, precision=2)


class SlideoTracker:
    """
    This software enables to synchronize slides with the corresponding 
    video recording.
    slideotracker = slides + video + tracking
    """
    HESSIAN_THRESHOLD = 100
    RATIO_KNN = 0.85
    RATIO_HOM = 0.2
    MIN_H_POINTS = 12
    MATCH_THRESHOLD = 20

    def __init__(self, videopath, slidepaths, frame_rate=25, debug=False):
        self.frame_rate = frame_rate
        self.videopath = videopath
        self.slidepaths = slidepaths
        print '#Compute slides features ...'
        self.slidefeats = dict([(id, self._image_feats_by_file(path))
                                for id, path in self.slidepaths.items()])
        self.slideclfs = dict([(id, knn.Neighbors(n_neighbors=2).fit(vt))
                               for id, (kp, vt) in self.slidefeats.items()])
        self.slideims = dict([(id, self._convert_image(p))
                               for id, p in self.slidepaths.items()])
        print '#done'
        print
        self.debug = debug

    def track(self):
        for frame_id, (fkp, fvt), frame in self._video_feats():
            if self.debug:
                print "#in progress, frame", frame_id
            for slide_id, slide_path in self.slidepaths.items():
                if self.debug:
                    print "#\t", self.slidepaths[slide_id], " slide in progress"

                f, t = self._best_kp(slide_id, (fkp, fvt))

                if self.debug:
                    sim = self.slideims[slide_id]
                    self._save(frame, sim, f, t,
                               "%05d-%s.jpg" % (frame_id, str(slide_id)))
                if self._ransac_test(f, t):                    
                    yield frame_id, self.slidepaths[slide_id]
                    if self.debug:
                        print "MATCH : ", frame_id, slide_path
                    break



    def _best_kp(self, slide_id, (fkp, fvt)):
        tkp, tvt = self.slidefeats[slide_id]
        clf = self.slideclfs[slide_id]

        dist, ind = clf.kneighbors(fvt, n_neighbors=2)
        f_dist, s_dist = np.hsplit(dist, 2)
        f_ind, s_ind = np.hsplit(ind, 2)
        best_fkp_ind = np.flatnonzero((f_dist / s_dist) < self.RATIO_KNN)
        best_tkp_ind = f_ind[best_fkp_ind].reshape(-1)

        #select only x, y components
        fkp, tkp = [np.hsplit(a, [2, ])[0]
                    for a
                    in [fkp[best_fkp_ind], tkp[best_tkp_ind]]]
        return fkp, tkp

    def _ransac_test(self, fkp, tkp):
        minp = max(self.MIN_H_POINTS, int(len(fkp) * self.RATIO_HOM))
        if self.debug :
            print "#\tnb of points %i | min nb points %i" % (len(fkp), minp)
        fsize, tsize = [a.shape[0] for a in [fkp, tkp]]
        fkp, tkp = [a.T  for a in [fkp, tkp]]
        fkp, tkp = [np.vstack((a, np.ones((1, s))))
                    for a, s in zip([fkp, tkp], [fsize, tsize])]
        try:
            homography.H_from_ransac(fkp, tkp, homography.ransac_model(),
                                     maxiter=100,
                                     match_theshold=self.MATCH_THRESHOLD,
                                     minp=minp)
        except ValueError:
            return False
        except np.linalg.LinAlgError:
            return False

        return True

    def _video_feats(self):
        '''
        Generator, compute video features
        return a dictionary
        [key = frame_number | value = (keypoints, vectors)]
        '''
        video = cv.CreateFileCapture(self.videopath)
        frame = cv.QueryFrame(video)
        frame_gray = cv.CreateImage(cv.GetSize(frame), frame.depth, 1)
        fn = 0
        while frame:
            cv.ConvertImage(frame, frame_gray)
            kp, vt = self._image_feats(frame_gray)
            yield fn, (kp, vt), frame_gray

            for i in range(self.frame_rate):
                frame = cv.QueryFrame(video)
                fn += 1

    def _image_feats(self, im_gray):
        kp, vt = cv.ExtractSURF(im_gray, None, cv.CreateMemStorage(),
                               (1, self.HESSIAN_THRESHOLD, 3, 4))
        #reformat
        kp = np.array([(x, y, l, s, d, h) for (x, y), l, s, d, h in kp])
        vt = np.array(vt)
        return kp, vt

    def _convert_image(self, filepath):
        im = cv.LoadImage(filepath, 1)
        im_gray = cv.CreateImage(cv.GetSize(im), im.depth, 1)
        cv.ConvertImage(im, im_gray)
        return im_gray

    def _image_feats_by_file(self, filepath):
        im_gray = self._convert_image(filepath)
        return self._image_feats(im_gray)

    def _save(self, fim, tim, fkp, tkp, ofile):
        import Image, ImageDraw 
        fim, tim = [Image.fromstring("L", cv.GetSize(i), i.tostring())
                    for i in [fim, tim]]
        rsize = (fim.size[0] + tim.size[0], max(fim.size[1], tim.size[1]))
        rim = Image.new('RGB', rsize)
        rim.paste(fim, box=(0, 0))
        rim.paste(tim, box=(fim.size[0], 0))
        
        d = ImageDraw.Draw(rim)         
        for (x1, y1), (x2, y2) in zip(fkp, tkp):
            d.line(((x1,y1),(x2+fim.size[0],y2)), fill='red')            
        rim.save(ofile) 

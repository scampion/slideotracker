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
import math
import os
import logging
from scikits.learn import neighbors as knn
import cv
import homography
import ransac
import operator
import time

np.set_printoptions(suppress=True, precision=2)

class SlideoTracker:
    """
    This software enables to synchronize slides with the corresponding 
    video recording.
    slideotracker = slides + video + tracking
    """
    HESSIAN_THRESHOLD = 100
    RATIO_KNN = 0.8
    RANSAC_ITER_RATIO = 10
    RANSAC_ITER  = 100
    MIN_H_POINTS = 20
    MATCH_THRESHOLD = 50
    
    DISTS_WEIGHT = 1
    RANSAC_WEIGHT = 2
    SCALE_RATIO_WEIGHT = 1
       
    THRESHOLD = 1
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
            scores = dict.fromkeys(self.slidepaths.keys())

            if self.debug:
                print "frame ", frame_id

            for slide_id, slide_path in self.slidepaths.items():
                # 1 : compute SURF distances
                st0 = time.time()
                f, t, dist = self._best_kp(slide_id, (fkp, fvt))
                st1 = time.time()
            
                # 2 : geometric robustification
                t0 = time.time()
                nb_inliners, scale_ratio = self._ransac(f, t)
                t1 = time.time()
                #geoscore = nb_inliners / (math.sqrt(f.shape[0] * t.shape[0]))
                geoscore = nb_inliners / f.shape[0]

                s = -1 
                if geoscore != 0:
                    s = math.log(scale_ratio * self.SCALE_RATIO_WEIGHT) +\
                        math.log((1 - dist) * self.DISTS_WEIGHT) +\
                        math.log(geoscore * self.RANSAC_WEIGHT)
                    s *= -1
                scores[slide_id] = s 
                    
                if self.debug:
                    m = ''                    
                    m += '| %0.2f score ' % s                    
                    m += '| %0.3f dist ' % dist
                    m += '| %04d  inliners ' % nb_inliners
                    m += '| %0.3f geoscore ' % geoscore
                    m += '| %0.3f sr ' % scale_ratio
                    m += '|| %04d ip '% f.shape[0]
                    m += '| %04d op' % t.shape[0]
                    m += '| %05s ' % slide_id
                    m += '| %0.3f r time  ' % (t1-t0)
                    m += '| %0.3f tot time' %  (t1-t0+st1-st0)
                    m += '| %s' % os.path.basename(slide_path)
                    if s > 0 :
                        print m 
                    sim = self.slideims[slide_id]
                    self._save(frame, sim, f, t,
                               "%05d-%s.jpg" % (frame_id, str(slide_id)))

            slide_id = min(scores.iteritems(), key=operator.itemgetter(1))[0]
            if scores[slide_id]  < self.THRESHOLD :
                yield frame_id, self.slidepaths[slide_id]
                    

    def _best_kp(self, slide_id, (fkp, fvt)):
        #print 'select best kp'
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
        dist = np.mean(f_dist[best_fkp_ind])
        return fkp, tkp, dist    
 
    def _ransac(self, fkp, tkp):
        #minp = max(self.MIN_H_POINTS, int(len(fkp) * self.RATIO_HOM))        
        fsize, tsize = [a.shape[0] for a in [fkp, tkp]]
        fkp, tkp = [a.T  for a in [fkp, tkp]]
        fkp, tkp = [np.vstack((a, np.ones((1, s))))
                    for a, s in zip([fkp, tkp], [fsize, tsize])]
        #maxiter = self.RANSAC_ITER_RATIO * fsize
        maxiter = self.RANSAC_ITER
        try:
            H, r = homography.H_from_ransac(fkp, tkp,
                                            homography.ransac_model(),
                                            maxiter=maxiter,
                                            match_theshold=self.MATCH_THRESHOLD,
                                            minp=self.MIN_H_POINTS)
        except ransac.RansacError:
            return 0, 0 
        except np.linalg.LinAlgError:
            return 0, 0         
        sx = abs(H[0][0])
        sy = abs(H[1][1])
        return len(r['inliers']), min(sx, sy) / max(sx, sy)

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

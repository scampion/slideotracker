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
from scikits.learn import neighbors
import numpy as np
import sys
import logging
#import geohash_orig 
#from geohash import GeoHash
#from geohash_optimize import GeoHash
#from geohash_optimize2 import GeoHash
#from geohash_test import GeoHash
import time

class Tracker:
    """
    Tracker class use knn algorithmes to synchronise
    slides and video frame features.
    It use geometric hashing, to improve results 
    @article{10.1109/99.641604,
    author = {Haim J. Wolfson and Isidore Rigoutsos},
    title = {Geometric Hashing: An Overview},
    journal ={Computing in Science and Engineering},
    volume = {4},
    issn = {1070-9924},
    year = {1997},
    pages = {10-21},
    doi = {http://doi.ieeecomputersociety.org/10.1109/99.641604},
    publisher = {IEEE Computer Society},
    address = {Los Alamitos, CA, USA},
    }
    """
    GEOHASH_QUANT =  100
    GEO_WEIGHT    = 1.02 #>1 
    NB_QUERY_KP   = 20
    THRESHOLD     = 0.6
    NBEST = 10

    def __init__(self,slidefeats,videofeats,precision):
        """
        Tracker constructor

        :param slidefeats: slides features, 
        keys are slides identifiers and values tuple
        (keypoints,vectors) 
        :type: dict
        :param videofeats: videos features  
        keys are frame identifiers and values tuple
        (keypoints,vectors) 
        :type: dict
        """
        self.log = logging.getLogger("Tracker")
        self.slidefeats = slidefeats
        self.videofeats = videofeats
        self.precision = precision
                
    def geohash_filter(self, matrix, frame_index):
        """
        Apply a geometric robustification to select right slide
        :rtype: dict[frame_id] = slide_id
        """        
        fn, sn = matrix.shape #number of frames, number of slides
        result = {}

        # foreach frame compute the best matching slide 
        for votes, frame_id in zip(matrix, frame_index):
            self.log.debug('frame id %04d | knn %s' % (frame_id, str(votes)))

            ###################################################################
            # Filters : keep nbest slides (n=CAND)
            #           keep slides with score > THRESHOLD 
            nbest = np.argsort(votes)[-self.NBEST:] 
            ind   = np.flatnonzero(votes[nbest] >= self.THRESHOLD )
            slides_ids = nbest[ind]

            ##################################################################
            # Compute geometry score
            t0 = time.time()
            #GS1
            #geoscores = self._geoscore(frame_id, slides_ids)
            #GS1 

            #GS2
            #self.log.info('Build geometric model, be patient')
            #geomod = self._build_geomodels()
            #geoscores = self._geoscore2(frame_id, slides_ids, geomodel)
            #GS2

            #self.log.info('frame id %04d | geoscore computing time %0.3f' %
            #             (frame_id, time.time()-t0))
            #self.log.debug('frame id %04d | geo %s'%(frame_id, str(geoscores)))

            #for sid, score in geoscores:
            #    votes[sid] = votes[sid] * (score + self.GEO_WEIGHT)

            result[frame_id] = np.argmax(votes)

            m = str(['%0.3f' % v for v in votes])
            self.log.debug('frame id %04d | knn*geo %s' % (frame_id, m))
        return result
                    
    def _geoscore(self, frame_id, slide_ids):
        scores = {}
        for slide_id in slide_ids:
            sbkp, fbkp = self._nbest_keypoints(slide_id, frame_id)

            #gh = geohash_orig.GeoHash(quant=self.GEOHASH_QUANT)
            #gh.addmodel(slide_id, sbkp)
            #self.log.debug('--------good----'+str(gh.votes(fbkp)))

            geohash = GeoHash(quant=self.GEOHASH_QUANT)
            geohash.addmodel(slide_id, sbkp)
            self.log.debug('--------test----'+str(geohash.votes(fbkp)))
            best = geohash.votes(fbkp)[0]

            score, model = best
            scores[slide_id] = score

        #normalize
        geoscores = [ (k, v/(2*self.NB_QUERY_KP*self.NB_QUERY_KP-1))
                     for k, v in scores.items() if v != 0 ]
        return np.array(geoscores)

    def _build_geomodels(self):
        geohash = GeoHash(quant=self.GEOHASH_QUANT)
        for s_id, (s_kp, s_vt) in self.slidefeats.items():
            skp = [[x,y] for x, y, lap, size, dir, hes in s_kp]
            geohash.addmodel(s_id, skp)
            self.log.debug('model %s geohashed' % s_id)
        return geohash

    def _geoscore2(self, frame_id, slide_ids, geohash):        
        f_kp, f_vt = self.videofeats[frame_id]
        fkp = [[x,y] for x, y, lap, size, dir, hes in f_kp]
        print 'before geohash votes'
        scores = geohash.votes(fbkp)
        print 'after geohash votes'
        #normalize
        geoscores = [ (k, v/(2*self.NB_QUERY_KP*self.NB_QUERY_KP-1))
                     for k,v in scores.items() if v != 0 ]
        return np.array(geoscores)


    def track(self):
        """
        start tracking process 
        return an 2-d array, matrix 
        where matrix[frame_id] = similarity coefs for
        each slides
        :rtype: (list of frame_id,numpy.array)
        """
        nb_slides = len(self.slidefeats.keys())
        nb_frames = len(self.videofeats.keys())
        matrix = np.zeros((nb_frames, nb_slides), 'int')

        labels, vectors = self._reshape()
        clf = neighbors.Neighbors()
        clf.fit(vectors, labels)

        frame_index = self.videofeats.keys()
        frame_index.sort()
        for i,f in enumerate(frame_index):
            kp, vt = self.videofeats[f]
            t0 = time.time()
            pred = clf.predict(vt)
            v = np.bincount(np.cast['int'](pred))
            matrix[i] = np.resize(v, nb_slides)
            self.log.info('NN computation time %0.3f' % (time.time()-t0))
            self._display_progress(i, f)

        return self._normalize(matrix), frame_index

    def _reshape(self): 
        '''
        XXX : TODO more pythonic function using numpy searchsort
        '''
        vectors = []
        labels  = []
        for id, (kp, vt) in self.slidefeats.items():
            vectors.extend(vt)
            labels.extend([id]*len(vt))
        return labels, vectors

    def _normalize(self,matrix):
        mean = np.mean(matrix,axis=0)
        gmean = np.mean(matrix)
        l =  matrix**2/(mean+gmean**0.5)**2
        return (l[:-1]*l[1:])**0.5 #smooth

    def _nbest_keypoints(self, slide_id, frame_id):
        #select the best matching keypoints
        f_kp, f_vt = self.videofeats[frame_id]
        s_kp, s_vt = self.slidefeats[slide_id]
        clf = neighbors.Neighbors(n_neighbors=1)
        clf.fit(f_vt)

        dist, sind = clf.kneighbors(s_vt[0:self.NB_QUERY_KP])
        skp = [[x,y] for x, y, lap, size, dir, hes in s_kp[0:self.NB_QUERY_KP]]
        fkp = [[x,y] for x, y, lap, size, dir, hes in f_kp[sind]]
        return skp, fkp

    def _display_progress(self, i, f):
        nb_frames = len(self.videofeats.keys())        
        m = '[%05i/%05i]/%02i%%/%06i' %(i, nb_frames, 100*i/nb_frames, f)
        sys.stdout.write('\b'*len(m)+m)
        sys.stdout.flush()

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

    def track(self):
        for frame_id, (fkp, fvt), frame in self._video_feats():
            print "#in progress, frame", frame_id
            for slide_id in self.slidepaths.keys():
                f, t = self._best_kp(slide_id, (fkp, fvt))
                print "#\t", self.slidepaths[slide_id], " slide in progress"
                rtest = self._ransac_test(f, t)

                #DEBUG
                sim = self.slideims[slide_id]
                self._save(frame, sim, f, t,
                           "%05d-%s.jpg" % (frame_id, str(slide_id)))
                #DEBUG

                if rtest:
                    print frame_id, self.slidepaths[slide_id]
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
        print "#\t debug ", minp, len(fkp)
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




def save(outfile, track_results, precision, format):
    '''
    Save method in JavaScript or CSV
    '''
    o = open(outfile, 'w')
    if format == 'js':
        frames = precision * np.array(track_results.keys())
        frames = [int(i) for i in frames]
        o.writelines('slides=%s;\n' % str(track_results.values()))
        o.writelines('frames=%s;\n' % frames)

    elif format == 'csv':
        o.writelines("#slide_number;star_frame;end_frame\n")
        current_frame = 0
        for sn, fn in track_results.items():
            sn, sf, ef = sn, precision * current_frame, precision * fn
            o.writelines("%i;%i;%i\n" % (sn, sf, ef))
            current_frame = fn
    else:
        raise NotImplementedError('Output format %s not available' % format)
    o.close()


def parse_index(index):
    index_file = open(index)
    video_path = index_file.readline().rstrip()
    slides_paths = dict([(i, path.rstrip())
                         for i, path in enumerate(index_file)])
    return video_path, slides_paths

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-i', '--index', action='store', type='string',
                      dest="index", metavar="index",
                      help="index file is a simple text file, the first " +
                      "line in the video path, others lines are paths on " +
                      "slide images (use ImageMagick, to convert pdf " +
                      "in several images)")
    parser.add_option("-p", "--precision", action="store", type='int',
                      dest='precision', default=25,
                      help='precision in number of frame (default 25)')
    parser.add_option("-o", "--out", action="store", dest='outfile',
                      help='output file name, by default results.js ',
                      default='results.js')
    parser.add_option("-f", "--format", action="store", dest='format',
                      help='output file format js (default),csv ',
                      default='js')
    parser.add_option("-d", "--debug", action="store_true", dest='debug',
                      help='debug trace', default=False)
    (options, args) = parser.parse_args()

    logger = logging.getLogger('slideotracker')
    if options.debug:
        dgf = os.path.basename(options.index)
        dgf += '-' + str(options.precision)
        logging.basicConfig(filename=dgf + '.log', level=logging.DEBUG)

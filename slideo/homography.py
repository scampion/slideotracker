"""
Robust homography estimation using RANSAC
http://www.janeriksolem.net/
"""
import numpy as np
import ransac


def H_from_points(fp, tp):
    """ find homography H, such that fp is mapped to tp
        using the linear DLT method. Points are conditioned
        automatically."""
    assert fp.shape == tp.shape

    #condition points (important for numerical reasons)
    #--from points--
    m = np.mean(fp[:2], axis=1)
    maxstd = np.max(np.std(fp[:2], axis=1))
    C1 = np.diag([1 / maxstd, 1 / maxstd, 1])
    C1[0][2] = -m[0] / maxstd
    C1[1][2] = -m[1] / maxstd
    fp = np.dot(C1, fp)

    #--to points--
    m = np.mean(tp[:2], axis=1)
    #C2 = C1.copy() #must use same scaling for both point sets
    maxstd = np.max(np.std(tp[:2], axis=1))
    C2 = np.diag([1 / maxstd, 1 / maxstd, 1])
    C2[0][2] = -m[0] / maxstd
    C2[1][2] = -m[1] / maxstd
    tp = np.dot(C2, tp)

    #create matrix for linear method, 2 rows for each correspondence pair
    nbr_correspondences = fp.shape[1]
    A = np.zeros((2 * nbr_correspondences, 9))
    for i in range(nbr_correspondences):
        A[2 * i] = [-fp[0][i], -fp[1][i], -1,
                     0, 0, 0,
                     tp[0][i] * fp[0][i], tp[0][i] * fp[1][i], tp[0][i]]
        A[2 * i + 1] = [0, 0, 0,
                      -fp[0][i], -fp[1][i], -1, tp[1][i] * fp[0][i],
                      tp[1][i] * fp[1][i], tp[1][i]]

    U, S, V = np.linalg.svd(A)
    H = V[8].reshape((3, 3))
    #decondition
    H = np.dot(np.linalg.inv(C2), np.dot(H, C1))
    #normalize and return
    return H / H[2][2]


class ransac_model:
    """ class for testing homography fit with ransac.py from
        http://www.scipy.org/Cookbook/RANSAC"""

    def __init__(self, debug=False):
        self.debug = debug

    def fit(self, data):
        """ fit homography to four selected correspondences"""
        #transpose to fit H_from_points()
        data = data.T
        #from points
        fp = data[:3, :4]
        #target points
        tp = data[3:, :4]
        #fit homography, H
        H = H_from_points(fp, tp)
        return H

    def get_error(self, data, H):
        """ apply homography to all correspondences,
            return error for each transformed point"""
        data = data.T
        #from points
        fp = data[:3]
        #target points
        tp = data[3:]
        #transform fp
        fp_transformed = np.dot(H, fp)
        #normalize hom. coordinates
        for i in range(3):
            fp_transformed[i] /= fp_transformed[2]

        err_per_point = np.sqrt(np.sum((tp - fp_transformed) ** 2, axis=0))
        return err_per_point


def H_from_ransac(fp, tp, model, maxiter=1000, match_theshold=10, minp=10):
    """ robust estimation of homography H from point
        correspondences using RANSAC (ransac.py from
        http://www.scipy.org/Cookbook/RANSAC).

        input: fp,tp (3*n arrays) points in hom. coordinates
    """
    #use ransac class
    model = ransac_model()
    #group corresponding points
    data = np.vstack((fp, tp))
    H, inliers = ransac.ransac(data.T, model, 4, maxiter, match_theshold, minp,
                               return_all=True)
    return H, inliers


def normalize(pt):
    for i in range(3):
        pt[i] /= pt[2]
    return pt

from pylab import *
from numpy import *
from numpy import random


def Haffine_from_points(fp,tp):
    """ find H, affine transformation, such that 
        tp is affine transf of fp"""

    if fp.shape != tp.shape:
        raise RuntimeError, 'number of points do not match'

    #condition points
    #-from points-
    m = mean(fp[:2], axis=1)
    maxstd = max(std(fp[:2], axis=1))
    C1 = diag([1/maxstd, 1/maxstd, 1]) 
    C1[0][2] = -m[0]/maxstd
    C1[1][2] = -m[1]/maxstd
    fp_cond = dot(C1,fp)

    #-to points-
    m = mean(tp[:2], axis=1)
    C2 = C1.copy() #must use same scaling for both point sets
    C2[0][2] = -m[0]/maxstd
    C2[1][2] = -m[1]/maxstd
    tp_cond = dot(C2,tp)

    #conditioned points have mean zero, so translation is zero
    A = concatenate((fp_cond[:2],tp_cond[:2]), axis=0)
    U,S,V = linalg.svd(A.T)

    #create B and C matrices as Hartley-Zisserman (2:nd ed) p 130.
    tmp = V[:2].T
    B = tmp[:2]
    C = tmp[2:4]

    tmp2 = concatenate((dot(C,linalg.pinv(B)),zeros((2,1))), axis=1) 
    H = vstack((tmp2,[0,0,1]))

    #decondition
    H = dot(linalg.inv(C2),dot(H,C1))

    return H / H[2][2]

def H_from_ransac(fp,tp,model,maxiter=1000,match_theshold=10, minp=10):
    """ robust estimation of homography H from point 
        correspondences using RANSAC (ransac.py from
        http://www.scipy.org/Cookbook/RANSAC).

        input: fp,tp (3*n arrays) points in hom. coordinates"""

    import ransac

    #use ransac class
    model = ransac_model()
    #group corresponding points
    data = vstack((fp,tp))

    H = ransac.ransac(data.T,model,4,maxiter,match_theshold,minp)

    return H

def normalize(pt):
    for i in range(3):
        pt[i] /= pt[2]
    return pt 


class ransac_model:
    """ class for testing homography fit with ransac.py from
        http://www.scipy.org/Cookbook/RANSAC"""

    def __init__(self,debug=False):
        self.debug = debug

    def fit(self, data):
        """ fit homography to four selected correspondences"""

        #transpose to fit H_from_points()
        data = data.T

        #from points
        fp = data[:3,:4]
        #target points
        tp = data[3:,:4]

        #fit homography, H
        H = H_from_points(fp,tp)

        return H

    def get_error( self, data, H):
        """ apply homography to all correspondences, 
            return error for each transformed point"""

        data = data.T

        #from points
        fp = data[:3]
        #target points
        tp = data[3:]

        #transform fp
        fp_transformed = dot(H,fp)

        #normalize hom. coordinates
        for i in range(3):
            fp_transformed[i] /= fp_transformed[2]

        err_per_point = sqrt( sum((tp-fp_transformed)**2,axis=0) )

        return err_per_point
        
        
def H_from_points(fp,tp):
    """ find homography H, such that fp is mapped to tp
        using the linear DLT method. Points are conditioned
        automatically."""

    if fp.shape != tp.shape:
        raise RuntimeError, 'number of points do not match'


    #condition points (important for numerical reasons)
    #--from points--
    m = mean(fp[:2], axis=1)
    maxstd = max(std(fp[:2], axis=1))
    C1 = diag([1/maxstd, 1/maxstd, 1]) 
    C1[0][2] = -m[0]/maxstd
    C1[1][2] = -m[1]/maxstd
    fp = dot(C1,fp)

    #--to points--
    m = mean(tp[:2], axis=1)
    #C2 = C1.copy() #must use same scaling for both point sets
    maxstd = max(std(tp[:2], axis=1))
    C2 = diag([1/maxstd, 1/maxstd, 1])
    C2[0][2] = -m[0]/maxstd
    C2[1][2] = -m[1]/maxstd
    tp = dot(C2,tp)


    #create matrix for linear method, 2 rows for each correspondence pair
    nbr_correspondences = fp.shape[1]
    A = zeros((2*nbr_correspondences,9))
    for i in range(nbr_correspondences):        
        A[2*i] = [-fp[0][i],-fp[1][i],-1,0,0,0,tp[0][i]*fp[0][i],tp[0][i]*fp[1][i],tp[0][i]]
        A[2*i+1] = [0,0,0,-fp[0][i],-fp[1][i],-1,tp[1][i]*fp[0][i],tp[1][i]*fp[1][i],tp[1][i]]

    U,S,V = linalg.svd(A)

    H = V[8].reshape((3,3))    

    #decondition
    H = dot(linalg.inv(C2),dot(H,C1))

    #normalize and return
    return H / H[2][2]


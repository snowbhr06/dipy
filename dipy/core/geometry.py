''' Utility functions for algebra etc '''

import math

import numpy as np
import numpy.linalg as npl


def sphere2cart(r, theta, phi):
    ''' Spherical to Cartesian coordinates

    This is the standard physics convention where `theta` is the
    inclination (polar) angle, and `phi` is the azimuth angle.

    Imagine a sphere with center (0,0,0).  Orient it with the z axis
    running south->north, the y axis running west-east and the x axis
    from posterior to anterior.  `theta` (the inclination angle) is the
    angle to rotate from the z-axis (the zenith) around the y-axis,
    towards the x axis.  Thus the rotation is counter-clockwise from the
    point of view of positive y.  `phi` (azimuth) gives the angle of
    rotation around the z-axis towards the y axis.  The rotation is
    counter-clockwise from the point of view of positive z.

    Equivalently, given a point P on the sphere, with coordinates x, y,
    z, `theta` is the angle between P and the z-axis, and `phi` is
    the angle between the projection of P onto the XY plane, and the X
    axis.

    Parameters
    ----------
    r : array-like
       radius
    theta : array-like
       inclination or polar angle
    phi : array-like
       azimuth angle

    Returns
    -------
    x : array
       x coordinate(s) in Cartesion space
    y : array
       y coordinate(s) in Cartesian space
    z : array
       z coordinate

    Notes
    -----
    See these pages:

    * http://en.wikipedia.org/wiki/Spherical_coordinate_system
    * http://mathworld.wolfram.com/SphericalCoordinates.html

    for excellent discussion of the many different conventions
    possible.  Here we use the physics conventions, used in the
    wikipedia page.

    Derivations of the formulae are simple. Consider a vector x, y, z of
    length r (norm of x, y, z).  The inclination angle (theta) can be
    found from: cos(theta) == z / r -> z == r * cos(theta).  This gives
    the hypotenuse of the projection onto the XY plane, which we will
    call Q. Q == r*sin(theta). Now x / Q == cos(phi) -> x == r *
    sin(theta) * cos(phi) and so on.

    We have deliberately named this function ``sphere2cart`` rather than
    ``sph2cart`` to distinguish it from the Matlab function of that
    name, because the Matlab function uses an unusual convention for the
    angles that we did not want to replicate.  The Matlab function is
    trivial to implement with the formulae given in the Matlab help.
    '''
    sin_theta = np.sin(theta)
    x = r * np.cos(phi) * sin_theta
    y = r * np.sin(phi) * sin_theta
    z = r * np.cos(theta)
    return x, y, z


def cart2sphere(x, y, z):
    ''' Return angles for Cartesian 3D coordinates `x`, `y`, and `z`

    See doc for ``sphere2cart`` for angle conventions and derivation
    of the formulae.

    0 >= `theta` >= pi and 0 >= `phi` >= 2*pi

    Parameters
    ----------
    x : array-like
       x coordinate in Cartesion space
    y : array-like
       y coordinate in Cartesian space
    z : array-like
       z coordinate

    Returns
    -------
    r : array
       radius
    theta : array
       inclination (polar) angle
    phi : array
       azimuth angle
    '''
    r = np.sqrt(x*x + y*y + z*z)
    theta = np.arccos(z/r)
    phi = np.arctan2(y, x)
    return r, theta, phi


def normalized_vector(vec):
    ''' Return vector divided by Euclidean (L2) norm

    See :term:`unit vector` and :term:`Euclidean norm`

    Parameters
    ----------
    vec : array-like shape (3,)

    Returns
    -------
    nvec : array shape (3,)
       vector divided by L2 norm

    Examples
    --------
    >>> vec = [1, 2, 3]
    >>> l2n = np.sqrt(np.dot(vec, vec))
    >>> nvec = normalized_vector(vec)
    >>> np.allclose(np.array(vec) / l2n, nvec)
    True
    >>> vec = np.array([[1, 2, 3]])
    >>> vec.shape
    (1, 3)
    >>> normalized_vector(vec).shape
    (3,)
    '''
    vec = np.asarray(vec).squeeze()
    return vec / math.sqrt((vec**2).sum())


def vector_norm(vec):
    ''' Return vector Euclidaan (L2) norm

    See :term:`unit vector` and :term:`Euclidean norm`

    Parameters
    ----------
    vec : array-like shape (3,)

    Returns
    -------
    norm : scalar

    Examples
    --------
    >>> vec = [1, 2, 3]
    >>> l2n = np.sqrt(np.dot(vec, vec))
    >>> nvec = vector_norm(vec)
    >>> np.allclose(nvec, np.sqrt(np.dot(vec, vec)))
    True
    '''
    vec = np.asarray(vec)
    return math.sqrt((vec**2).sum())
    

def nearest_pos_semi_def(B):
    ''' Least squares positive semi-definite tensor estimation
    
    Reference: Niethammer M, San Jose Estepar R, Bouix S, Shenton M,
    Westin CF.  On diffusion tensor estimation. Conf Proc IEEE Eng Med
    Biol Soc.  2006;1:2622-5. PubMed PMID: 17946125; PubMed Central
    PMCID: PMC2791793.
 
    Parameters
    ----------
    B : (3,3) array-like
       B matrix - symmetric. We do not check the symmetry.
       
    Returns
    -------
    npds : (3,3) array
       Estimated nearest positive semi-definite array to matrix `B`.

    Examples
    --------
    >>> B = np.diag([1, 1, -1])
    >>> nearest_pos_semi_def(B)
    array([[ 0.75,  0.  ,  0.  ],
           [ 0.  ,  0.75,  0.  ],
           [ 0.  ,  0.  ,  0.  ]])
    '''
    B = np.asarray(B)
    vals, vecs = npl.eigh(B)
    # indices of eigenvalues in descending order
    inds = np.argsort(vals)[::-1]
    vals = vals[inds]
    cardneg = np.sum(vals < 0)
    if cardneg == 0:
        return B
    if cardneg == 3:
        return np.zeros((3,3))
    lam1a, lam2a, lam3a = vals
    scalers = np.zeros((3,))
    if cardneg == 2:
        b112 = np.max([0,lam1a+(lam2a+lam3a)/3.])
        scalers[0] = b112
    elif cardneg == 1:
        lam1b=lam1a+0.25*lam3a
        lam2b=lam2a+0.25*lam3a
        if lam1b >= 0 and lam2b >= 0:
            scalers[:2] = lam1b, lam2b
        else: # one of the lam1b, lam2b is < 0
            if lam2b < 0:
                b111=np.max([0,lam1a+(lam2a+lam3a)/3.])
                scalers[0] = b111
            if lam1b < 0:
                b221=np.max([0,lam2a+(lam1a+lam3a)/3.])
                scalers[1] = b221
    # resort the scalers to match the original vecs
    scalers = scalers[np.argsort(inds)]
    return np.dot(vecs, np.dot(np.diag(scalers), vecs.T))

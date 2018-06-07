from numba import jit, guvectorize, float64, int32, float64, b1


#@guvectorize([(float64[:], float64[:], float64[:], float64[:],float64[:], b1[:])], '(),(),(m),(m),(k),()', nopython = True, cache = True, target='parallel')
@jit(nopython=True)#
def point_in_polygon(xArr,yArr, xpts, ypts, bbox, ans):
    """Calculate if coordinates x, y is inside of the polygon described by
    the points array. bbox must be xmin, xmax, ymin, ymax
    """
    for j in range(len(xArr)):
        x = xArr[j]
        y = yArr[j]
        inside = ans[j]
        if (x > bbox[0]) and (x < bbox[1]) and (y > bbox[2]) and (y < bbox[3]):
            "see if inside of polygon"
            n = len(xpts)
            for i in range(n-1):
                px0 = xpts[i]
                py0 = ypts[i]
                px1 = xpts[i+1]
                py1 = ypts[i+1]
                if y > min(py0, py1):
                    if y<= max(py0, py1):
                        if x <= max(px0, px1):
                            if py0 != py1:
                                xinters = (y-py0)*(px1-px0)/(py1-py0)+px0
                                if px0==px1 or x<= xinters:
                                    inside = not inside
        ans[j] = inside

if __name__=='__main__':
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge, Polygon
    from matplotlib.collections import PatchCollection
    # build the test points
    ### SHOULD BE True
    num_points = 200000
    r = np.random.rand(num_points)#*.5
    theta = np.random.rand(num_points)*2*np.pi
    xt = r*np.cos(theta)
    yt = r*np.sin(theta)
    #plt.plot(xt,yt, '.')
    ### SHOULD BE false
    #r = .5*np.random.rand(num_points) + .5
    #theta = np.random.rand(num_points)*2*np.pi
    #xt = np.append(xt,r*np.cos(theta))
    #yt = np.append(yt,r*np.sin(theta))

    theta = np.linspace(0, 2*np.pi, 1000)
    #print(np.sin(theta[0]),np.sin(theta[-1]))
    #print(np.cos(theta[0]),np.cos(theta[-1]))
    r= .4 + .6*np.cos(theta)
    polyX = r*np.cos(theta)
    polyX = np.append(polyX, polyX[0])
    #polyX = np.append(polyX,np.array([0,0]))
    polyY = r*np.sin(theta)
    polyY = np.append(polyY, polyY[0])
    #polyY = np.append(polyY,np.array([0,-.5]))


    #polyX = np.append(polyX,np.append(.5*np.cos(theta), polyX[0]))
    #polyY = np.append(polyY,np.append(.5*np.sin(theta), polyY[0]))

    ans = np.zeros(len(xt), dtype='bool')
    bbox = np.array([polyX.min(), polyX.max(), polyY.min(), polyY.max()])


    point_in_polygon(xt, yt, polyX, polyY,bbox , ans)


    plt.plot(xt[np.invert(ans)],yt[np.invert(ans)], '.')
    plt.plot(xt[ans],yt[ans], '.')
    plt.gca().add_patch(Polygon(np.stack((polyX,polyY), axis=-1), True, fc='w', ec = 'k'))
    print(np.stack((polyX,polyY), axis=-1).shape)
    plt.show()

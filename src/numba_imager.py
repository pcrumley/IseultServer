from numba import jit,guvectorize, float64, uint, b1,uint8, float32
from math import fabs, copysign, log10,sqrt
from numpy import nan, isnan
import numpy as np
from myCmaps import myCmaps
from PIL import Image

class myNumbaImage(object):
    '''A class that will handle the image writing
    '''
    def __init__(self, py, px):
        self.py = py #in pixels
        self.px = px #in pixels

        self.cmap = 'viridis'
        self.norm = 'linear'
        self.clim = [None, None] # The min and max
        self.xlim = [None, None] # Min & Max x value of the image
        self.ylim = [None, None] # Min & Max y value of the final
        self.extent = [None, None, None, None] #(x1, x2, y1, y2) # of the data
        self.zero = 0.0
        self.gamma = 1.0
        self.clipped = True
        self.data = None
        self.griddedData = np.empty((py, px))

    def setData(self, X):
        '''The fields data and the info needed to convert to physical units'''
        self.data = X
        self.imgData = np.empty((self.data.shape[0],self.data.shape[1],4), dtype = 'uint8')
    def setExtent(self, exList):
        self.extent = exList

    def setCmap(self, cmapStr):
        self.cmap = cmapStr
    def setNorm(self, normStr, zero = 0.0, gamma = 1.0, clipped = True):
        self.clipped = True
        if normStr == 'linear' or normStr == 'log':

            self.norm = normStr
        elif normStr == 'pow':
            self.norm = normStr
            self.gamma = gamma
            self.zero = zero

    def resizeImage(self, py, px):
        self.img = np.empy((py,px,4), dtype = 'uint8')

    def set_xlim(self, xmin = None, xmax=None):
        if xmin != None:
            self.xlim[0] = xmin

        if xmax != None:
            self.xlim[1] = xmax
    def set_ylim(self, ymin = None, ymax = None):
        if ymin != None:
            self.ylim[0] = ymin
        if ymax != None:
            self.ylim[1] = ymax
    def set_clim(self, cmin = None, cmax = None):
        if cmin != None:
            self.clim[0] = cmin
        if cmax != None:
            self.clim[1] = cmax

    def renderImage(self):
        '''Render an image from the data'''
        #try:
        # we want to render image that is px by py in size,
        # and corresponds to the data from xlim and ylim.
        cmin = self.data[~np.isnan(self.data)].min() if self.clim[0] is None else self.clim[0]
        cmax = self.data[~np.isnan(self.data)].max() if self.clim[1] is None else self.clim[1]

        xmin = self.xlim[0]
        if xmin is None:
            xmin = self.extent[0]
        xmax = self.xlim[1]
        if xmax is None:
            xmax = self.extent[1]

        ymin = self.ylim[0]
        if ymin is None:
            ymin = self.extent[2]
        ymax = self.ylim[1]
        if ymax is None:
            ymax = self.extent[3]
        # Since we are using nearest neighbor algorithm to resize images we
        # either re-grid the data to the image size then make the image, or
        # we can resize data first then compute the norm, or we can compute
        # norm on entire dataset then resize the image. If we ever implement
        # other interpolations like bicubic/bilinear, whatever, we should
        # always apply the interpolation on the normed image.

        ### TODO --- Implement efficient algorithm where interpolation is
        # performed on the images instead of data.
        """
        if self.griddedData.shape[0] != self.img.shape[0] or self.griddedData.shape[1] != self.img.shape[1]:
            self.griddedData = np.empty([self.img.shape[0], self.img.shape[1]], dtype = 'f8')
        reGridData(self.data, self.griddedData, self.extent, xmin, xmax, ymin, ymax)
        """
        if self.norm =='linear':
            linearNorm(self.data, cmin, cmax, self.clipped, myCmaps[self.cmap], self.imgData)
        if self.norm == 'pow':
            # first we have to calculate some stuff that will be passed to
            # powerNorm for optimizations
            cminNormed = powerNormFunc(cmin, self.zero, self.gamma)
            powNormColorBin = powerNormBin(cmin, cmax, self.zero, self.gamma,myCmaps[self.cmap].shape[0] )
            powerNormImg(self.data,cminNormed, powNormColorBin, self.zero, self.gamma,self.clipped, myCmaps[self.cmap], self.imgData)
        if self.norm == 'log':
            logNorm(self.data,cmin,logNormBin(cmin, cmax, myCmaps[self.cmap].shape[0]), self.clipped, myCmaps[self.cmap], self.imgData)
        #self.img = np.flip(self.img, axis  = 0)
        #print(self.img, self.img)
        self.img = Image.frombytes('RGBA', self.data.shape[::-1],self.imgData).resize((self.px,self.py), Image.BICUBIC)

@guvectorize([(uint8[:],)], # img as RBGA 8 bit array
             '(k)', nopython = True, cache = True, target='parallel')
def makeTransparent(img):
    img[3]=0

@jit(nopython=True, cache =True)
def reGridData(data, target, extent, xmin, xmax, ymin, ymax):
    '''Remake the data the same size as the image array. I think you could
    probably do this in the same step that the norms are applied
    xmin, xmax, ymin, and ymax correspond to the size of the target data.
    extent is the size of the actual data [ x0, x1, y0, y1]'''
    # multipliers that convert and image index to a data index
    '''Remake the data the same size as the image array. I think you could
    probably do this in the same step that the norms are applied
    xmin, xmax, ymin, and ymax correspond to the size of the target data.
    extent is the size of the actual data [ x0, x1, y0, y1]'''
    # multipliers that convert and image index to a data index
    tsizex = xmax-xmin # The x size of the image
    tsizey = ymax-ymin # The y size of the image
    y2diy = (extent[3]-extent[2])/data.shape[0]
    x2dix = (extent[1]-extent[0])/data.shape[1]
    # the output data image is only defined where the original data existed.
    # i.e. between the originally defined extent. We define the
    imin = ((extent[2]-ymin)*target.shape[0])/tsizey
    imax = ((extent[3]-ymin)*target.shape[0])/tsizey
    jmin = ((extent[0]-xmin)*target.shape[1])/tsizex
    jmax = ((extent[1]-xmin)*target.shape[1])/tsizex
    xhelp = (xmin-extent[0])/x2dix
    jhelp = tsizex/target.shape[1]/x2dix
    yhelp = (ymin-extent[2])/y2diy
    ihelp = tsizey/target.shape[0]/y2diy
    target[:,:] =nan
    for i in range(target.shape[0]):
        if i<=imax and  i>=imin:
            idat = round(yhelp-i*ihelp)
            if idat < 0:
                idat = 0
            elif idat >= data.shape[0]:
                idat = data.shape[0]-1
            for j in range(target.shape[1]):
                if j<=jmax and j>=jmin:
                    jdat = round(xhelp+j*jhelp)
                    if jdat <0:
                        jdat = 0
                    elif jdat >= data.shape[1]:
                        jdat=data.shape[1]-1
                    target[i,j] = data[idat,jdat]


@guvectorize([(float64[:], # data
               float64[:], # vmin
               float64[:], # vmax
               b1[:], # clipped
               uint8[:,:], # cmap
               uint8[:], # Data linearly normed to an RBG 8 bit array
               )],
               '(), (), (), (), (n,m),(p)', nopython = True, cache = True, target='parallel')
def linearNorm(data,vmin,vmax, clipped, cmap,img):
    '''This function takes in a data array and returns a linearly
    RGB888 array that can be shown as an image'''
    vmin = vmin[0]
    vmax = vmax[0]
    if vmax<=vmin:
        img[3]=255
        for k in range(3):
            img[k] = cmap[cmap.shape[0]//2,k]
    elif isnan(data[0]):
        img[3] = 0
    else:
        # Don't interpolate colors:
        # we can only create as many colors as are in the colormap
        maxnum = cmap.shape[0]
        databin = ((vmax-vmin)/maxnum)**-1
        # First norm the array
        alpha = 255
        #pxNum = int((data[0]-vmin)*databin)
        pxNum = int((data[0]-vmin)*databin)
        if pxNum <0:
            pxNum =0
            if not clipped[0]:
                alpha = 0
        elif pxNum >= maxnum:
            pxNum = maxnum-1
            if not clipped[0]:
                alpha = 0
        img[3] = alpha
        for k in range(3):
            img[k] = cmap[pxNum, k]


@jit(nopython=True, cache = True)
def powerNormFunc(data, zeropt, gamma):
    if gamma != 0.5:
        return copysign(fabs(data-zeropt)**gamma, data-zeropt)
    else:
        return copysign(sqrt(fabs(data-zeropt)), data-zeropt)
@jit(nopython =True, cache = True)
def powerNormBin(vmin, vmax, zeropt, gamma, maxnum):
    if vmin<vmax:
        return ((powerNormFunc(vmax, zeropt, gamma)-powerNormFunc(vmin, zeropt, gamma))/maxnum)**-1
    else:
        return -1

@guvectorize([(float64[:], # data
               float64[:], # vmin_normed
               float64[:], # databin
               float64[:], # zeropt
               float64[:], # gamma
               b1[:], # clipped
               uint8[:,:], # cmap
               uint8[:], # Data power normed to an RBG 8 bit array
               )],
               '(), (), (),(),(), (),(n,m),(p)', nopython = True, target='parallel', cache = True)
def powerNormImg(data,vmin_normed, databin, zeropt, gamma,clipped, cmap, img):
    '''This function takes in a data array and returns a
    power mapped sign(dat-zeropt)*(dat-zeropt)**-gamma
    RGB888 array that can be shown as an image'''
    zero = zeropt[0]
    gamma = gamma[0]
    maxnum = cmap.shape[0]
    if databin[0]<0:
        img[3] = 255
        for k in range(3):
            img[k] = cmap[cmap.shape[0]//2,k]
    elif isnan(data[0]):
        img[3] = 0
    else:
        # Don't interpolate colors:
        # we can only create as many colors as are in the colormap
        alpha = 255
        pxNum = int((powerNormFunc(data[0], zero, gamma)-vmin_normed[0])*databin[0])
        if pxNum <0:
            pxNum =0
            if not clipped[0]:
                alpha =0
        elif pxNum >= maxnum:
            pxNum = maxnum-1
            if not clipped[0]:
                alpha =0
        img[3] = alpha
        for k in range(3):
            img[k] = cmap[pxNum, k]


@jit(nopython =True, cache = True)
def logNormBin(vmin, vmax, maxnum):
    if vmin<vmax and vmin > 0:
        return (log10(vmax/vmin))/maxnum
    else:
        return -1


@guvectorize([(float64[:], # data
               float64[:], # vmin
               float64[:], # vmax
               b1[:], # clipped
               uint8[:,:], # cmap
               uint8[:], # Data power normed to an RBG 8 bit array])
               )],
               '(),(),(),(),(n,m),(p)', nopython = True, cache = True, target='parallel')
def logNorm(data,vmin,logbin, clipped, cmap, img):
    '''This function takes in a data array and returns a
    power mapped sign(dat-zeropt)*(dat-zeropt)**-gamma
    RGBA888 array that can be shown as an image. vmin and vmax must be>0'''
    vmin = vmin[0]
    if logbin[0] <0:
        # The log norm makes no sense, return a transparent image
        img[3] =0
    elif isnan(data[0]) or data[0]<=0:
        img[3] = 0
    else:
        # Don't interpolate colors:
        # we can only create as many colors as are in the colormap
        maxnum = cmap.shape[0]
        # First norm the array
        alpha = 255
        pxNum = int(log10(data[0]/vmin)//logbin[0])
        if pxNum <0:
            pxNum =0
            if not clipped[0]:
                alpha = 0
        elif pxNum >= maxnum:
            pxNum = maxnum-1
            if not clipped[0]:
                alpha = 0
        img[3] = alpha
        for k in range(3):
            img[k] = cmap[pxNum, k]

if __name__ == "__main__":
    import time
    import numpy as np
    import h5py
    from myCmaps import myCmaps
    import sys
    import io
    from PIL import Image
    import matplotlib.cm as cm

    try:
        with h5py.File(sys.argv[1], 'r') as f:
            Bz = np.array(f['bz'][0,:,:],dtype = 'f8')
    except:
        with h5py.File('output/flds.tot.003', 'r') as f:
            Bz1 = np.array(f['bz'][0,:,:],dtype = 'f8')
        with h5py.File('output/flds.tot.002', 'r') as f:
            Bz2 = np.array(f['bz'][0,:,:],dtype = 'f8')

    #for i in range(3):
    #    Bz = np.append(Bz,Bz, axis = 0)
    #Bz = np.copy(Bz[0:50,0:50])
    #print(Bz.shape)

    im1 = myFieldImage(1000, 1000)

    im1.setData(Bz1)

    im1.setExtent([0,Bz1.shape[1], 0, Bz1.shape[0]])
    #im2 = myFieldImage(1000, 2000)
    #im2.setData(Bz2)
    #im2.setExtent([0,Bz2.shape[1], 0, Bz2.shape[0]])
    #imList = [im1, im2]
    #BzList = [Bz1, Bz2]

    im1.setNorm('pow', zero = 0.0, gamma = 1.0)
    im1.setNorm('linear')#, zero = 0.0, gamma = 1.0)
    im1.setCmap('viridis')
    im1.renderImage()
    def render_png(imgdata):
        #make a pil images
        img = Image.fromarray(imgdata)
        img_io = io.BytesIO()
        img.save(img_io, format='png',compress_level = 0)#, quality=100)
        #img_io.seek(0)
    render_png(im1.img)

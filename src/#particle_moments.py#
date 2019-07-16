from numpy import zeros, nan
from numba import jit
from tristan_sim import TristanSim
from hist_helpers import stepify, eval_clause, parse_boolstr
from numba_imager import myNumbaImage
from point_in_polygon import point_in_polygon
import numpy as np

@jit(nopython = True, cache = True)
def CalcMoments(x1, x2, min1, max1, bnum1):
    x2Average = zeros(bnum1)
    counts = zeros(bnum1)
    b1_w = bnum1/(max1 - min1)
    if (len(x2) == len(x1)) and len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1 - 1
                else:
                    j = (x1[i] - min1) * b1_w
                if j<bnum1:
                    counts[int(j)] += 1
                    x2Average[int(j)] += x2[i]
    counts[counts==0] = 1
    return x2Average/counts

@jit(nopython=True)#
def CalcWeightedMoment(x1, x2, weights, min1, max1, bnum1):
    x2Average = zeros(bnum1)
    counts = zeros(bnum1)
    b1_w = bnum1/(max1 - min1)
    if (len(x2) == len(x1)) and len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1 - 1
                else:
                    j = (x1[i] - min1) * b1_w
                if j<bnum1:
                    counts[int(j)] += weights[i]
                    x2Average[int(j)] += x2[i]
    counts[counts==0] = 1
    return x2Average/counts

@jit(nopython=True)#
def Calc2DMoments(x1, x2, x3, min1, max1, bnum1, min2,max2, bnum2):
    counts= zeros((bnum1, bnum2))
    x3Average = zeros((bnum1, bnum2))
    b1_w = ((max1-min1)/bnum1)**-1
    b2_w =((max2-min2)/bnum2)**-1
    if (len(x1) == len(x2)) and (len(x2) == len(x3)) and len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1-1
                else:
                    j = (x1[i]-min1)*b1_w
                if j<bnum1:
                    if x2[i]>=min2:
                        if x2[i]==max2:
                            k =bnum2-1
                        else:
                            k = (x2[i]-min2)*b2_w
                        if k<bnum2:
                            counts[int(j),int(k)] += 1.0
                            x3Average[int(j),int(k)] += x3[i]
    #counts[counts==0] = 1
    for i in range(bnum1):
        for j in range(bnum2):
            if counts[int(i),int(j)]==0:
                counts[int(i),int(j)] = np.nan
    return x3Average/counts

@jit(nopython=True)#
def Calc2DWeightedMoments(x1, x2, x3, weights, min1, max1, bnum1, min2,max2, bnum2):
    counts= zeros((bnum1, bnum2))
    x3Average = zeros((bnum1, bnum2))
    b1_w = ((max1-min1)/bnum1)**-1
    b2_w =((max2-min2)/bnum2)**-1
    if (len(x1) ==len(x2)) and (len(x1) ==len(weights)) and (len(x1) ==len(x3)) and len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1-1
                else:
                    j = (x1[i]-min1)*b1_w
                if j<bnum1:
                    if x2[i]>=min2:
                        if x2[i]==max2:
                            k =bnum2-1
                        else:
                            k = (x2[i]-min2)*b2_w
                        if k<bnum2:
                            x3Average[int(j),int(k)] += x3[i]
                            counts[int(j),int(k)] += weights[i]
    for i in range(bnum1):
        for j in range(bnum2):
            if counts[int(i),int(j)]==0:
                counts[int(i),int(j)] = np.nan
    return x3Average/counts

def make_1d_moments(outdir = '', sim_type = 'tristan-mp', n='1', prtl_type='',
                 xval='', yval = '', weights = '', boolstr = '', xbins ='200', xvalmin = '',
                 xvalmax = '', xtra_stride = '1', xscale = 'linear',
                selPolyXval = '', selPolyYval = '', selPolyXarr = '', selPolyYarr= ''):
    '''We calculate a 1D average of yval as a function of xval at outdir,
    and then return a list of dictionaries
    where each dictinary is  of the form
    {'num': the number count,
    'x0': left edge of the bin,
    'x1': right edge of the bin}.'''
    ### first we open up a tristan sim
    if sim_type =='tristan-mp':
        cur_sim = TristanSim(outdir, n = int(n), xtra_stride = int(xtra_stride))

    # first we evaluate the boolean string to see what values we should discard:
    bool_arr = parse_boolstr(boolstr, cur_sim, prtl_type)

    # Now we go through an fill out some of the unfilled data needed to make
    # take an average

    xarr = getattr(getattr(cur_sim, prtl_type), xval)
    xarr = xarr if bool_arr is None else xarr[bool_arr]

    yarr = getattr(getattr(cur_sim, prtl_type), yval)
    yarr = yarr if bool_arr is None else yarr[bool_arr]

    warr = np.array([])
    if len(weights) != 0:
        warr = getattr(getattr(cur_sim, prtl_type), weights)
        warr = warr if bool_arr is None else warr[bool_arr]

    # NOW WE APPLY THE POLYGON:
    if (len(selPolyXval) != 0):
        inside = np.zeros(len(xarr), dtype='bool')
        datX = getattr(getattr(cur_sim, prtl_type), selPolyXval)
        datX = datX if bool_arr is None else datX[bool_arr]
        datY = getattr(getattr(cur_sim, prtl_type), selPolyYval)
        datY = datY if bool_arr is None else datY[bool_arr]

        polyX = np.fromstring(selPolyXarr, sep=',')
        polyY = np.fromstring(selPolyYarr, sep=',')
        bbox = np.array([polyX.min(), polyX.max(), polyY.min(), polyY.max()])
        point_in_polygon(datX, datY, polyX, polyY, bbox, inside)
        xarr = xarr[inside]
        yarr = yarr[inside]
        if (len(warr) != 0):
            warr = warr[inside]

    xvalmin = xarr.min() if len(xvalmin)==0 else float(xvalmin)
    xvalmax = xarr.max() if len(xvalmax)==0 else float(xvalmax)

    if len(warr)==0:
        if xscale =='log' and xvalmin > 0:
            hist = CalcMoments(np.log10(xarr), yarr, np.log10(xvalmin), np.log10(xvalmax), int(float(xbins)))
        else:
            hist = CalcMoments(xarr, yarr, xvalmin, xvalmax, int(float(xbins)))
    else:
        #calculate unweighed histogram
        if xscale =='log' and xvalmin > 0:
            hist = CalcWeightedMoment(np.log10(xarr), yarr, warr, np.log10(xvalmin), np.log10(xvalmax), int(float(xbins)))
        else:
            hist = CalcWeightedMoment(xarr, yarr, warr, xvalmin, xvalmax, int(float(xbins)))
    ####
    #
    # Now we have the histogram, we need to turn it into a JSON compatible with
    # D3 hist function. D3 hist return a sorted array that keeps all of the particle
    # data. That is not possible in our case due to memory constraints. Instead we
    # simply return a list
    #
    ###

    if xscale =='log' and xvalmin >0:
        bin_width = (np.log10(xvalmax)-np.log10(xvalmin))/int(xbins)
        bins = np.logspace(np.log10(xvalmin), np.log10(xvalmax), num = int(xbins)+1)
    else:
        bin_width = (xvalmax-xvalmin)/int(xbins)
        bins = np.linspace(xvalmin, xvalmax, num = int(xbins)+1)

    x_arr, y_arr = stepify(bins, hist)
    mom1D = [{'y': y_arr[i],
           'x': x_arr[i]} for i in range(len(x_arr))]
    return {
        'lineData': mom1D,
        'xscale': 'log' if xscale =='log' and xvalmin >0 else 'linear',
        'xmin': mom1D[0]['x'],
        'xmax': mom1D[-1]['x'],
        'vmin': np.min(hist),
        'vmax': np.max(hist)
        }

def make_2d_mom_img(outdir = '', sim_type = 'tristan-mp', n='1', prtl_type='',
                    yval='', xval='', mval='', weights = '', boolstr = '', ybins = '200',
                    xbins ='200', yvalmin='', yvalmax='', xvalmin = '',
                    xvalmax = '', normhist = 'true',cmap='viridis', cnorm = 'log',
                    pow_zero = '0', pow_gamma='1.0', vmin = '', clip = 'true',
                    vmax = '', xmin='', xmax ='', ymin='', ymax='', interpolation = 'bicubic',
                    px ='400', py='400', aspect='auto', mask_zeros='true', xtra_stride = '1',
                    selPolyXval= '', selPolyYval='', selPolyXarr='', selPolyYarr=''):
    # First we calculate the histogram, then we turn it into an image and return
    # the image as a bytesIO
    ### first we open up a tristan sim
    if sim_type =='tristan-mp':
        cur_sim = TristanSim(outdir, n = int(n), xtra_stride = int(xtra_stride))

    # first we evaluate the boolean string to see what values we should discard:
    bool_arr = parse_boolstr(boolstr, cur_sim, prtl_type)
    # Now we go through an fill out some of the unfilled data needed to make
    # a histogram

    xarr = getattr(getattr(cur_sim, prtl_type), xval)
    xarr = xarr if bool_arr is None else xarr[bool_arr]

    yarr = getattr(getattr(cur_sim, prtl_type), yval)
    yarr = yarr if bool_arr is None else yarr[bool_arr]

    marr = getattr(getattr(cur_sim, prtl_type), mval)
    marr = marr if bool_arr is None else marr[bool_arr]


    warr = np.array([])
    if len(weights) != 0:
        warr = getattr(getattr(cur_sim, prtl_type), weights)
        warr = warr if bool_arr is None else warr[bool_arr]

    # NOW WE APPLY THE POLYGON:
    if (len(selPolyXval) != 0):
        inside = np.zeros(len(xarr), dtype='bool')
        datX = getattr(getattr(cur_sim, prtl_type), selPolyXval)
        datX = datX if bool_arr is None else datX[bool_arr]
        datY = getattr(getattr(cur_sim, prtl_type), selPolyYval)
        datY = datY if bool_arr is None else datY[bool_arr]

        polyX = np.fromstring(selPolyXarr, sep=',')
        polyY = np.fromstring(selPolyYarr, sep=',')
        bbox = np.array([polyX.min(), polyX.max(), polyY.min(), polyY.max()])
        point_in_polygon(datX, datY, polyX, polyY, bbox, inside)
        xarr = xarr[inside]
        yarr = yarr[inside]
        marr = marr[inside]
        if (len(warr) != 0):
            warr = warr[inside]

    yvalmin = yarr.min() if len(yvalmin)==0 else float(yvalmin)
    yvalmax = yarr.max() if len(yvalmax)==0 else float(yvalmax)
    xvalmin = xarr.min() if len(xvalmin)==0 else float(xvalmin)
    xvalmax = xarr.max() if len(xvalmax)==0 else float(xvalmax)

    if len(warr)==0:
        hist = Calc2DMoments(yarr, xarr, marr, yvalmin, yvalmax, int(float(ybins)), xvalmin, xvalmax, int(float(xbins)))
    else:
        #calculate unweighed histogram
        hist = Calc2DWeightedMoments(yarr, xarr, marr, warr, yvalmin, yvalmax, int(float(ybins)), xvalmin, xvalmax, int(float(xbins)))

    ####
    #
    # Now we have the histogram, we need to turn it into an image
    #
    ###
    hist_img = myNumbaImage(int(py), int(px))
    hist_img.setInterpolation(interpolation)
    hist_img.setData(hist)
    hist_img.setExtent([xvalmin,xvalmax,yvalmin, yvalmax])
    hist_img.set_xlim(xmin = None if len(xmin)==0 else float(xmin),
                      xmax = None if len(xmax)==0 else float(xmax))
    hist_img.set_ylim(ymin = None if len(ymin)==0 else float(ymin),
                      ymax = None if len(ymax)==0 else float(ymax))
    if cnorm =='log':
        hist_img.setNorm('log', clipped = True if clip =='true' else False)
    if cnorm =='linear':
        hist_img.setNorm('linear', clipped = True if clip =='true' else False)
    if cnorm =='pow':
        hist_img.setNorm('pow',zero = float(pow_zero), gamma = float(pow_gamma), clipped = True if clip =='true' else False)
    hist_img.setCmap(cmap)
    hist_img.set_clim(cmin = None if len(vmin) ==0 else float(vmin), cmax = None if len(vmax)==0 else float(vmax))
    hist_img.set_aspect(0 if aspect=='auto' else 1)
    #hist_img.set_aspect(1)# if aspect=='auto' else 1)
    return hist_img.renderImageDict()


'''
if __name__=='__main__':
    import numpy as np
    from tristan_sim import TristanSim
    mySim = TristanSim('../test_output')
    print(np.all(np.where(parse_boolstr('[x.gt.20.0]AND[x.lt.30]',mySim,'ions'))[0] ==np.where(parse_boolstr('[x.gt.20]AND[x.lt.30]',mySim,'ions'))[0]))
    print(mySim.ions.quantities)
'''

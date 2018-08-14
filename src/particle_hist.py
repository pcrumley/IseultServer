from numpy import zeros, nan
from numba import jit, guvectorize, float64, int32, float64, b1
from math import sqrt, log10
from tristan_sim import TristanSim
from numba_imager import myNumbaImage
from point_in_polygon import point_in_polygon
import numpy as np
#import os
#os.environ['NUMBA_WARNINGS'] = '1'
### SOME STUFF FOR THE NUMBA HIST


@jit(nopython=True)#
def FastHist(x1, min1, max1, bnum1):
    hist= zeros(bnum1)
    b1_w = ((max1-min1)/bnum1)**-1
    if len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1-1
                else:
                    j = (x1[i]-min1)*b1_w
                if j<bnum1:
                    hist[int(j)] += 1
    return hist
@jit(nopython=True)#
def FastWeightedHist(x1, weights, min1, max1, bnum1):
    hist= zeros(bnum1)
    b1_w = ((max1-min1)/bnum1)**-1
    if len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1-1
                else:
                    j = (x1[i]-min1)*b1_w
                if j<bnum1:
                    hist[int(j)] += weights[j]
    return hist

@jit(nopython=True)#
def Fast2DHist(x1, x2, min1, max1, bnum1, min2,max2, bnum2):
    hist= zeros((bnum1, bnum2))
    b1_w = ((max1-min1)/bnum1)**-1
    b2_w =((max2-min2)/bnum2)**-1
    if (len(x1)== len(x2)) and len(x1)>0:
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
                            hist[int(j),int(k)] += 1
    return hist
@jit(nopython=True)#
def Fast2DWeightedHist(x1, x2, weights, min1, max1, bnum1, min2,max2, bnum2):
    hist= zeros((bnum1, bnum2))
    b1_w = ((max1-min1)/bnum1)**-1
    b2_w =((max2-min2)/bnum2)**-1
    if (len(x1) ==len(x2)) and (len(x1) ==len(weights)) and len(x1)>0:
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
                            hist[int(j),int(k)] += weights[i]
    return hist
def eval_clause(clause, sim, prtl_type):
        '''This will parse and return a boolean clause to be applied to the
        particle simulation. The clause must be like "x.gt.29.9". Accepted
        inputs inside the parentheses are any key inside of the
        sim.prtl_type.avail_quantities(). Available comparisions are
        .le. .lt. .eq. .neq. .ge. .gt.'''
    #try:
        tmplist = clause.split('.')
        left_dat = []
        if tmplist[0] in getattr(sim,prtl_type).quantities:
            left_dat = getattr(getattr(sim,prtl_type),tmplist[0])

        right_num = float(tmplist[2]+'.'+tmplist[3]) if len(tmplist) ==4 else float(tmplist[2])
        if tmplist[1] == 'le':
            return left_dat <= right_num
        elif tmplist[1] == 'lt':
            return left_dat < right_num
        elif tmplist[1] == 'eq':
            return left_dat == right_num
        elif tmplist[1] == 'neq':
            return left_dat != right_num
        elif tmplist[1] == 'ge':
            return left_dat >= right_num
        elif tmplist[1] == 'gt':
            return left_dat > right_num
        else:
            return

def parse_boolstr(boolstr, sim, prtl_type):
    '''This will parse and return a boolean array to be applied to the particle
    simulation. The boolstring must be of the form [clause], [clause]AND[clause].
    or [clause]OR[clause]. Right now we don't support more than 2 clauses.
    A better parser could handle something like "[[clause1]OR[clause2]]AND[clause3]"
    TODO---implement better parser.'''
    if boolstr=='':
        return
    else:
        i = 0
        while i<len(boolstr) and boolstr[i] != ']':
            i += 1
        if i== len(boolstr)-1:
            if boolstr[i]==']':
                return eval_clause(boolstr[1:i],sim,prtl_type)
            else:
                return
        elif boolstr[i+1:i+4] =='AND':
            return eval_clause(boolstr[1:i],sim,prtl_type)*parse_boolstr(boolstr[i+4:], sim,prtl_type)
        elif boolstr[i+1:3] == 'OR':
            return eval_clause(boolstr[1:i],sim,prtl_type)+parse_boolstr(boolstr[i+3:], sim,prtl_type)
        else:
            return

def make_1d_hist(outdir = '', sim_type = 'tristan-mp', n='1', prtl_type='',
                 xval='', weights = '', boolstr = '', xbins ='200', xvalmin = '',
                 xvalmax = '', xtra_stride = '1',
                selPolyXval = '', selPolyYval = '', selPolyXarr = '', selPolyYarr= ''):
    '''We calculate a 1D histogram at outdir, and then return a list of dictionaries
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
    # a histogram
    if bool_arr is None:
        xarr = getattr(getattr(cur_sim, prtl_type), xval)
        if len(weights)!=0:
            warr = getattr(getattr(cur_sim, prtl_type), weights)
        else:
            warr = np.array([])
    else:
        xarr = getattr(getattr(cur_sim, prtl_type), xval)[bool_arr]
        if len(weights)!=0:
            warr = getattr(getattr(cur_sim, prtl_type), weights)[bool_arr]
        else:
            warr = np.array([])

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

    xvalmin = xarr.min() if len(xvalmin)==0 else float(xvalmin)
    xvalmax = xarr.max() if len(xvalmax)==0 else float(xvalmax)

    if len(warr)==0:
        hist = FastHist(xarr, xvalmin, xvalmax, int(float(xbins)))

    else:
        #calculate unweighed histogram
        hist = FastWeightedHist(xarr, warr, xvalmin, xvalmax, int(float(xbins)))

    ####
    #
    # Now we have the histogram, we need to turn it into a JSON compatible with
    # D3 hist function. D3 hist return a sorted array that keeps all of the particle
    # data. That is not possible in our case due to memory constraints. Instead we
    # simply return a list
    #
    ###


    bin_width = (xvalmax-xvalmin)/int(xbins)
    hist1D = [{'num': hist[i],
               'x0': bin_width*i,
               'x1':bin_width*(i+1)} for i in range(len(hist))]

    return hist1D

def make_2d_hist_img(outdir = '', sim_type = 'tristan-mp', n='1', prtl_type='',
                    yval='', xval='', weights = '', boolstr = '', ybins = '200',
                    xbins ='200', yvalmin='', yvalmax='', xvalmin = '',
                    xvalmax = '', normhist = 'true',cmap='viridis', cnorm = 'log',
                    pow_zero = '0', pow_gamma='1.0', vmin = '', clip = 'true',
                    vmax = '', xmin='', xmax ='', ymin='', ymax='', interpolation = 'bicubic',
                    px ='400', py='400', aspect='auto', mask_zeros='true', xtra_stride = '1',
                    selPolyXval= '', selPolyYval='', selPolyXarr='', selPolyYarr=''):
    '''First we calculate the histogram, then we turn it into an image and return
    the image as a bytesIO'''
    ### first we open up a tristan sim
    if sim_type =='tristan-mp':
        cur_sim = TristanSim(outdir, n = int(n), xtra_stride = int(xtra_stride))

    # first we evaluate the boolean string to see what values we should discard:
    bool_arr = parse_boolstr(boolstr, cur_sim, prtl_type)
    # Now we go through an fill out some of the unfilled data needed to make
    # a histogram
    if bool_arr is None:
        yarr = getattr(getattr(cur_sim, prtl_type), yval)
        xarr = getattr(getattr(cur_sim, prtl_type), xval)

        if len(weights)!=0:
            warr = getattr(getattr(cur_sim, prtl_type), weights)
        else:
            warr = np.array([])
    else:
        yarr = getattr(getattr(cur_sim, prtl_type), yval)[bool_arr]
        xarr = getattr(getattr(cur_sim, prtl_type), xval)[bool_arr]
        if len(weights)!=0:
            warr = getattr(getattr(cur_sim, prtl_type), weights)[bool_arr]
        else:
            warr = np.array([])

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

    yvalmin = yarr.min() if len(yvalmin)==0 else float(yvalmin)
    yvalmax = yarr.max() if len(yvalmax)==0 else float(yvalmax)
    xvalmin = xarr.min() if len(xvalmin)==0 else float(xvalmin)
    xvalmax = xarr.max() if len(xvalmax)==0 else float(xvalmax)

    if len(warr)==0:
        hist = Fast2DHist(yarr, xarr, yvalmin, yvalmax, int(float(ybins)), xvalmin, xvalmax, int(float(xbins)))
    else:
        #calculate unweighed histogram
        hist = Fast2DWeightedHist(yarr, xarr, warr, yvalmin, yvalmax, int(float(ybins)), xvalmin, xvalmax, int(float(xbins)))

    ####
    #
    # Now we have the histogram, we need to turn it into an image
    #
    ###
    if normhist == 'true' and hist.max() != 0:
        hist *= hist.max()**-1
    if mask_zeros =='true':
        hist[hist==0] = np.nan
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



if __name__=='__main__':
    import numpy as np
    from tristan_sim import TristanSim
    mySim = TristanSim('../test_output')
    print(np.all(np.where(parse_boolstr('[x.gt.20.0]AND[x.lt.30]',mySim,'ions'))[0] ==np.where(parse_boolstr('[x.gt.20]AND[x.lt.30]',mySim,'ions'))[0]))
    print(mySim.ions.quantities)

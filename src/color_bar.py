from numba_imager import myNumbaImage
import numpy as np

def make_color_bar(cmap='viridis', cnorm = 'log',
                       pow_zero = '0', pow_gamma='1.0',
                       vmin = '0', vmax = '1',
                       clip = 'true', interpolation = 'bicubic',
                       px ='30', py='400', alignment='vertical'):
    '''First we calculate the histogram, then we turn it into an image and return
    the image as a bytesIO'''

    gradient =  np.linspace(float(vmin), float(vmax), 512)# A way to make the colorbar display better
    gradient = np.vstack((gradient, gradient))
    if alignment == 'vertical':
        gradient = np.transpose(gradient)
    color_bar = myNumbaImage(int(py), int(px))
    color_bar.setInterpolation(interpolation)
    color_bar.setData(gradient)
    color_bar.setExtent([0,1,0,1])
    if cnorm =='pow':
        color_bar.setNorm('pow',zero = float(pow_zero), gamma = float(pow_gamma),clipped = True if clip =='true' else False)
    else:
        color_bar.setNorm('linear',clipped = True if clip =='true' else False)
    color_bar.setCmap(cmap)
    color_bar.set_clim(cmin = float(vmin), cmax = float(vmax))
    color_bar.set_aspect(0)
    return color_bar.renderColorBar()

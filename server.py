from flask import Flask, send_file, request, abort
from test_imager import myFieldImage
import numpy as np
import h5py
from myCmaps import myCmaps
import matplotlib.cm as cm
import sys
import io
from PIL import Image
import time
app = Flask(__name__)

@app.route('/api/imgs/')
def render_image():
    tic = time.time()
    query_dict = {}
    arg = request.args.get('n')
    if arg:
        print(arg)
        fpath = 'output/flds.tot.'+arg.zfill(3)
        with h5py.File(fpath, 'r') as f:
            Bz1 = np.array(f['bz'][0,:,:],dtype = 'f8')

        im1 = myFieldImage(400, 400)
        im1.setData(Bz1)
        im1.setExtent([0,Bz1.shape[1], 0, Bz1.shape[0]])
        im1.setNorm('pow', zero = 0.0, gamma = 1.0)
        im1.setCmap('Blue-Black-Red')
        im1.renderImage()
        img_io = io.BytesIO()
        im1.img.save(img_io, format='png',compress_level = 1)#, quality=100)
        img_io.seek(0)
        toc = time.time()
        print(toc-tic)
        return send_file(img_io, mimetype='image/png')
    abort(404)
if __name__=='__main__':
    app.run(port=8000, debug=True)

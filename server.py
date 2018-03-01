from flask import Flask, send_file, request, abort, jsonify
import sys
sys.path.insert(0, './src/')
from particle_hist import make_2d_hist_img
import io
import h5py
app = Flask(__name__)
"""
@app.route('/api/field/imgs/')
def field_image():

    query_dict = {}
    arg = request.args.get('n')
    if arg:
        print(arg)
        fpath = 'test_output/flds.tot.'+arg.zfill(3)
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
        return send_file(img_io, mimetype='image/png')
        img_io.close()
    abort(404)
"""
@app.route('/api/handshake')
def handshake():
    return jsonify({name:'IseultServer', version: 'alpha'})
@app.route('/api/2dhist/imgs/')
def hist2d_image():

    query_dict = {}
    for key in ['outdir','sim_type','n', 'prtl_type', 'yval', 'xval', 'weights',
                'boolstr', 'ybins', 'xbins', 'yvalmin', 'yvalmax', 'xvalmin',
                'xvalmax', 'normhist','cmap', 'cnorm', 'pow_zero', 'pow_gamma',
                'vmin', 'clip', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax', 'px',
                'py', 'aspect', 'mask_zeros']:
        arg = request.args.get(key)
        if arg:
            query_dict[key] = arg
    img_io = make_2d_hist_img(**query_dict)
    #return send_file(img_io, mimetype='image/png')
    return jsonify({'img':img_io.decode('utf-8')})

    #return jsonify(query_dict)
    abort(404)
if __name__=='__main__':
    app.run(port=5000, debug=True)

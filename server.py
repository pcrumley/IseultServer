from flask import Flask, send_file, request, abort, jsonify, make_response, current_app
import sys, os
sys.path.insert(0, './src/')
from particle_hist import make_2d_hist_img, make_1d_hist
from particle_moments import  make_1d_moments, make_2d_mom_img
from color_bar import make_color_bar
from datetime import timedelta
from open_sim import open_sim
from functools import update_wrapper
import requests

app = Flask(__name__)
"""
def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator
"""

@app.route('/api/handshake')
#@crossdomain(origin='http://localhost:8080')
#@crossdomain(origin='*')
def handshake():
    return jsonify({'name':'IseultServer',
                    'version': 'alpha',
                    'sim_types': ['tristan-mp'],
                    'server_dir': os.path.split(os.path.abspath(os.curdir))[0]})

@app.route('/api/1dhist/')
#@crossdomain(origin='http://localhost:8080')
def hist1d():
    query_dict = {}
    for key in ['outdir','sim_type','n', 'prtl_type', 'xval', 'weights',
                'boolstr',  'xbins', 'xvalmin', 'xscale',
                'xvalmax', 'xtra_stride',
                'selPolyXval', 'selPolyYval', 'selPolyXarr', 'selPolyYarr' ]:
        arg = request.args.get(key)
        if arg:
            query_dict[key] = arg
    responseDict = make_1d_hist(**query_dict)
    #responseDict['i'] = int(request.args.get('i'))
    #responseDict['url'] = request.url
    return jsonify(responseDict)

    #return jsonify(query_dict)
    abort(404)



@app.route('/api/1dmoments/')
#@crossdomain(origin='http://localhost:8080')
def mom1d():
    query_dict = {}
    for key in ['outdir','sim_type','n', 'prtl_type', 'xval', 'yval', 'weights',
                'boolstr',  'xbins', 'xvalmin', 'xscale',
                'xvalmax', 'xtra_stride',
                'selPolyXval', 'selPolyYval', 'selPolyXarr', 'selPolyYarr' ]:
        arg = request.args.get(key)
        if arg:
            query_dict[key] = arg
    responseDict = make_1d_moments(**query_dict)
    #responseDict['i'] = int(request.args.get('i'))
    #responseDict['url'] = request.url
    return jsonify(responseDict)

    #return jsonify(query_dict)
    abort(404)
@app.route('/api/2dhist/imgs/')
#@crossdomain(origin='http://localhost:8080')
#@crossdomain(origin='*')
def hist2d_image():
    query_dict = {}
    for key in ['outdir','sim_type','n', 'prtl_type', 'yval', 'xval', 'weights',
                'boolstr', 'ybins', 'xbins', 'yvalmin', 'yvalmax', 'xvalmin',
                'xvalmax', 'normhist','cmap', 'cnorm', 'pow_zero', 'pow_gamma',
                'vmin', 'clip', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax', 'px',
                'py', 'aspect', 'mask_zeros', 'interpolation', 'xtra_stride',
                'selPolyXval', 'selPolyYval', 'selPolyXarr', 'selPolyYarr']:
        arg = request.args.get(key)
        if arg:
            query_dict[key] = arg
    responseDict = make_2d_hist_img(**query_dict)
    responseDict['i'] = int(request.args.get('i'))
    responseDict['imgX'] = int(request.args.get('px'))
    responseDict['imgY'] = int(request.args.get('py'))
    responseDict['url'] = request.url
    return jsonify(responseDict)

    #return jsonify(query_dict)
    abort(404)

@app.route('/api/2dmom/imgs/')
#@crossdomain(origin='http://localhost:8080')
def mom2d_image():
    query_dict = {}
    for key in ['outdir','sim_type','n', 'prtl_type', 'yval', 'xval', 'mval',
                'weights',
                'boolstr', 'ybins', 'xbins', 'yvalmin', 'yvalmax', 'xvalmin',
                'xvalmax', 'normhist','cmap', 'cnorm', 'pow_zero', 'pow_gamma',
                'vmin', 'clip', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax', 'px',
                'py', 'aspect', 'mask_zeros', 'interpolation', 'xtra_stride',
                'selPolyXval', 'selPolyYval', 'selPolyXarr', 'selPolyYarr']:
        arg = request.args.get(key)
        if arg:
            query_dict[key] = arg
    responseDict = make_2d_mom_img(**query_dict)
    responseDict['i'] = int(request.args.get('i'))
    responseDict['imgX'] = int(request.args.get('px'))
    responseDict['imgY'] = int(request.args.get('py'))
    responseDict['url'] = request.url
    return jsonify(responseDict)

    #return jsonify(query_dict)
    abort(404)
@app.route('/dirs/', defaults={'req_path': ''})
@app.route('/dirs/<path:req_path>')
#@crossdomain(origin='http://localhost:8080')
def dir_listing(req_path):
    BASE_DIR = '/'
    print(req_path)
    # Joining the base and the requested path
    abs_path = os.path.abspath(os.path.join(BASE_DIR, req_path))
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return abort(404)

    dirList = []
    fileList = []
    with os.scandir(abs_path) as it:
        for entry in it:
            if not entry.name.startswith('.') and not entry.name.startswith('_'):
                if entry.is_dir():
                    dirList.append(entry.name)
                elif entry.is_file():
                    fileList.append(entry.name)
    return jsonify({'parentDir': os.path.split(abs_path)[0], 'dirs': dirList, 'files': fileList})

@app.route('/api/colorbar/')
#@crossdomain(origin='http://localhost:8080')
def colorbar_image():
    query_dict = {}
    for key in ['cmap', 'cnorm', 'pow_zero', 'pow_gamma', 'vmin', 'vmax', 'clip',
                'interpolation', 'px', 'py', 'alignment']:
        arg = request.args.get(key)
        if arg:
            query_dict[key] = arg
    responseDict = make_color_bar(**query_dict)
    responseDict['url'] = request.url
    return jsonify(responseDict)


@app.route('/api/openSim/')
def open_simulation():
    query_dict = {}
    responseDict = {}
    for key in ['sim_type', 'outdir']:
        arg = request.args.get(key)
        if arg:
            query_dict[key] = arg
    return jsonify(open_sim(**query_dict))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    print(path)
    if app.debug:
        return requests.get('http://localhost:8080/{}'.format(path)).text
    else:
        return render_template("index.html")

if __name__=='__main__':
    #app.run(ssl_context='adhoc', port=5000, debug=True)
    app.run(port=5080, debug=True)

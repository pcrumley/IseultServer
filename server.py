from flask import Flask, send_file, request, abort, jsonify, make_response, current_app
import sys
sys.path.insert(0, './src/')
from particle_hist import make_2d_hist_img
from color_bar import make_color_bar
from datetime import timedelta
from open_sim import open_sim
from functools import update_wrapper

app = Flask(__name__)

def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
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


@app.route('/api/handshake')
@crossdomain(origin='*')
def handshake():
    return jsonify({'name':'IseultServer',
                    'version': 'alpha',
                    'sim_types': ['tristan-mp']})

@app.route('/api/2dhist/imgs/')
@crossdomain(origin='*')
def hist2d_image():
    query_dict = {}
    for key in ['outdir','sim_type','n', 'prtl_type', 'yval', 'xval', 'weights',
                'boolstr', 'ybins', 'xbins', 'yvalmin', 'yvalmax', 'xvalmin',
                'xvalmax', 'normhist','cmap', 'cnorm', 'pow_zero', 'pow_gamma',
                'vmin', 'clip', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax', 'px',
                'py', 'aspect', 'mask_zeros', 'interpolation', 'xtra_stride']:
        arg = request.args.get(key)
        if arg:
            query_dict[key] = arg
    responseDict = make_2d_hist_img(**query_dict)
    return jsonify(responseDict)

    #return jsonify(query_dict)
    abort(404)

@app.route('/api/colorbar/')
@crossdomain(origin='*')
def colorbar_image():
    query_dict = {}
    for key in ['cmap', 'cnorm', 'pow_zero', 'pow_gamma', 'vmin', 'vmax', 'clip',
                'interpolation', 'px', 'py', 'alignment']:
        arg = request.args.get(key)
        if arg:
            query_dict[key] = arg
    responseDict = make_color_bar(**query_dict)
    return jsonify(responseDict)

    #return jsonify(query_dict)
    abort(404)

@app.route('/api/openSim/')
@crossdomain(origin='*')
def open_simulation():
    query_dict = {}
    responseDict = {}
    for key in ['sim_type', 'outdir']:
        arg = request.args.get(key)
        if arg:
            query_dict[key] = arg
    return jsonify(open_sim(**query_dict))
    abort(404)


if __name__=='__main__':
    app.run(port=5000, debug=True)

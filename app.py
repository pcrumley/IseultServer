from tornado import ioloop, web
import sys
import os
import base64
import json
from io import StringIO
sys.path.insert(0, './src/')
from particle_hist import make_2d_hist_img, make_1d_hist
from particle_moments import  make_1d_moments, make_2d_mom_img
from color_bar import make_color_bar
#from datetime import timedelta
from open_sim import open_sim
#sys.path.append('./python/')

#from gen_png import hdf2png
#from cache import FileCache

my_port = 50502
if len(sys.argv) > 1:
    my_port = sys.argv[1]

settings = {
    "static_path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "static"),
    "autoreload": True,
    # "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    # "login_url": "/login",
    # "xsrf_cookies": True,
}


class ApiHandler(web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def get(self):
        fpath = self.get_argument('path', None)
        fname = self.get_argument('filename', None)
        res = self.get_argument('res', 0)
        self.write(json.dumps({'name':'IseultServer',
                        'version': 'alpha',
                        'sim_types': ['tristan-mp'],
                        'server_dir': os.path.split(os.path.abspath(os.curdir))[0]}))

class HandshakeHandler(web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def get(self):
        self.write(json.dumps({'name':'IseultServer',
                        'version': 'alpha',
                        'sim_types': ['tristan-mp'],
                        'server_dir': os.path.split(os.path.abspath(os.curdir))[0]}))

class Hist1dHandler(web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
    def get(self):
        query_dict = {}

        default_dict = {"outdir":None, "sim_type": 'tristan-mp', "n":'1', "prtl_type":None,
                         "xval":None, "weights": '', "boolstr": '', "xbins":'200',  "xvalmin": '',
                         "xvalmax": '', "xtra_stride": '1', "xscale": 'linear',
                        "selPolyXval": '', "selPolyYval": '', "selPolyXarr": '', "selPolyYarr":''}

        for key, val  in default_dict.items():
            query_dict[key] = self.get_query_argument(key, val)
        responseDict = make_1d_hist(**query_dict)
        self.write(json.dumps(responseDict))

class Hist2dHandler(web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def get(self):
        query_dict = {}
        default_dict = { "outdir":None, "sim_type": 'tristan-mp', "n":'1', "prtl_type":'ions',
                 "xval":'x', "yval":'px', "weights": '', "boolstr": '', "normhist": 'true', "xbins":'200', "ybins":'200',"xvalmin": '',
                 "xvalmax": '', "xtra_stride": '1',
                 "cmap":'viridis', "cnorm":'linear',
                 "pow_zero":'0', "pow_gamma":'1.0', "vmin":'', "clip":True,
                 "vmax":'', "xmin":'', "xmax":'', "ymin":'', "ymax":'', "interpolation":'bicubic',
                 "px":'400', "py":'400', "aspect":'auto', "mask_zeros":True,
                "selPolyXval": '', "selPolyYval": '', "selPolyXarr": '', "selPolyYarr":''}
        for key, val  in default_dict.items():
            query_dict[key] = self.get_query_argument(key, val)
        responseDict = make_2d_hist_img(**query_dict)
        responseDict['i'] = int(self.get_query_argument('i'))
        responseDict['imgX'] = int(self.get_query_argument('px'))
        responseDict['imgY'] = int(self.get_query_argument('py'))
        responseDict['url'] = self.request.full_url()
        self.write(json.dumps(responseDict))



class Mom1dHandler(web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def get(self):
        query_dict = {}
        default_dict = {"outdir":None, "sim_type": 'tristan-mp', "n":'1', "prtl_type":None,
                         "xval":None, "yval":None, "weights": '', "boolstr": '', "xbins":'200', "xvalmin": '',
                         "xvalmax": '', "xtra_stride": '1', "xscale": 'linear',
                        "selPolyXval": '', "selPolyYval": '', "selPolyXarr": '', "selPolyYarr":''}
        for key, val  in default_dict.items():
            query_dict[key] = self.get_query_argument(key, val)
        responseDict = make_1d_moments(**query_dict)
        self.write(json.dumps(responseDict))

class Mom2dHandler(web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
    def get(self):
        query_dict = {}

        default_dict = { "outdir":None, "sim_type": 'tristan-mp', "n":'1', "prtl_type":'ions',
                 "xval":'x', "yval":'y', "mval":'px', "weights": '', "boolstr": '', "xbins":'200', "ybins":'200',"xvalmin": '',
                 "xvalmax": '',"yvalmin": '',
                 "yvalmax": '', "xtra_stride": '1',
                 "cmap":'viridis', "cnorm":'linear',
                 "pow_zero":'0', "pow_gamma":'1.0', "vmin":'', "clip":True,
                 "vmax":'', "xmin":'', "xmax":'', "ymin":'', "ymax":'', "interpolation":'bicubic',
                 "px":'400', "py":'400', "aspect":'auto', "mask_zeros":True,
                "selPolyXval": '', "selPolyYval": '', "selPolyXarr": '', "selPolyYarr":''}


        for key, val  in default_dict.items():

            query_dict[key] = self.get_query_argument(key, val)
        responseDict = make_2d_mom_img(**query_dict)
        responseDict['i'] = int(self.get_query_argument('i'))
        responseDict['imgX'] = int(self.get_query_argument('px'))
        responseDict['imgY'] = int(self.get_query_argument('py'))
        responseDict['url'] = self.request.full_url()
        self.write(json.dumps(responseDict))

class DirHandler(web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
    def get(self):
        print('hi!')
        BASE_DIR = '/'
        #print(self.request.uri)
        my_path = self.get_query_argument("path", "/Users/pcrumley/")
        # Joining the base and the requested path
        abs_path = os.path.abspath(os.path.join(BASE_DIR, my_path))

        # Return 404 if path doesn't exist
        #if not os.path.exists(abs_path):
        #    raise self.HTTPError(400)
        # Check if path is a file and serve
        #if os.path.isfile(abs_path):
        #    raise self.HTTPError(400)

        dirList = []
        fileList = []
        with os.scandir(abs_path) as it:
            for entry in it:
                if not entry.name.startswith('.') and not entry.name.startswith('_'):
                    if entry.is_dir():
                        dirList.append(entry.name)
                    elif entry.is_file():
                        fileList.append(entry.name)
        self.write(json.dumps({'parentDir': os.path.split(abs_path)[0], 'dirs': dirList, 'files': fileList}))

class ColorbarHandler(web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
    def get(self):
        query_dict = {}
        print('COLORBAR!')
        default_dict = { "cmap":'viridis', "cnorm":'linear',
                     "pow_zero":'0', "pow_gamma":'1.0', "vmin":'0', "clip":True,
                     "vmax":'1', "interpolation":'bicubic',
                     "px":'10', "py":'400', "alignment":'vertical'}

        for key, val  in default_dict.items():
            query_dict[key] = self.get_query_argument(key, val)
        responseDict = make_color_bar(**query_dict)

        responseDict['url'] = self.request.full_url()
        self.write(json.dumps(responseDict))

class SimOpenHandler(web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
    def get(self):
        query_dict = {}
        default_dict = {'simType':"tristan-mp", 'outdir': ''}
        for key,val  in default_dict.items():
            query_dict[key] = self.get_query_argument(key, val)

        self.write(json.dumps(open_sim(**query_dict)))
"""
@app.route('/api/openSim/')
@crossdomain(origin='http://localhost:8080')
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
"""
class StaticHandler(web.RequestHandler):
    def get(self):
        fpath = self.get_argument('path', None)
        fname = self.get_argument('filename', None)
        res = self.get_argument('res', 0)
        self.render("index.html",
                    fpath=fpath,
                    fname=fname,
                    port=my_port,
                    render_res=res)


def make_app():
    return web.Application([

        (r"/", StaticHandler),
        (r"/api", ApiHandler),
        (r"/api/handshake", HandshakeHandler),
        (r"/api/1dhist/", Hist1dHandler),
        (r"/api/1dmoments/", Mom1dHandler),
        (r"/api/2dhist/", Hist2dHandler),
        (r"/api/2dmom/", Mom2dHandler),
        (r"/api/dirs/", DirHandler),
        (r"/api/colorbar/", ColorbarHandler),
        (r"/api/openSim/", SimOpenHandler),

        #(r"/vr", VRHandler),
        #(r"/public/(.*)", web.StaticFileHandler, {"path": "./public"}),
      #(r"/img/", ImgHandler),
    ], **settings)

if __name__ == "__main__":
    app = make_app()
    app.listen(my_port)
ioloop.IOLoop.current().start()

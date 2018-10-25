#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
import sys, os
sys.path.insert(0, './src/')
from particle_hist import make_2d_hist_img, make_1d_hist
from particle_moments import  make_1d_moments, make_2d_mom_img
from color_bar import make_color_bar
from datetime import timedelta
from open_sim import open_sim
from functools import update_wrapper

while True:
    #  Wait for next request from client
    msg = socket.recv_json()
    #mJSON = json.loads(msg)

    print(msg)
    #for key in mJSON.keys():
    #   print(key)
    print("Received request: %s" % msg['rType'])
    if (msg['rType'] == 'Handshake'):
        socket.send_json({'name':'IseultServer',
                        'version': 'alpha',
                        'sim_types': ['tristan-mp'],
                        'server_dir': os.path.split(os.path.abspath(os.curdir))[0]})
    elif (msg['rType'] == 'hist1d'):
        query_dict = {}
        for key in ['outdir','sim_type','n', 'prtl_type', 'xval', 'weights',
                'boolstr',  'xbins', 'xvalmin', 'xscale',
                'xvalmax', 'xtra_stride',
                'selPolyXval', 'selPolyYval', 'selPolyXarr', 'selPolyYarr' ]:
            try:
                query_dict[key] = msg['payload'][key]
            except KeyError:
                pass
        responseDict = make_1d_hist(**query_dict)
        socket.send_json(responseDict)

    elif (msg['rType'] == 'mom1d'):
        query_dict = {}
        for key in ['outdir','sim_type','n', 'prtl_type', 'xval', 'yval', 'weights',
                    'boolstr',  'xbins', 'xvalmin', 'xscale',
                    'xvalmax', 'xtra_stride',
                    'selPolyXval', 'selPolyYval', 'selPolyXarr', 'selPolyYarr' ]:
            try:
                query_dict[key] = msg['payload'][key]
            except KeyError:
                pass
        responseDict = make_1d_moments(**query_dict)
        socket.send_json(responseDict)

    elif (msg['rType'] == 'mom1d'):
        query_dict = {}
        for key in ['outdir','sim_type','n', 'prtl_type', 'xval', 'yval', 'weights',
                    'boolstr',  'xbins', 'xvalmin', 'xscale',
                    'xvalmax', 'xtra_stride',
                    'selPolyXval', 'selPolyYval', 'selPolyXarr', 'selPolyYarr' ]:
            try:
                query_dict[key] = msg['payload'][key]
            except KeyError:
                pass
        responseDict = make_1d_moments(**query_dict)
        socket.send_json(responseDict)

    elif (msg['rType'] == 'hist2d'):
        query_dict = {}
        for key in ['outdir','sim_type','n', 'prtl_type', 'yval', 'xval', 'weights',
                    'boolstr', 'ybins', 'xbins', 'yvalmin', 'yvalmax', 'xvalmin',
                    'xvalmax', 'normhist','cmap', 'cnorm', 'pow_zero', 'pow_gamma',
                    'vmin', 'clip', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax', 'px',
                    'py', 'aspect', 'mask_zeros', 'interpolation', 'xtra_stride',
                    'selPolyXval', 'selPolyYval', 'selPolyXarr', 'selPolyYarr']:
            try:
                query_dict[key] = msg['payload'][key]
            except KeyError:
                pass

        responseDict = make_2d_hist_img(**query_dict)
        responseDict['i'] = int(request.args.get('i'))
        responseDict['imgX'] = int(request.args.get('px'))
        responseDict['imgY'] = int(request.args.get('py'))
        responseDict['url'] = request.url
        socket.send_json(responseDict)

    elif (msg['rType'] == 'mom2d'):
        query_dict = {}
        for key in ['outdir','sim_type','n', 'prtl_type', 'yval', 'xval', 'mval',
                    'weights',
                    'boolstr', 'ybins', 'xbins', 'yvalmin', 'yvalmax', 'xvalmin',
                    'xvalmax', 'normhist','cmap', 'cnorm', 'pow_zero', 'pow_gamma',
                    'vmin', 'clip', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax', 'px',
                    'py', 'aspect', 'mask_zeros', 'interpolation', 'xtra_stride',
                    'selPolyXval', 'selPolyYval', 'selPolyXarr', 'selPolyYarr']:
            try:
                query_dict[key] = msg['payload'][key]
            except KeyError:
                pass

        responseDict = make_2d_mom_img(**query_dict)
        responseDict['i'] = int(request.args.get('i'))
        responseDict['imgX'] = int(request.args.get('px'))
        responseDict['imgY'] = int(request.args.get('py'))
        responseDict['url'] = request.url
        socket.send_json(responseDict)

    elif (msg['rType'] == 'dirs'):
        BASE_DIR = '/'
        try:
            req_path = msg['payload']['path']

        except KeyError:
            req_path = ''
            # Joining the base and the requested path
        abs_path = os.path.abspath(os.path.join(BASE_DIR, req_path))
        dirList = []
        fileList = []
        with os.scandir(abs_path) as it:
            for entry in it:
                if not entry.name.startswith('.') and not entry.name.startswith('_'):
                    if entry.is_dir():
                        dirList.append(entry.name)
                    elif entry.is_file():
                        fileList.append(entry.name)
        socket.send_json({'parentDir': os.path.split(abs_path)[0], 'dirs': dirList, 'files': fileList})

    elif (msg['rType'] == 'colorbar'):
        query_dict = {}
        for key in ['cmap', 'cnorm', 'pow_zero', 'pow_gamma', 'vmin', 'vmax', 'clip',
                    'interpolation', 'px', 'py', 'alignment']:
            try:
                query_dict[key] = msg['payload'][key]
            except KeyError:
                pass

        responseDict = make_color_bar(**query_dict)
        responseDict['url'] = request.url
        socket.send_json(responseDict)

    elif (msg['rType'] == 'openSim'):
        query_dict = {}
        responseDict = {}
        for key in ['sim_type', 'outdir']:
            try:
                query_dict[key] = msg['payload'][key]
            except KeyError:
                pass
        socket.send_json(open_sim(**query_dict))
    else:
        #  Send reply back to client
        socket.send(b"World")
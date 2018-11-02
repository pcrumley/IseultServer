#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
import json

context = zmq.Context()
worker = context.socket(zmq.PULL)
worker.bind("tcp://*:5555")
pusher = context.socket(zmq.PUSH)
pusher.bind("tcp://*:5556")
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
    msg = worker.recv_json()
    #mJSON = json.loads(msg)

    print(msg)
    #for key in mJSON.keys():
    #   print(key)
    print("Received request: %s" % msg['rType'])

    if (msg['rType'] == 'Handshake'):
        print(msg)
        pusher.send_json({'rType': msg['rType'],
            'payload': {
                'progName':'IseultServer',
                'version': 'alpha',
                'id': msg['payload']['id'],
                'name': msg['payload']['name'],
                'url': msg['payload']['url'],
                'simTypes': ['tristan-mp'],
                'serverDir': os.path.split(os.path.abspath(os.curdir))[0]}
            })

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
        responseDict['rType'] = 'Handshake'
        pusher.send_json(responseDict)

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
        pusher.send_json(responseDict)

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
        pusher.send_json(responseDict)

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
        responseDict['rType'] = 'hist2d'
        responseDict['i'] = int(msg['payload']['i'])
        responseDict['imgX'] = int(msg['payload']['px'])
        responseDict['imgY'] = int(msg['payload']['py'])
        responseDict['url'] = msg['payload']['url']
        print(responseDict)
        pusher.send_json(responseDict)

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
        pusher.send_json(responseDict)

    elif (msg['rType'] == 'dirs'):
        BASE_DIR = '/'
        try:
            req_path = msg['path']

        except KeyError:
            req_path = ''
            # Joining the base and the requested path
        abs_path = os.path.abspath(os.path.join(BASE_DIR, req_path))
        print(abs_path)
        dirList = []
        fileList = []
        with os.scandir(abs_path) as it:
            for entry in it:
                if not entry.name.startswith('.') and not entry.name.startswith('_'):
                    if entry.is_dir():
                        dirList.append(entry.name)
                    elif entry.is_file():
                        fileList.append(entry.name)
        pusher.send_json({
            'rType': 'dirs',
            'payload': {
                'parentDir': os.path.split(abs_path)[0],
                'dirList': dirList,
                'fileList': fileList
                }
            })

    elif (msg['rType'] == 'colorbar'):
        query_dict = {}
        for key in ['cmap', 'cnorm', 'pow_zero', 'pow_gamma', 'vmin', 'vmax', 'clip',
                    'interpolation', 'px', 'py', 'alignment']:
            try:
                query_dict[key] = msg['payload'][key]
            except KeyError:
                pass

        responseDict = make_color_bar(**query_dict)
        responseDict['url'] = msg['payload']['url']
        responseDict['rType'] = 'colorbar'
        print(responseDict)
        pusher.send_json(responseDict)

    elif (msg['rType'] == 'openSim'):
        query_dict = {}
        responseDict = {'payload': {}}
        for key in ['simType', 'outdir']:
            try:
                query_dict[key] = msg['payload']['info'][key]
            except KeyError:
                pass
        responseDict['payload']['data'] = open_sim(**query_dict)
        responseDict['payload']['info'] = msg['payload']['info']
        responseDict['payload']['i'] = len(responseDict['payload']['data']['fileArray']) - 1
        responseDict['payload']['lassos'] = {}
        responseDict['rType'] = 'openSim'
        pusher.send_json(responseDict)
    else:
        #  Send reply back to client
        pusher.send(b"World")

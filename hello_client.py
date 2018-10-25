#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq
import json
context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#  Do 10 requests, waiting each time for a response
sendDict = {"rType": "hist1d",
    'payload': {
        'sim_type':'tristan-mp',
        'outdir':'/Users/crumleyp/Code/IseultServer/test_output/',
        'n':3,
        'i':2,
        'xval':'x',
        'xvalmin':'',
        'xvalmax':'',
        'xbins':50,
        'weights': '',
        'prtl_type':'ions'
        }
    }
print(sendDict['rType'])
for request in range(1):
    print("Sending request %s …" % request)
    socket.send_json(sendDict)
    #  Get the reply.
    message = socket.recv_json()
    print("Received reply %s [ %s ]" % (request, message))

# IseultServer
A flask-based server to accessing particle-in-cell data.

This is a flask server that is a work-in-progress.
The long-term goal is to provide a RESTful api to access simulation data over the internet. 
Current design plans are that it will likely never be secure enough to allow arbitrary access 
to the various clusters where your data may be saved.

You must locally host the server on at each place where you have simulation data you would like to 
access. The server should be only locally hosted with port-forwarding to access from your computer. 
To start the server, clone the git directory to a folder in a location where you have read access 
to simulation data.

To run the server on tigressdata type
```bash
$ module load anaconda3 
$ python server.py
```
This will start a flask server in debug mode on tigressdata port:5000. To access the server from your
local machine, you must use port forwarding. e.g.
```bash
$  ssh -N -f -L localhost:5001:localhost:5000 <USER>@tigressdata.princeton.edu
```
The above code makes it so you can access the IseultServer at localhost:5001.

The python code that provides the RESTful api is located in the ./src/ directory. 
You can easily make new APIs for different simulations using the templates as a starting point.

The data will eventually be visualized with Iseult.js&mdash;a javascript front-end for the server located 
here: http://github.com/pcrumley/Iseultjs The directory is private for now, but I plan on hosting it online 
when it is further along.

Right now, it's not very useful as it is still in heavy development, but you can play around by manually 
editing the urls to handle the calls.

Watch this space!


| Dependencies: |
| ------------ |
| Python 3.6&mdash;http://python.org |
| Flask&mdash;http://flask.pocoo.org/ |
| NumPy&mdash;http://numpy.org |
| Numba&mdash;http://numba.pydata.org/ |
| Pillow&mdash;http://pillow.readthedocs.io/en/3.1.x/installation.html |
| h5py&mdash;http://h5py.org |

These things are in the default anaconda package. If the installation becomes more complicated I will detail it here.

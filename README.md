# IseultServer
A flask-based server to accessing particle-in-cell data.

This is a flask server that is a work-in-progress.
The long-term goal is to provide a RESTful api to access simulation data over the internet. 
Current design plans are that it will likely never be secure enough to allow arbitrary access 
to the various clusters where your data may be saved.

You must locally host the server on at each place where you have simulation data you would like to 
access. The server should be only locally hosted. To start the server, download the git directory
to a folder in a location where you have read access to simulation data.

cd to the directory and type
```bash
$ export FLASK_APP=server.py

```

The python code that provides the RESTful api is located in the ./src/ directory. 
You can easily make new APIs for different simulations using the templates as a starting point.

The data can be visualized with Iseult.js&mdash;a javascript front-end for the server located here: 
http://github.com/pcrumley/Iseultjs

Right now, it's not very useful as it is still in heavy development.

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

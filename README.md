# IseultServer
A zeroMQ messaging server for sending your simulation data.

I am working on making a RESTful api to access simulation data over the internet. Initial plans were to send the data via an XHTML request, but it is difficult to send it from a locally hosted server to a real webpage. I am switching the webpage to an electron-app and have moved IseultServer from Flask to zeroMQ. You should be able to find the flask server here on an ealier commit. I am not planning on maintaining the Flask part of the app. 

Design plan is like this:

IseultServer  <-- JSON/ZeroMQ --> electron node.js <-- electron.IPC --> electron renderer.

You must locally host the python kernel on at each place where you have simulation data you would like to 
access. The server should be only locally hosted with port-forwarding to access from your computer. 
To start the server, clone the git directory to a folder in a location where you have read access 
to simulation data.

To run the server on tigressdata type
```bash
$ module load anaconda3 
$ python zMQ_server.py
```
This will start a python instance that opens a socket on port:5555. To access the server from your
local machine, you must use port forwarding. e.g.
```bash
$  ssh -N -f -L localhost:5001:localhost:5555 pcrumley@tigressdata2.princeton.edu
```
The above code makes it so you can access the IseultServer at localhost:5001.

The python code that provides the RESTful api is located in the ./src/ directory. 
You can easily make new APIs for different simulations using ./src/tristan_sim.py as a starting point.

The data will eventually be visualized with Iseult.js&mdash;a javascript front-end for the server located 
here: http://github.com/pcrumley/IseultJS The directory is private for now, but I plan on hosting it online 
when it is further along.

Right now, it's not very useful as it is still in heavy development, but you can play around by manually 
editing the urls to handle the calls.

Watch this space!

# Installing Dependencies

It is recommended to setup a virtual python environment to keep all the right dependencies. You can either do this with anaconda, or with pip.

## Anaconda

You can create a virtual environment with anaconda using the following command:
```bash
$ conda create -n yourenvname python=3.6 anaconda
$ source activate yourenvname
```
Note this will create a new directory `.conda` in your current directory that contains all the packages necessary for the environment. It is recommended you choose a directory that has reasonable storage quota (many clusters limit the home directory to a very small quota). To install the dependencies, use the following command:
```bash
$ conda install --yes --file requirements.txt
```
Now you should have all the required python packages installed to run the server. To exit from the virtual environment, use
```bash
$ source deactivate
```

## Pip

Anaconda is the easier way to get numba installed on your machine since is include prebuilt binaries for llvmlite. 
If you prefer to use pip, you must first build llvmlite yourself or install it via anaconda. See here for details
http://llvmlite.pydata.org/en/latest/admin-guide/install.html

Then, you need the python package `virtualenv` installed. To create a virtual environment, use the following commands:
```bash
$ virtualenv yourenvname
$ source ./yourenvname/bin/activate
```
Similar to the conda solution, this creates a directory under the current path that contains the necessary package and environment files. To install the dependencies, use:
```bash
$ pip install -r requirements.txt
```
To exit the environment, simply use:
```bash
$ deactivate
```

## todo
Add access to field & spectral quantities.
Make rendering images more efficient by not rendering full image then resizing as is currently done
....

| Dependencies: |
| ------------ |
| Matplotlib &mdash; (just for colormaps) |
| Python 3.6&mdash;http://python.org |
| pyZMQ&mdash;https://github.com/zeromq/pyzmq/ |
| NumPy&mdash;http://numpy.org |
| Numba&mdash;http://numba.pydata.org/ |
| Pillow&mdash;http://pillow.readthedocs.io/en/3.1.x/installation.html |
| h5py&mdash;http://h5py.org |

These things are in the default anaconda package. If the installation becomes more complicated I will detail it here.

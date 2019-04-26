import re, os
import numpy as np
import h5py

class cached_property(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    """
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class Particles(object):
    '''A base object that holds the info of one type of particle in the simulation
    '''
    __prtl_types = []
    def __init__(self, sim, name):
        self.sim = sim
        self.name = name
        self.__prtl_types.append(name)
        self.quantities = []
    def load_saved_quantities(self, key):
        try:
            with h5py.File(os.path.join(self.sim.dir,'prtl.tot.'+self.sim.n),'r') as f:
                return f[key][::self.sim.xtra_stride]
        except IOError:
            return np.array([])


    @classmethod
    def get_prtls(cls):
        return cls.__prtl_types

class Ions(Particles):
    '''The ion subclass'''

    def __init__(self, sim, name='ions'):
        Particles.__init__(self, sim, name)
        self.quantities= ['x','y','z','px','py','pz', 'gamma', 'proc', 'index', 'charge', 'KE']
        # YOU WRITE AS IF LaTeX BUT YOU MUST DOUBLE ESCAPE '\' CHARACTER
        self.axislabels = ['x\\ [c/\\omega_{pe}]', 'y\\ [c/\\omega_{pe}]', 'z \\ [c/\\omega_{pe}]',
                           '\\gamma_i\\beta_{i,x}', '\\gamma_i\\beta_{i,y}', '\\gamma_i\\beta_{i,z}',
                           '\\gamma_i', '\\mathrm{proc_i}','\\mathrm{ind_i}', 'q_i', '\\mathrm{KE}_i \\ [m_i c^2]']

        self.oneDlabels = ['x\\ [c/\\omega_{pe}]', 'y\\ [c/\\omega_{pe}]', 'z \\ [c/\\omega_{pe}]',
                           '\\gamma\\beta_{x}', '\\gamma\\beta_{y}', '\\gamma\\beta_{z}',
                           '\\gamma', '\\mathrm{proc}','\\mathrm{ind}', 'q', '\\mathrm{KE} \\ [m_i c^2]']

        self.histLabel = 'f_i (p)'
    @cached_property
    def x(self):
        return self.load_saved_quantities('xi')/self.sim.comp

    @cached_property
    def y(self):
        return self.load_saved_quantities('yi')/self.sim.comp

    @cached_property
    def z(self):
        return self.load_saved_quantities('zi')/self.sim.comp

    @cached_property
    def px(self):
        return self.load_saved_quantities('ui')

    @cached_property
    def py(self):
        return self.load_saved_quantities('vi')

    @cached_property
    def pz(self):
        return self.load_saved_quantities('wi')

    @cached_property
    def charge(self):
        return self.load_saved_quantities('chi')

    @cached_property
    def gamma(self):
        # an example of a calculated quantity
        #return self.load_saved_quantities('proci')
        return np.sqrt(self.px**2+self.py**2+self.pz**2+1)

    @cached_property
    def KE(self):
        # an example of a calculated quantity could use
        #return self.load_saved_quantities('proce')
        return (self.gamma-1)


    @cached_property
    def proc(self):
        return self.load_saved_quantities('proci')

    @cached_property
    def index(self):
        return self.load_saved_quantities('indi')

class Electrons(Particles):
    '''The electron subclass'''
    def __init__(self, sim, name='electrons'):
        Particles.__init__(self, sim, name)
        self.quantities = ['x','y','z','px','py','pz', 'gamma', 'proc', 'index', 'charge', 'KE']
        # YOU WRITE AS IF LaTeX BUT YOU MUST DOUBLE ESCAPE '\'  CHARACTER
        self.axislabels = ['x\\ [c/\\omega_{pe}]', 'y\\ [c/\\omega_{pe}]', 'z \\ [c/\\omega_{pe}]',
                           '\\gamma_e\\beta_{x,e}', '\\gamma_e\\beta_{y,e}', '\\gamma_e\\beta_{z,e}',
                           '\\gamma_e', '\\mathrm{proc_e}','\\mathrm{ind_e}', 'q_e', '\\mathrm{KE}_e \\ [m_i c^2]']
        self.oneDlabels = ['x\\ [c/\\omega_{pe}]', 'y\\ [c/\\omega_{pe}]', 'z \\ [c/\\omega_{pe}]',
                           '\\gamma\\beta_{x}', '\\gamma\\beta_{y}', '\\gamma\\beta_{z}',
                           '\\gamma', '\\mathrm{proc}','\\mathrm{ind}', 'q', '\\mathrm{KE} \\ [m_i c^2]']

        self.histLabel = 'f_e (p)'
    @cached_property
    def x(self):
        return self.load_saved_quantities('xe')/self.sim.comp

    @cached_property
    def y(self):
        return self.load_saved_quantities('ye')/self.sim.comp

    @cached_property
    def z(self):
        return self.load_saved_quantities('ze')/self.sim.comp

    @cached_property
    def px(self):
        return self.load_saved_quantities('ue')

    @cached_property
    def py(self):
        return self.load_saved_quantities('ve')

    @cached_property
    def pz(self):
        return self.load_saved_quantities('we')

    @cached_property
    def charge(self):
        return self.load_saved_quantities('che')

    @cached_property
    def gamma(self):
        # an example of a calculated quantity could use
        #return self.load_saved_quantities('proce')
        return np.sqrt(self.px**2+self.py**2+self.pz**2+1)

    @cached_property
    def KE(self):
        # an example of a calculated quantity could use
        #return self.load_saved_quantities('proce')
        return (self.gamma-1)*self.sim.me/self.sim.mi

    @cached_property
    def proc(self):
        return self.load_saved_quantities('proce')

    @cached_property
    def index(self):
        return self.load_saved_quantities('inde')


class TristanSim(object):
    '''A object that provides an API to access data from Tristan-mp
    particle-in-cell simulations. The specifics of your simulation should be
    defined as a class that extends this object.'''
    params = ['comp','bphi','btheta',]
    def __init__(self, dirpath=None, n=1, xtra_stride = 1):
        self.dir = str(dirpath)
        self.xtra_stride = xtra_stride

        self.n=str(n).zfill(3)
        ### add the ions
        self.ions = Ions(self, name='ions') # NOTE: the name must match the attritube name
        # e.g. self.ions ===> name ='ions'
        ### add the electrons
        self.electrons = Electrons(self, name='electrons')


    def get_file_nums(self):
        try:
            # create a bunch of regular expressions used to search for files
            f_re = re.compile('flds.tot.*')
            prtl_re = re.compile('prtl.tot.*')
            s_re = re.compile('spect.*')
            param_re = re.compile('param.*')

            # Create a dictionary of all the paths to the files
            self.PathDict = {'Flds': [], 'Prtl': [], 'Param': [], 'Spect': []}
            self.PathDict['Flds']= [item for item in filter(f_re.match, os.listdir(self.dir))]
            self.PathDict['Prtl']= [item for item in filter(prtl_re.match, os.listdir(self.dir))]
            self.PathDict['Spect']= [item for item in filter(s_re.match, os.listdir(self.dir))]
            self.PathDict['Param']= [item for item in filter(param_re.match, os.listdir(self.dir))]

            ### iterate through the Paths and just get the .nnn number
            for key in self.PathDict.keys():
                for i in range(len(self.PathDict[key])):
                    try:
                        self.PathDict[key][i] = int(self.PathDict[key][i].split('.')[-1])
                    except ValueError:
                        self.PathDict[key].pop(i)
                    except IndexError:
                        pass

            ### GET THE NUMBERS THAT HAVE ALL 4 FILES:
            allFour = set(self.PathDict['Param'])
            for key in self.PathDict.keys():
                allFour &= set(self.PathDict[key])
            allFour = sorted(allFour)
            return list(allFour)
        except OSError:
            return []
    def get_avail_prtls(self):
        prtl_obj = {}
        prtl_obj['prtls'] = {}
        for prtl in Particles.get_prtls():
            prtl_obj['prtls'][prtl]= {'quantities': getattr(getattr(self,prtl),'quantities'),
                             'axisLabels': getattr(getattr(self,prtl),'axislabels'),
                             'oneDLabels': getattr(getattr(self,prtl),'oneDlabels'),
                             'histLabel': getattr(getattr(self,prtl),'histLabel')}
        return prtl_obj
    def load_param(self, key):
        try:
            with h5py.File(os.path.join(self.dir,'param.'+self.n),'r') as f:
                return f[key][0]
        except IOError:
            return np.nan

    # SOME SIMULATION WIDE PARAMETERS
    @cached_property
    def comp(self):
        return self.load_param('c_omp')

    @cached_property
    def bphi(self):
        return self.load_param('bphi')

    @cached_property
    def btheta(self):
        return self.load_param('btheta')

    @cached_property
    def sigma(self):
        return self.load_param('sigma')

    @cached_property
    def c(self):
        return self.load_param('c')

    @cached_property
    def delgam(self):
        return self.load_param('delgam')

    @cached_property
    def gamma0(self):
        return self.load_param('gamma0')

    @cached_property
    def istep(self):
        return self.load_param('istep')

    @cached_property
    def me(self):
        return self.load_param('me')

    @cached_property
    def mi(self):
        return self.load_param('mi')

    @cached_property
    def mx(self):
        try:
            with h5py.File(os.path.join(self.dir,'param.'+self.n),'r') as f:
                return f['mx'][:]
        except IOError:
            return np.array([])

    @cached_property
    def mx0(self):
        return self.load_param('mx0')

    @cached_property
    def my(self):
        try:
            with h5py.File(os.path.join(self.dir,'param.'+self.n),'r') as f:
                return f['my'][:]
        except IOError:
            return np.array([])

    @cached_property
    def my0(self):
        return self.load_param('my0')

    @cached_property
    def mz0(self):
        return self.load_param('mz0')

    @cached_property
    def ntimes(self):
        return self.load_param('ntimes')

    @cached_property
    def ppc0(self):
        return self.load_param('ppc0')

    @cached_property
    def qi(self):
        return self.load_param('qi')

    @cached_property
    def sizex(self):
        return self.load_param('sizex')
    @cached_property
    def sizey(self):
        return self.load_param('sizey')

    @cached_property
    def stride(self):
        return self.load_param('stride')

    @cached_property
    def time(self):
        return self.load_param('time')

    @cached_property
    def walloc(self):
        return self.load_param('walloc')

    @cached_property
    def xinject2(self):
        return self.load_param('xinject2')


if __name__=='__main__':
    mySim = TristanSim('../test_output')
    for prtl in Particles.get_prtls():
        print(getattr(getattr(mySim,prtl),'x'))
    #print(mySim.get_avail_prtl_quantities())

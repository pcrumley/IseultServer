from tristan_sim import TristanSim
from myCmaps import myCmaps_names

def open_sim(sim_type ='tristan-mp', outdir = ''):
    if sim_type =='tristan-mp':
        mySim = TristanSim(dirpath=outdir)

    responseDict = mySim.get_avail_prtls()
    responseDict['cmaps']= myCmaps_names
    responseDict['fileArray'] = mySim.get_file_nums()
    return responseDict

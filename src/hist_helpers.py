from numba import jit
from numpy import ones
import numpy as np

def stepify(bins, hist):
    tmp_bin = np.dstack((bins, bins)).flatten() 
    tmp_hist = np.concatenate((np.array([0]),np.dstack((hist, hist)).flatten(), np.array([0])))
    return tmp_bin, tmp_hist

def eval_clause(clause, sim, prtl_type):
        '''This will parse and return a boolean clause to be applied to the
        particle simulation. The clause must be like "x.gt.29.9". Accepted
        inputs inside the parentheses are any key inside of the
        sim.prtl_type.avail_quantities(). Available comparisions are
        .le. .lt. .eq. .neq. .ge. .gt.'''
    #try:
        tmplist = clause.split('.')
        left_dat = []
        if tmplist[0] in getattr(sim,prtl_type).quantities:
            left_dat = getattr(getattr(sim,prtl_type),tmplist[0])

        right_num = float(tmplist[2]+'.'+tmplist[3]) if len(tmplist) ==4 else float(tmplist[2])
        if tmplist[1] == 'le':
            return left_dat <= right_num
        elif tmplist[1] == 'lt':
            return left_dat < right_num
        elif tmplist[1] == 'eq':
            return left_dat == right_num
        elif tmplist[1] == 'neq':
            return left_dat != right_num
        elif tmplist[1] == 'ge':
            return left_dat >= right_num
        elif tmplist[1] == 'gt':
            return left_dat > right_num
        else:
            return

def parse_boolstr(boolstr, sim, prtl_type):
    '''This will parse and return a boolean array to be applied to the particle
    simulation. The boolstring must be of the form [clause], [clause]AND[clause].
    or [clause]OR[clause]. Right now we don't support more than 2 clauses.
    A better parser could handle something like "[[clause1]OR[clause2]]AND[clause3]"
    TODO---implement better parser.'''
    if boolstr=='':
        return
    else:
        i = 0
        while i<len(boolstr) and boolstr[i] != ']':
            i += 1
        if i== len(boolstr)-1:
            if boolstr[i]==']':
                return eval_clause(boolstr[1:i],sim,prtl_type)
            else:
                return
        elif boolstr[i+1:i+4] =='AND':
            return eval_clause(boolstr[1:i],sim,prtl_type)*parse_boolstr(boolstr[i+4:], sim,prtl_type)
        elif boolstr[i+1:3] == 'OR':
            return eval_clause(boolstr[1:i],sim,prtl_type)+parse_boolstr(boolstr[i+3:], sim,prtl_type)
        else:
            return

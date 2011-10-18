#!/usr/bin/env python

'''
Script for extracting "scan tables" from Sardana NeXus files into an tab-separated ASCII tables.
When data from multiple entries are extracted from a file, each table is stored in a different file.
The output files for a given input file are stored in a directory whose name matches the input file name (minus extension)

Usage:
python h52ascii.py <nexusfilename> [<entryname1> [<entryname2>] ...] 

If no entry names are provided, all entries from the given nexus file name will be extracted.

Note: only scalar values are extracted   
'''

import nxs
import sys,os
import numpy


def measurement2ascii(fd, entryname, ofname):
    #read the measurement/point_nb data 
    tmp = "/%s/measurement/point_nb"%entryname
    try:
        fd.openpath(tmp)
    except:
        print 'Cannot open hdf5 path "%s". Skipping.'%tmp
        return False 
    ptnb = fd.getdata()
    fd.closedata()
    #prepare a list with column names and a table made of data "columns" 
    namelist=['point_nb']
    table = [ptnb.copy().flatten()]
    for name,nxclass in fd.entries():
        if name == 'point_nb': continue
        dshape,dtype = fd.getinfo()
        if tuple(dshape) != ptnb.shape: continue #not a scalar (incompatible shape)
        table.append(fd.getdata().flatten())
        namelist.append(name)
    #write the table to a file
    try:
        datfile = open(ofname,'w')
    except:
        print 'Cannot create file "%s". Skipping.'%ofname
        return False
    datfile.write("\t".join(namelist)) #write a header of column names
    datfile.write("\n")
    numpy.savetxt(datfile, numpy.vstack(table).transpose(), delimiter='\t') #write the data table
    datfile.close()
    return True


def main():
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        print "Usage:\npython h52ascii.py <nexusfilename> [<entryname1> [<entryname2>] ...] "
        sys.exit(1)
        #fname = '/home/cpascual/20110228_ccd_tests.h5'
        
    entrynames = sys.argv[2:] 
    
    fd = nxs.open(fname,'r')
    
    if len(entrynames)==0:
        entrynames = [n for n,c in fd.entries() if c=='NXentry']
    
    dirname,ext = os.path.splitext(fname)
    try:
        os.makedirs(dirname)
    except:
        print 'Cannot create dir "%s". Skipping.'%dirname
    
    for ename in entrynames:
        ofname = os.path.join(dirname,"%s.dat"%ename)
        print "Extracting %s:%s to %s"%(fname,ename,ofname)
        measurement2ascii(fd, ename, ofname)
    
    fd.close()


if __name__ == "__main__":
    main()
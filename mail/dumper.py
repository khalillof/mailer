#!/usr/bin/env python3
import sqlite3


def db_dump():

    fname='dump.sql'
    dumpfile = None 
    try:
        with sqlite3.connect('db.sqlite3', uri=True) as con:
            # check db connection
            print('db connected') if con else print('db not connected')    
            
            # write db data to file
            with open(fname, 'w') as f:
                for line in con.iterdump():
                    f.write('%s\n' % line)
                   
        # read db data from file been written in brevious step
        with open(fname, 'r') as dfile:
            dumpfile = dfile.read()
    except Exception as ex:
        print(ex)
        raise
    else:    
        return dumpfile

#print(db_dump())
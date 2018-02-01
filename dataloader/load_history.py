#!/usr/bin/env python

import argparse
import datetime
import pandas
import os
import sys

tickfile_dir = '/Users/brian/sandbox/gdax/tickdata'

def parse_args(cli_args):

    parser = argparse.ArgumentParser(description='GDAX trade data pull')
    
    precision_selection = ['1m', '5m', '15m', '1h', '6h', '1d']
    
    parser.add_argument('-p', action='store', dest='precision', help='time precision',
        choices=precision_selection, default='15m')
        
    args = parser.parse_args()
    fname = tickfile_dir + "/ether-" + args.precision + '.csv'
    args.fname = fname
    
    return args
    
    
def build_ohlc_bars(datafile):
    '''
    Native file is [ time, low, high, open, close, volume ].  Convert to OHLCV
    '''
    df = pandas.read_csv(datafile, header=0, 
        names=['timestamp', 'low', 'high', 'open', 'close', 'volume'], 
        index_col='timestamp')
        
    df.index = pandas.to_datetime((df.index.values*1e9).astype(int))
    
    return df
    
    
if __name__ == '__main__':

    args = parse_args(sys.argv[1:])
    
    df = build_ohlc_bars(args.fname)
   
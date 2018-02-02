#!/usr/bin/env python

import argparse
import datetime
import pandas
import os
import sys

tickfile_dir = '/Users/brian/sandbox/pandacoin/tickdata'
precision_selection = ['1m', '5m', '15m', '1h', '6h', '1d']

def validate_precision(precision):
    '''
    Make sure selected precision is a valid choice.  Error if not.
    '''
    try:
        precision_selection.index(precision)
    except ValueError:
        print("precision must be one of: '1m', '5m', '15m', '1h', '6h', '1d'")

def create_input_file_name(precision):
    
    file_name = tickfile_dir + "/ether-" + precision + ".csv"
    return file_name

def parse_args(cli_args):
    '''
    Input: CLI args
    Output: object with attribute fname (file name)
    '''
    parser = argparse.ArgumentParser(description='GDAX trade data pull')
    parser.add_argument('-p', action='store', dest='precision', help='time precision',
        choices=precision_selection, default='15m')
    args = parser.parse_args()

    validate_precision(args.precision)

    args.fname = create_input_file_name(args.precision)
    
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

def load_gdax_bars(precision):
    '''
    Load ETH price data based upon requested time precision.  Return a pandas dataframe of data.
    '''
    validate_precision(precision)
    fname = create_input_file_name(precision)
    df = build_ohlc_bars(fname)

    return df
    
if __name__ == '__main__':

    args = parse_args(sys.argv[1:])
    fname = create_input_file_name(args.precision)
    df = build_ohlc_bars(args.fname)
   

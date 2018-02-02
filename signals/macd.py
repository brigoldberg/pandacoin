#!/usr/bin/env python

import argparse
import datetime
import os
import pandacoin
import pandas
import sys


class MACD(object):

    def __init__(self, bars, short_window=12, long_window=26):
        self.bars = bars
        self.short_window = short_window
        self.long_window = long_window

    def generate_ma_signals(self):
        '''Return dataframe of signals to go long, short or hold (1, -1 or 0)'''
        self.signals = pandas.DataFrame(index=self.bars.index)
        self.signals['signal'] = 0.0
        
        self.signals['ma_short']= self.bars['close'].rolling(window=self.short_window).mean()
        self.signals['ma_long']= self.bars['close'].rolling(window=self.long_window).mean()



def parse_args(cli_args):

    parser = argparse.ArgumentParser(description='MACD Strategy')
    parser.add_argument('-v', action='store_true', dest='debug', help='verbose output', default=False)
    parser.add_argument('-p', action='store', dest='precision', help='time precision', default='5m')
    parser.add_argument('-s', action='store', dest='ma_short', help='short MA', default=12)
    parser.add_argument('-l', action='store', dest='ma_long', help='long MA', default=26)
    args = parser.parse_args()
    
    return args



if __name__ == '__main__':

    args = parse_args(sys.argv[1:])
    gdax_df = pandacoin.load_gdax_bars(args.precision)
    
    macd = MACD(gdax_df, 12, 26)

    macd.generate_ma_signals()

#!/usr/bin/env python

import argparse
import datetime
import os
import pandas
import sys


class MACD(object):

    def __init__(self, bars, short_window=12, long_window=26):
        self.bars = bars
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self):
        '''Return dataframe of signals to go long, short or hold (1, -1 or 0)'''
        self.signals = pandas.DataFrame(index=self.bars.index)
        self.signals['signal'] = 0.0
        
        self.signals['ma_short']= self.bars['close'].rolling(window=self.short_window).mean()
        self.signals['ma_long']= self.bars['close'].rolling(window=self.long_window).mean()


def build_ohlc_bars(datafile):
    '''
    Native file is [ time, low, high, open, close, volume ].  Convert to OHLCV
    '''
    df = pandas.read_csv(datafile, header=0, 
        names=['timestamp', 'low', 'high', 'open', 'close', 'volume'], 
        index_col='timestamp')
        
    df.index = pandas.to_datetime((df.index.values*1e9).astype(int))
    
    df['ma-12'] = df['close'].rolling(window=12).mean()
    df['ma-26'] = df['close'].rolling(window=26).mean()
    
    return df
    
def plot_price_ma(df):
    pass


if __name__ == '__main__':

    datafile = '/Users/brian/sandbox/gdax/tickdata/ether-5m.csv'

    df = build_ohlc_bars(datafile)
    
    #macd = MACD(df, 12, 26)
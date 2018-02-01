#!/usr/bin/env python

import argparse
import bokeh.io
from bokeh.models import DatetimeTickFormatter
from bokeh.models.markers import Diamond
from bokeh.plotting import figure, output_file, show
import pandas
import os
import sys


class TickPlot(object):

    def __init__(self, args):
    
        self.win_short = 12
        self.win_long = 26
        self.base_dir = '/Users/brian/sandbox/gdax'
    
        self.precision = args.precision
        self.debug = args.debug
        self.draw_plot = args.draw_plot
        self.bars = args.bars
        self.plot_type = args.plot_type
        self.plot_fn = self.get_plot_fn()
        self.tick_df = self.load_tick_file()
        
        self.create_ma()
        self.create_signal()
        if self.draw_plot is True:
            self.plot_data()
    
    def get_plot_fn(self):
        '''Create filename for output file'''
        file_name = 'charts/ether-' + self.precision + '.html'
        
        return os.path.join(self.base_dir, file_name)
        
    def load_tick_file(self):
        '''Load tick data into pandas df'''
        tick_file = os.path.join(self.base_dir, 'tickdata', 'ether-'+self.precision+'.csv')
        df = pandas.read_csv(tick_file, header=0, 
            names=['timestamp', 'low', 'high', 'open', 'close', 'volume'], 
            index_col='timestamp')
        df.index = pandas.to_datetime((df.index.values*1e9).astype(int))
        
        lookback = int("-" + self.bars)
        df = df.iloc[lookback:]
                
        return df
        
    def create_ma(self):
        '''Add moving average columns to dataframe'''
        #self.tick_df['ma-short'] = self.tick_df['close'].rolling(window=self.win_short).mean()
        #self.tick_df['ma-long']  = self.tick_df['close'].rolling(window=self.win_long).mean()
        self.tick_df['ma-short'] = self.tick_df['close'].ewm(span=self.win_short, adjust=False).mean()
        self.tick_df['ma-long']  = self.tick_df['close'].ewm(span=self.win_long, adjust=False).mean()


    def create_signal(self):
        '''
        Signal is created when the short MA starts below the long MA and then goes above the
        long MA.
        '''
        previous_day_short_ma = self.tick_df['ma-short'].shift(2)
        previous_day_long_ma = self.tick_df['ma-long'].shift(2)
        
        self.cross_up = (previous_day_short_ma < self.tick_df['ma-long']) & (self.tick_df['ma-short'] > self.tick_df['ma-long'])
    
    def plot_data(self):
        '''Select line or candle plot for output'''
        if self.plot_type == 'line':
            self.plot_line()
        elif self.plot_type == 'candle':
            self.plot_candle()
    
    def plot_line(self):
        pass
        
    def plot_candle(self):
        '''Create candlestick plot'''
        x = self.tick_df.index
        close = self.tick_df['close']
        ma_short = self.tick_df['ma-short']
        ma_long = self.tick_df['ma-long']

        inc = self.tick_df.close > self.tick_df.open
        dec = self.tick_df.open > self.tick_df.close

        #w = 5*60*600 # half day in ms
        w = 60*600 # half day in ms
        
        candle_width = 0.5
        if self.precision == '1m':
            candle_width = 0.5
        

        TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
        
        p = figure(x_axis_type='datetime', tools=TOOLS, plot_width=2000, plot_height=1000,
            title=("Ether %s" % self.precision))
        
        p.segment(self.tick_df.index, self.tick_df.high, self.tick_df.index, self.tick_df.low, color="black")
        
        p.vbar(self.tick_df.index[inc], w, self.tick_df.open[inc], self.tick_df.close[inc], 
            fill_color="green", line_color="green", line_width=candle_width)
        
        p.vbar(self.tick_df.index[dec], w, self.tick_df.open[dec], self.tick_df.close[dec], 
            fill_color="red", line_color="red", line_width=candle_width)
  
        p.line(x, ma_short, legend="ma-short", line_color="orange", line_width=4)
        p.line(x, ma_long, legend="ma-long", line_color="blue", line_width=4)
        
        circle_x = self.tick_df[self.cross_up == True].index
        circle_y = self.tick_df['ma-short'][self.cross_up == True]
        
        p.diamond(circle_x, circle_y, fill_color="green", line_width=10)

        bokeh.io.output_file(self.plot_fn)
        show(p)

    
def parse_args(cli_args):
    '''
    
    '''
    parser = argparse.ArgumentParser(description="Candlestick plotter")
    
    precision_selection = ['1m', '5m', '15m', '1h', '6h', '1d']
    plot_type = ['candle', 'line']
    
    parser.add_argument('-v', action='store_true', dest='debug', help='verbose output', default=False)
    parser.add_argument('-p', action='store', dest='precision',    help='time precision',
        choices=precision_selection, default='5m')
    parser.add_argument('-b', action='store', dest='bars', help='Tick bars', default='300')
    parser.add_argument('-t', action='store', dest='plot_type', help='plot line type',
        choices=plot_type, default='candle')
    parser.add_argument('-d', action='store_true', dest='draw_plot', help='draw plot', default=False)
    
    args = parser.parse_args()
    
    return args

if __name__ == '__main__':

    args = parse_args(sys.argv[1:])


    myplot = TickPlot(args)
   

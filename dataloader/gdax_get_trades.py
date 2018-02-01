#!/usr/bin/env python

import argparse
import datetime
import gdax
import logging
import pandas
import time
import sys

class DataFetcher(object):

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    tickfile_dir = '/Users/brian/sandbox/gdax/tickdata'

    def __init__(self, args):
        '''
        Create a list of dates.  For each date, create time windows to pass to GDAX.
        Output a CSV file for each day and candlestick type (1m, 5m, etc).
        '''
        self.product_id = 'ETH-USD'
        self.d_start = args.date_start        # datetime
        self.d_end = args.date_end              # datetime
        self.precision = args.precision        # int (seconds)
        self.window_length = 3600            # int (seconds)
        self.debug = args.debug                # boolean T/F
        self.output_file = self.tickfile_dir + '/ether-' + get_precision_name(self.precision) + '.csv'
        
        if self.debug is True:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
            
        self.logger.debug('Product ID: %s' % self.product_id)
        self.logger.debug('Date start: %s' % self.d_start)
        self.logger.debug('Date end: %s' % self.d_end)
        self.logger.debug('Precision: %s' % self.precision)

        # methods
        self.build_date_range()        # Create list of days to get tickdata
        self.build_time_slices()

    def build_date_range(self):
        '''
        Create list of calendar days for price fetching.
        eg:    ['2018-01-15', '2018-01-16', 2018-01-17']
        '''
        self.date_list = pandas.date_range(start=self.d_start, end=self.d_end)
        
        self.logger.debug('Date list: %s' % self.date_list)
        
    def build_time_slices(self):
        '''
        Build list of time periods for GDAX query.
        '''
        self.slices = []
        timeslice = self.date_list[0]

        if self.precision >= 3600:
            #self.window_length = self.precision
            self.window_length = 86400
            
        while timeslice < (self.date_list[-1] + datetime.timedelta(days=1)):
        
            slice_end = timeslice + datetime.timedelta(seconds=self.window_length - 1)
            self.slices.append((timeslice, slice_end))
            self.logger.debug('TimeSlice: %s to %s' % (timeslice, slice_end))
            timeslice = timeslice + datetime.timedelta(seconds=self.window_length)
            
    def get_trades(self):
        '''
        Use GDAX to fetch price data for each time slice.
        '''
        
        public_client = gdax.PublicClient()
        fh = open(self.output_file, 'w')
        
        for slice in self.slices:
            gdax_data = public_client.get_product_historic_rates('ETH-USD', 
                    start=slice[0], end=slice[1], granularity=self.precision)
            self.logger.debug('API Request: GET /products/%s/candles?start=%s&end=%s&granularity=%s'% 
                (self.product_id, slice[0], slice[1], self.precision))
            time.sleep(1)
            
            for line in reversed(gdax_data):
    
                # timestamp, low, high, open, close, volume
                gdax_tick = ('%s,%s,%s,%s,%s,%s' % (line[0], line[1], line[2], line[3], line[4], line[5]))
                self.logger.debug(gdax_tick)
    
                fh.write('%s\n' % gdax_tick)
                fh.flush()
            
        fh.close()  


def get_precision(precision):
    p_key = {'1m': 60, '5m': 300, '15m': 900, '1h': 3600, '6h':21600, '1d':86400}
    return p_key[precision]
    
def get_precision_name(precision):
    p_key = {60: '1m', 300: '5m', 900: '15m', 3600: '1h', 21600: '6h', 86400: '1d'}
    return p_key[precision]

def parse_args(cli_args):
    '''
    Convert date strings to datetime. Convert precision to seconds.
    '''
    parser = argparse.ArgumentParser(description='GDAX data loader')
    
    precision_selection = ['1m', '5m', '15m', '1h', '6h', '1d']
    
    parser.add_argument('-v', action='store_true', dest='debug', help='verbose output', default=False)
    parser.add_argument('-p', action='store', dest='precision',    help='time precision',
        choices=precision_selection, default='1h')
    parser.add_argument('-s', action='store', dest='date_start', help='start date', default='2018-01-01')
    parser.add_argument('-e', action='store', dest='date_end', help='end date', default='2018-01-03')
    
    args = parser.parse_args()
    
    args.date_start = datetime.datetime.strptime(args.date_start, '%Y-%m-%d')
    args.date_end = datetime.datetime.strptime(args.date_end, '%Y-%m-%d')
    args.precision = get_precision(args.precision)
    
    return args
            
if __name__ == '__main__':

    args = parse_args(sys.argv[1:])
    
    dfetch = DataFetcher(args)
    dfetch.get_trades()

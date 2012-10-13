'''
Created on Mar 7, 2011

@author: ludifan
'''
import logging

from numpy import array, concatenate, where, arange, histogram
import numpy.ma as ma
#from scipy.stats.stats import cumfreq

class TimeSerie(object):
    def __init__(self, dates, values):
        self.dates = array(dates, dtype=str)
        self.values = ma.masked_invalid(values)
        # sort values by date
        ind = self.dates.argsort()
        self.dates = self.dates[ind]
        self.values = self.values[ind]
        
        
    def filledValues(self, fill_value=1e20):
        return ma.filled(self.values, fill_value)
        
            
    def removeDates(self, indexToHold):
        self.dates = self.dates[indexToHold]
        self.values = self.values[indexToHold]
        

class TimeSerieCollection(dict):
    def computeStatistics(self):
        dates = []
        values = []
        for ts in self.itervalues():
            dates.append(ts.dates)
            values.append(ts.values)
        dates = concatenate(dates).astype(int)
        values = ma.concatenate(values)
        minDate = dates.min()
        nDates = dates.max() - minDate + 1 
        hist = histogram(dates*(-values.mask), bins=arange(nDates)+minDate)
        values = values.compressed()
        if values.size == 0:
            raise Exception("empty dataset")
        lowend = values.min()*0.99
        highend = values.max()*1.01
        #cumfreqs, lowlim, binsize, extrapoints = cumfreq(values, 40, (lowend, highend))
        #normcumfreqs = cumfreqs/values.size
        #ind = ((normcumfreqs > 0.02) & (normcumfreqs < 0.98)).nonzero()[0]
        #if ind.size == 0:
        #    raise Exception("empty dataset")
        #min = ind[0]*binsize + lowlim
        #max = ind[-1]*binsize + lowlim
        #return min, max, hist
        return values.min(),values.max(),hist

    def clean(self, indexToHold):
        """removes dates in all timeseries"""
        for key,val in self.iteritems():
            val.removeDates(indexToHold)


    @classmethod
    def fromWorldBankData(cls, data):
        res = {}
        for item in data:
            id = item["country"]["id"]
            if not res.has_key(id):
                res[id] = {"date":[], "value":[]}
        for item in data:
            id = item["country"]["id"]
            date = item["date"]
            val = item["value"]
            res[id]["date"].append(date)
            res[id]["value"].append(float(val) if val is not None else float("nan"))
        for (key,val) in res.iteritems():
            res[key] = TimeSerie(val["date"], val["value"])
        return cls(res)

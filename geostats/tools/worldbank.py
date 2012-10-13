'''
Created on Mar 2, 2011

@author: scy
'''
import numpy as np
from urllib2 import urlopen
from data import TimeSerieCollection
import json

#http://api.worldbank.org/countries/AUT/indicators/AG.CON.FERT.MT?per_page=10&date=1960:2011
API_URL = "http://api.worldbank.org"
FEATURED = ["EG.ELC.NUCL.ZS", "SP.RUR.TOTL.ZS", "EN.ATM.CO2E.PC", "SP.DYN.CONU.ZS", "IT.CEL.SETS.P2", "SP.DYN.CBRT.IN", "SH.DYN.AIDS.ZS"]


def jsonFromURL(url):
    sock = urlopen(url, None)
    raw = sock.read()
    sock.close()
    try:
        res = json.loads(raw)
        return res 
    except:
        raise Exception(raw)


class WorldBankAPI():
    def __init__(self):
    	self.preloaded = False
        pass
   
    def dataFromURL(self, url):
        data = jsonFromURL(url)
        page_info = data[0]
        if page_info["total"] == 0:
            # reponse vide
            return None
        res = data[1]
        page = 2
        while (page_info["page"] < page_info["pages"]):
            data = jsonFromURL(url + "&page=%s" % page)
            page_info = data[0]
            res += data[1]
            page += 1
        return res


    def describeIndicator(self, indicator):
        url = "/".join((API_URL, "indicator", indicator)) + "?format=json"
        return self.dataFromURL(url)


    def featuredIndicators(self):
        return [self.describeIndicator(ind)[0] for ind in FEATURED]
            
        
    def countriesForRegion(self, region):
        url = "/".join((API_URL, "countries")) + "?format=json&region=%s" % region
        return self.dataFromURL(url)
    
    
    def getIndicator(self, id="SP.POP.TOTL", dates="1960:2010", countries="all"):
        url = "/".join((API_URL, "countries", countries, "indicators", id)) + "?per_page=500&format=json&date=%s" % dates
        #print url
        return self.dataFromURL(url)
    
    
    def getRegions(self):
        url = "/".join((API_URL, "regions")) + "?format=json"
        return self.dataFromURL(url)
    
    
    def getTopics(self):
        url = "/".join((API_URL, "topics")) + "?format=json"
        return self.dataFromURL(url)
    
    
    def indicatorsForTopic(self, topic):
        url = "/".join((API_URL, "topic", topic, "indicator")) + "?per_page=500&format=json"
        return self.dataFromURL(url)


    def preload(self):
        """WorldBank API preload"""
        if self.preloaded:
            return
        self.WB_TOPICS = self.getTopics()
        self.SELECTED_TOPICS = []
        for ind in [0,4,5,7,8,10,13,14,16,17]:
            self.SELECTED_TOPICS.append(self.WB_TOPICS[ind])
        for top in self.SELECTED_TOPICS:
            top["wb_url"] = "http://data.worldbank.org/topic/" + top["id"]
            top["indicators"] = self.indicatorsForTopic(top["id"])
        
        self.WB_REGIONS = self.getRegions()
        self.SELECTED_REGIONS = []
        for reg in self.WB_REGIONS:
            if reg['code'] in ['ARB','EAS','ECA','EUU', 'LCN','MEA','EMU','SAS','SSF','LDC','OED']:
                self.SELECTED_REGIONS.append(reg)
                
        self.WB_FEATURED = self.featuredIndicators()
        self.preloaded = True




if __name__ == "__main__":
    wb = WorldBankAPI()
    reg = wb.countriesForRegion("EUU")
    codes = []
    for item in reg:
        codes.append(item["id"])
    res = wb.getIndicator(id="SH.STA.WAST.ZS", countries=";".join(codes))
    col = TimeSerieCollection.fromWorldBankData(res)
    (min,max,hist) = col.computeStatistics()
    ind = np.where(hist[0]!=0)
    for key,val in col.iteritems():
        val.removeDates(ind)
    
#    for k in sorted(t[0].iterkeys()):
#        print k, t[0][k].values
#    res = describeIndicator("SP.POP.TOTL")
#    print res[0]
#    reg = getRegions()
#    print reg
#    top = getTopics()
#    print top
#    ind = indicatorsForTopic("5")
#    print ind


# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)

import os
import numpy as np
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.contrib.gis.maps.google.gmap import GoogleMap
from django.contrib.gis.maps.google.overlays import GPolygon
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.core.cache import cache
from json import dumps

#matplotlib config dir
os.environ["MPLCONFIGDIR"] = "/tmp"
from matplotlib.colors import Normalize, rgb2hex
from matplotlib.cm import jet
from tools.data import TimeSerieCollection
from models import Country
from tools.gmap import GMAP_KEY
from tools.worldbank import WorldBankAPI

GMAP_TPL = 'world/google-map-ext.js'

WBAPI = WorldBankAPI()
    
    
def index(request):
    logger.debug("Robert De Niro")
    return HttpResponseRedirect("/world/stats/EUU/EG.ELC.NUCL.ZS")
    
    
def countries(request, region, indicator):
    try:
        WBAPI.preload()
        indic = cache.get(indicator)
        if indic is None:
            indic = WBAPI.describeIndicator(indicator)[0]
            cache.set(indicator, indic)
        reg = cache.get(region)
        if reg is None:
            reg = WBAPI.countriesForRegion(region)
            cache.set(region, reg)
        codes = []
        for item in reg:
            codes.append(item["id"])
        key = ':'.join([region,indicator])
        data = cache.get(key)
        if data is None:
            res = WBAPI.getIndicator(id=indicator, countries=";".join(codes))
            data = TimeSerieCollection.fromWorldBankData(res)
            cache.set(key, data)
        (mini, maxi, histo) = data.computeStatistics()
        keptIndex = np.where(histo[0] != 0)
        data.clean(keptIndex)
    except Exception, error:
        return render_to_response("world/error_page.html", {'error_message':error, \
                                        'reload_url':reverse('world.views.countries', args=(region, indicator)) })
    polys = []
    timeseries = []
    norm = Normalize(mini, maxi)
    #colorbar.create_colorbar(jet, norm)
    for c in Country.objects.filter(iso2__in=data.keys()):
        values = data[c.iso2].filledValues()
        colors = [rgb2hex(jet(norm(val))[0:3]) if val != 1e20 else "#000000" for val in values]
#        print c.iso2, len(c.geom)
#        print [len(p.coords[0]) for p in c.geom]
        for p in c.geom:
            if len(p.coords[0]) < 5:
                continue
            poly = GPolygon(p, stroke_color="#000000", stroke_weight=1, stroke_opacity=0.8, \
                            fill_opacity=0.7, fill_color=colors[0])
            polys.append(poly)
            timeseries.append(dumps(colors))
    
    timesteps = dumps(data[data.keys()[0]].dates.tolist());        
    gmap = GoogleMap(template=GMAP_TPL, key=GMAP_KEY, polygons=polys, 
                     extra_context={'maptype':'G_SATELLITE_MAP',
                                    'timesteps':timesteps, 
                                    'timeseries':timeseries, 
                                    })
    
    histo_values = ",".join([str(val) for val in histo[0][keptIndex]])
    
    for reg in WBAPI.SELECTED_REGIONS:
        reg['url'] = reverse('world.views.countries', args=(reg['code'], indicator))
        if reg['code'] == region:
            wb_region = reg        

    for topic in WBAPI.SELECTED_TOPICS:
        for ind in topic["indicators"]:
            ind["url"] = reverse('world.views.countries', args=(region, ind["id"].strip()))

    for ind in WBAPI.WB_FEATURED:
        ind["url"] = reverse('world.views.countries', args=(region, ind["id"].strip()))

    indic["wb_url"] = "http://data.worldbank.org/indicator/" + indicator
    wb_region["wb_url"] = "http://data.worldbank.org/region/" + wb_region["code"]

    res_dico = {'google':gmap, 
                'steps':len(colors),
                'region':wb_region,
                'regions':WBAPI.SELECTED_REGIONS,
                'topics':WBAPI.SELECTED_TOPICS,
                'featured':WBAPI.WB_FEATURED,
                'indicator':indic,
                'histo_values':histo_values,
                'vmin':mini, 'vmax':maxi }

    return render_to_response("world/world_stats.html", res_dico)


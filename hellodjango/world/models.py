# -*- coding: utf-8 -*-

from django.contrib.gis.db import models

class Country(models.Model):
    id = models.IntegerField(db_column="ogc_fid", primary_key=True)
    geom = models.MultiPolygonField(db_column="wkb_geometry", srid=4326)
    name = models.CharField(db_column="name", max_length=50)
    iso2 = models.CharField(db_column="iso2", max_length=2)
    area = models.IntegerField(db_column="area")
    pop2005 = models.IntegerField(db_column="pop2005")
    objects = models.GeoManager()
    
    class Meta:
        db_table = "world_borders_simpl"
        verbose_name = u"Frontières"



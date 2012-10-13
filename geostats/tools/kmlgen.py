# -*- coding: utf-8 -*-
from genericpath import exists
from monsite.settings import DATA_DIR
import math
import os
import psycopg2

kmldoc = r"""<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
    <Document>
        <Style id="folderStyle">
            <ListStyle>
                <listItemType>checkHideChildren</listItemType>
            </ListStyle>
        </Style>
        %(style)s
        <Folder>
            <name>Fleuve</name>
            <description>Carthage</description>
            <styleUrl>#folderStyle</styleUrl>
            %(placemarks)s
        </Folder>
        %(tour)s
    </Document>
    </kml>
    """

polystyle = r"""<Style id="Surf_Eau_default">
        <LineStyle>
            <color>ffc8c8c8</color>
        </LineStyle>
        <PolyStyle>
            <color>ff960000</color>
        </PolyStyle>
        </Style>
        """

linestyles = r"""<Style id="Cours_Eau_default">
            <LineStyle>
               <color>99800000</color>
               <colorMode>normal</colorMode>      <!-- colorModeEnum: normal or random -->
               <width>5</width>                   <!-- float -->
            </LineStyle>
            </Style>
         <Style id="Cours_Eau_random">
            <LineStyle>
               <colorMode>random</colorMode>      <!-- colorModeEnum: normal or random -->
               <width>3</width>                   <!-- float -->
            </LineStyle>
            </Style>
        <Style id="Confluent">
            <LineStyle>
                <color>99ffff66</color>
                <colorMode>normal</colorMode>      <!-- colorModeEnum: normal or random -->
               <width>3</width>                   <!-- float -->
            </LineStyle>
        </Style>
           """
    
placemark = r"""<Placemark>
        <description>%(desc)s</description>
        <styleUrl>#%(style)s</styleUrl>
        %(geom)s
        </Placemark>
        """

os.environ["CLIENT_ENCODING"] = "UTF8"



tour="""<gx:Tour>
        <name>%(name)s</name>
        <visibility>1</visibility>
        <gx:Playlist>
            %(flyto)s    
        </gx:Playlist>
    </gx:Tour>
    """
    
flyto_cam = """<gx:FlyTo>
            <gx:duration>%(duration)i</gx:duration>
            <gx:flyToMode>smooth</gx:flyToMode>
            <Camera>
                <longitude>%(lon)f</longitude>
                <latitude>%(lat)f</latitude>
                <altitude>%(alt)f</altitude>
                <heading>%(heading)f</heading>
                <tilt>%(tilt)f</tilt>
                <roll>%(roll)f</roll>
                <altitudeMode>clampToGround</altitudeMode>
            </Camera>
        </gx:FlyTo>
        """

flyto_lookat = """<gx:FlyTo>
            <gx:duration>%(duration)i</gx:duration>
            <gx:flyToMode>smooth</gx:flyToMode>
            <LookAt>
                <longitude>%(lon)f</longitude>
                <latitude>%(lat)f</latitude>
                <altitude>%(alt)f</altitude>
                <heading>%(heading)f</heading>
                <tilt>%(tilt)f</tilt>
                <range>%(range)f</range>
                <altitudeMode>clampToGround</altitudeMode>
            </LookAt>
        </gx:FlyTo>
        """
    
def get_troncons(codehydro):
    """liste ordonnée des troncons d'un cours d'eau"""
    con = psycopg2.connect("dbname='eau_france' user='scy' password='titoon'")
    cur = con.cursor()
    cur.execute("select id_bdcarthage_noeud_initial, id_bdcarthage_noeud_final" +
                         " from troncon_hydrographique where code_hydrographique_cours_eau = '%s' order by fpkh" % codehydro)
    res = cur.fetchall()
    con.close()
    return res


def get_noeud_ini_fin(con, code_ini, code_fin):
    cur = con.cursor()
    cur.execute("select asKML(wkb_geometry) from noeud_hydrographique where id_bdcarthage = %s " % code_ini)
    noeud_ini = cur.fetchall() 
    cur.execute("select asKML(wkb_geometry) from noeud_hydrographique where id_bdcarthage = %s " % code_fin)
    noeud_fin = cur.fetchall() 
    res = (noeud_ini[0], noeud_fin[0])
    return res


def get_tour(codehydro):
    resFileName = "/tour_%s.kml" % codehydro
    resPath = DATA_DIR + resFileName
    if (exists(resPath)):
        return resFileName
    pm = get_coursdo_placemarks(codehydro, "Cours_Eau_default")
    pm += get_confluent_placemarks(codehydro)
    tron = get_troncons(codehydro)
    con = psycopg2.connect("dbname='eau_france' user='scy' password='titoon'")
    res = ""
    ini = tron[0][0]
    for elmt in tron[1::5]:
        fin = elmt[1]
        nd = get_noeud_ini_fin(con, ini, fin)
        ini = fin
        (lat,lon, head) = compute_heading(strip_point(nd[0]), strip_point(nd[1]))
        res += flyto_lookat % {"duration":1, "lon":lon, "lat":lat, "heading":head, "tilt":75, "range":5000, "alt":0}
#    for elmt in tron:
#        nd = get_noeud_ini_fin(con, elmt[0], elmt[1])
#        (lat,lon, head) = compute_heading(strip_point(nd[0]), strip_point(nd[1]))
#        res += flyto_lookat % {"duration":1, "lon":lon, "lat":lat, "heading":head, "tilt":80, "range":500, "alt":0}
    con.close()
    tr = tour % {"flyto":res, "name":"dowstream tour"}
    doc = kmldoc % {"style":linestyles, "placemarks":pm, "tour":tr}
    f = file(resPath,"w")
    f.write(doc.encode("utf-8"))
    f.close()
    return resFileName


def compute_heading(a, b):
    (xi,yi) = a
    (xf,yf) = b
    x = xf - xi
    y = yf - yi
    sign = 1.0
    if x < 0:
        sign = -1.0
    return yf, xf, sign * math.acos(y / norm(x,y)) * 180.0 / math.pi
    
    
def norm(x,y):
    return math.sqrt(x**2 + y**2)


def strip_point(point):
    point = point[0]
    for s in ["<Point>","<coordinates>","</Point>","</coordinates>"]:
        point = point.strip(s)
    return [float(i) for i in point.split(',')]


def get_coursdo_placemarks(codehydro, style):
    con = psycopg2.connect("dbname='eau_france' user='scy' password='titoon'")
    cur = con.cursor()
    cmp = "="
    if '%' in codehydro: 
        cmp = "like"
    cur.execute("select toponyme, asKML(wkb_geometry) from cours_d_eau where code_hydrographique %s '%s'" % (cmp,codehydro))
    res = ""
    for (desc,geom) in cur.fetchall():
        dico = {"desc":desc.strip(), "geom":geom, "style":style}
        res += placemark % dico
    con.close()
    return res


def get_confluent_placemarks(codehydro):
    con = psycopg2.connect("dbname='eau_france' user='scy' password='titoon'")
    cur = con.cursor()
    cur.execute("select code_zone from zone_hydrographique where code_hydrographique_cours_eau = '%s'" % codehydro)
    res = ""
    for code in cur.fetchall():
        res += get_coursdo_placemarks(code[0] + "%0", "Confluent")
    con.close()
    return res

    
def get_troncon_placemarks(codehydro):
    con = psycopg2.connect("dbname='eau_france' user='scy' password='titoon'")
    cur = con.cursor()
    cur.execute("select toponyme1, asKML(wkb_geometry) from troncon_hydrographique where code_hydrographique_cours_eau = '%s'" % codehydro)
    res = ""
    for (desc,geom) in cur.fetchall():
        dico = {"desc":desc, "geom":geom, "style":"Cours_Eau_random"}
        res += placemark % dico
    con.close()
    return res


def get_lines(pm):
    doc = kmldoc % {"style":linestyles, "placemarks":pm, "tour":""}
    f = file("media/data/hydro.kml","w")
    f.write(doc)
    f.close()


def get_hydrosurf(classif):
    con = psycopg2.connect("dbname='eau_france' user='scy' password='titoon'")
    cur = con.cursor()
    cur.execute("select toponyme, asKML(wkb_geometry) from hydrographie_surfacique where \"classification_entité\" = '%s'" % classif)
    res = ""
    for (desc,geom) in cur.fetchall():
        dico = {"desc":desc, "geom":geom, "style":"Surf_Eau_default"}
        res += placemark % dico
    con.close()
    return res


def get_polys(pm):  
    doc = kmldoc % {"style":polystyle, "placemarks":pm, "tour":""}
    f = file("media/data/hydro.kml","w")
    f.write(doc)
    f.close()


if __name__ == "__main__":
    #res = get_troncon_placemarks("----000A")
    #get_lines(res)
    get_tour("O---0100")
    #res = get_troncons("O---0100")
    #print res
    
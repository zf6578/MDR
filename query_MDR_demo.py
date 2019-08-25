# -*- coding: utf-8 -*-
import networkx as nx
import time
from fiona.crs import from_epsg
from functools import partial
from collections import Counter
import pyproj
from shapely.ops import transform
from collections import namedtuple, defaultdict
import fiona,geopandas,shapefile
import osmnx as ox
import pandas as pd
import pickle,os,rtree
from hmm.RSTR_v15 import RSTRtree
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from hmm.STRtree import STRtree_f
from hmm.STR_Hilbert import STR_Hilbert
from hmm.HMMv1 import haversine,transimission_probability,observation_probability,getDegree,getDegree_cos,find_dijkstra_path_length
from forgery_py.forgery.name import location
##################################
#60s ��׼����100
##################################
#from hmm.testmatching import *
DISTANCE_SET=200
SMALL_PROBABILITY = 0.0000000001
question_point=[]
road_point=[]
project_set = namedtuple('project_set', ["log_lon", "log_lat",'tar', "project_lon", "project_lat",'road_head_lon','road_head_lat','road_tail_lon','road_tail_lat', "road_id",'log_direction','road_direction','r_coord','road_length','road_kind'])
gps_set = namedtuple('gps_set', ['x','y','direction'])
obs_object=namedtuple('obs_object',['obs_lon','obs_lat','candidata_list','max_pro','last_target','target','road_ids','r_h_t','direction_error','direction_project_road','log_dir','t_info','error_dis'])
per=0.8
road_fix=[]  
def get_road_rtree(osm_path):
    c = fiona.open(osm_path)
    coord_feature_dict = {}
    geom_list = []
    count=0
    b_list=[]
    for feature in c: 
        geometry = feature['geometry']  
        dd=geometry['coordinates']
        geometry['coordinates']=dd
        geom = shape(geometry) 
        geom_list.append(geom)
        count+=1
        #if count==10000:break
    c.close()
#     print(len(geom_list))
    #len(geo_list)=2668904

    begin_tick3 = time.time()
    RSTR=RSTRtree(geom_list)
    end3=time.time()
    print('RSTRtree building time: %s Seconds'%(end3-begin_tick3))
    return RSTR, coord_feature_dict

def read_gps_pkl(file):
    traj_file = open(file,'rb')
    traj = pickle.load(traj_file)
    id=0
    origi_points_lists=[]
    origi_points_show=[]
    for tra in traj:
        origi_tra=[]
#         print(tra)
        gps_id_logs = defaultdict(list)
        for i in tra:
            origi_tra.append([i[0],i[1]])
            direction=i[2]
            gps_id_logs[id].append(
                gps_set(
                    i[0],
                    i[1],
                    direction,
                    )
                )
            id+=1
        origi_points_show.append(origi_tra)
        origi_points_lists.append(gps_id_logs)
    return origi_points_lists,origi_points_show
 
 
def get_obs_point(data1,data2):
    d1=[]
    d2=[]
    for i in range(len(data1)):
        if(data2[i][0]==0):continue
        else:
            d1.append(data1[i])
            d2.append([data2[i][0],data2[i][1]])
    return d1,d2

def geodesic_point_buffer(lat, lon, m):
    proj_wgs84 = pyproj.Proj(init='epsg:4326')
    # Azimuthal equidistant projection
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(0, 0).buffer(m)
    return transform(project, buf)


if __name__ == '__main__':
    count=0
    str_query_time=0
     
    str_list,coord_feature_dict = get_road_rtree('./input/edges.shp')
    gps_info,origi_points_show = read_gps_pkl('app-0809/result_traj/5767.pickle')
    #str_list,coord_feature_dict = get_road_rtree('./input/road/gis_osm_roads_free_1.shp')
#     with open('RSTR_PYTHON_china.pickle','wb') as file:
#         pickle.dump(str_list,file)
#     with open('RSTR_PYTHON_china.pickle','rb') as file2:
#         str_list = pickle.load(file2)
    buffers_10=[]
    buffers_100=[]
    buffers_1000=[]
    buffers_2000=[]
    buffers_3000=[]
    buffers_4000=[]
    buffers_5000=[]
    buffers=[]
    for traj in range(len(gps_info)):
        for id,logs in gps_info[traj].items():  
            count+=1  
            point = Point(logs[0].x, logs[0].y)
            point_buffer=geodesic_point_buffer(point.x,point.y,50)
#             result1=[]
#             road=str_list[1].query_rect(str_list[1].root,point_buffer,result1)
#             road=str_list[0].query(point_buffer)
#             for i in road:
#                 print(i)
#             print('----------------------')
#             for i in result1:
#                 print(i)
            buffers.append(point_buffer)
            if count==10:
                buffers_10=buffers.copy()
            elif count==100:
                buffers_100=buffers.copy()
            elif count==1000:
                buffers_1000=buffers.copy()
            elif count==2000:
                buffers_2000=buffers.copy()
            elif count==3000:
                buffers_3000=buffers.copy()
            elif count==4000:
                buffers_4000=buffers.copy()
            elif count==5000:
                buffers_5000=buffers.copy()

    begin_tick_10_hilbert = time.time()
    for i in buffers_10:
        result2=[]
        road=str_list.query_rect(str_list.root,i,result2)
#         print(len(road))
#         for i in road:
#             print(i)
    end_10_hilbert=time.time()   
    print('10 buffer_RSTR_V1: %s Seconds'%(end_10_hilbert-begin_tick_10_hilbert))

    begin_tick_100_hilbert = time.time()
    for i in buffers_100:
        result2=[]
        road=str_list.query_rect(str_list.root,i,result2)
#         print(len(road))
#         for i in road:
#             print(i)
    end_100_hilbert=time.time()   
    print('100 buffer_RSTR_V1: %s Seconds'%(end_100_hilbert-begin_tick_100_hilbert))



    begin_tick_1000_hilbert = time.time()
    for i in buffers_1000:
        result2=[]
        road=str_list.query_rect(str_list.root,i,result2)
    end_1000_hilbert=time.time()   
    print('1000 buffer_RSTR_V1: %s Seconds'%(end_1000_hilbert-begin_tick_1000_hilbert))

    begin_tick_2000_python = time.time()
    for i in buffers_2000:
        result1=[]
        road=str_list.query_rect(str_list.root,i,result1)
    end_2000_python=time.time()
    print('2000 buffer_str: %s Seconds'%(end_2000_python-begin_tick_2000_python))

    begin_tick_3000_python = time.time()
    for i in buffers_3000:
        result1=[]
        road=str_list.query_rect(str_list.root,i,result1)
    end_3000_python=time.time()
    print('3000 buffer_str: %s Seconds'%(end_3000_python-begin_tick_3000_python))
    begin_tick_4000_python = time.time()
    for i in buffers_4000:
        result1=[]
        road=str_list.query_rect(str_list.root,i,result1)
    end_4000_python=time.time()
    print('4000 buffer_str: %s Seconds'%(end_4000_python-begin_tick_4000_python))





    begin_tick_5000_hilbert = time.time()
    for i in buffers_5000:
        result2=[]
        road=str_list.query_rect(str_list.root,i,result2)
    end_5000_hilbert=time.time()   
    print('5000 buffer_RSTR_V1: %s Seconds'%(end_5000_hilbert-begin_tick_5000_hilbert))

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

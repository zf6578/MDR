# -*- coding: utf-8 -*-
'''
Created on 2019年8月15日

@author: 
zhao fan
zhao huihui
chen ren hai
feng zhi yong
'''
import math
import hashlib
from shapely.geometry import Polygon
import math
import pyproj
from hmm.HMMv1 import haversine
from hmm.STR_Hilbert import hilbert_code_abs
from shapely.geometry import Polygon
NODEC1=1000
NODEC2=10
show_over_area=[]
show_over_node=[]
overlap_str=[]
overlap_rstr=[]
class RSTRPoint:
    
    def __init__(self, x,y):
            self.x = x
            self.y = y
class RSTRNode:
    def __init__(self,mbr,isleaf,childlist,hashvalue,geoline):
        self.mbr =mbr
        self.isleaf = isleaf
        self.childList = childlist       
        self.hashvalue = hashvalue
        self.geoline = geoline
#STR rectangle
class Rect:
    def __init__(self,bounds):
        self.minx=bounds[0]
        self.miny=bounds[1]
        self.maxx=bounds[2]
        self.maxy=bounds[3]
    def  getCenter(self):
        return  RSTRPoint((self.minx+self.maxx)/2.0,(self.miny+self.maxy)/2.0)
    def toString(self):
        strd = ""+str(self.minx)+" "+str(self.maxx)+" "+str(self.miny)+" "+str(self.maxy)
        return strd
    def getbounds(self):
        return (self.minx,self.miny,self.maxx,self.maxy)
#STR tree
beijing=[]
class RSTRtree:

    def __init__(self,geolist):
        nodelist=[]
        for i in geolist:
            r=Rect(i.bounds)
            nodelist.append(RSTRNode(r,1,None,"",i))
        rootnodes =self.createTree(10,nodelist)
        root = self.mergeRoot(rootnodes)   
        self.root=root
        #print(show_over_area)
        print(show_over_node)
        #print(len(show_over_area),len(show_over_node))
    def createTree(self,nodec,nodelist):  
        current = nodelist
        break_num=0
        check_1=0
        check_2=0
        while len(current)>10:
            overlap_floor_str=0
            overlap_floor_rstr=0
            print('begin',len(current))
            cur=[]
            leafnodecount=int(math.ceil(len(current)/float(nodec)))
            xsliceCapacity=int(math.ceil(math.sqrt(leafnodecount)))
            slices = self.stripPartition(current,xsliceCapacity*nodec,1)
            temp_core_list=[]
            print(len(slices))
            for i in range(len(slices)):
                temp1=slices[i]
                #before=self.stripPartition(temp1,10,2)
#                 break_num+=1
                if i==len(slices)-1:
                    core=slices[i]
                    after=self.stripPartition(core,nodec,2)
                else:
                    core=slices[i]
                    core_right=slices[i+1]
                    yslices_core=sorted(core, key=lambda STRNode: float(STRNode.mbr.getCenter().y),reverse =True)
                    yslices_next=sorted(core_right, key=lambda STRNode: float(STRNode.mbr.getCenter().y),reverse =True)
                    after,next_use_list=self.cross_search(yslices_core,yslices_next,10,temp_core_list)
                    temp_core_list=next_use_list
                    print(len(slices[i]),len(after))
                #isinter1=self.find_inter(before)
#                 print('修正前','叶子节点容量为',10)
#                 print('第',i,'个slices','每个slices有',len(before),'个叶子节点',len(slices),'====================================================')
#                 print('这个slices里共有',isinter1,'个重复矩形框')
#                 isinter2=self.find_inter(after)
#                 print('修正后','叶子节点容量为',10)
#                 print('第',i,'个slices','每个slices有',len(after),'个叶子节点','====================================================')
#                 print('这个slices里共有',isinter2,'个重复矩形框')
                #check_1+=isinter1
                #check_2+=isinter2
                #overlap_floor_str+=isinter1
                #overlap_floor_rstr+=isinter2
                #if break_num==2:break
                
            
                for arr in after:
                    t2=[]
                    if arr[0].isleaf==True:
                        hashleaf = ""
                        for n in arr:
                            hashleaf += n.mbr.toString()
                        hashva=hashlib.sha1(hashleaf.encode(encoding='utf_8')).hexdigest()
                        j=self.get_upper_mbr(arr)
                        show_over_node.append([[j.miny,j.minx],[j.miny,j.maxx],[j.maxy,j.maxx],[j.maxy,j.minx]])
                        rstrnode=RSTRNode(self.get_upper_mbr(arr),False,arr,hashva,None)
                        cur.append(rstrnode)
                    else:
                        hashup = ""
                        for n in arr:
                            hashup += n.mbr.toString()+n.hashvalue
                        hashva=hashlib.sha1(hashup.encode(encoding='utf_8')).hexdigest()
                        rstrnode=RSTRNode(self.get_upper_mbr(arr),False,arr,hashva,None)
                        cur.append(rstrnode)
            current=cur
            
            #print(len(current))
            overlap_str.append(overlap_floor_str)
           # overlap_rstr.append(overlap_floor_rstr)
        print(overlap_str,overlap_rstr)
        print(check_1,check_2)
        return current
    def cross_search(self,yslices_core,yslices_next,num,core_use_list):
        not_full=[]
        result_list=[]
        next_use_list=[]
        cluster_dic=dict()
        for i in range(len(yslices_core)):
            if i in core_use_list: continue
            #当前工作：变更corelist
            cluster_list=[]
            cluster_list.append(yslices_core[i])
            core_use_list.append(i)
            search_area_mbr=self.get_search_area(yslices_core[i])
            t1=[]          
            t1.append([[search_area_mbr.miny,search_area_mbr.minx],[search_area_mbr.miny,search_area_mbr.maxx],[search_area_mbr.maxy,search_area_mbr.maxx],[search_area_mbr.maxy,search_area_mbr.minx]])
            Hit_list=self.get_rec_from_area(i,yslices_core,yslices_next,search_area_mbr,core_use_list,next_use_list)
            show_over_area.append(t1)
            #print(len(Hit_list))      
            if len(Hit_list)>8:
                cluster_dic,core_use_list,next_use_list=self.get_cluster(cluster_list,Hit_list,core_use_list,next_use_list,cluster_dic)
            elif len(Hit_list)<9 and len(Hit_list)>3:
                cluster_dic,core_use_list,next_use_list=self.hit_to_cluster_half(cluster_list,Hit_list,core_use_list,next_use_list,cluster_dic)
            else:
                #print('不满',len(Hit_list))
                not_full,core_use_list,next_use_list=self.hit_to_cluster(not_full,yslices_core[i],i,Hit_list,core_use_list,next_use_list)              
        new_cluster=self.re_insert(cluster_dic,not_full)
        #self.fix_cluster(new_cluster)
        for i in new_cluster:
            result_list.append(new_cluster[i])
#             t2=[]
#             t3=[]
#             for j in new_cluster[i]:
#                 mbr1=j.mbr
#                 t2.append([[mbr1.miny,mbr1.minx],[mbr1.miny,mbr1.maxx],[mbr1.maxy,mbr1.maxx],[mbr1.maxy,mbr1.minx]])
#             t3.append(t2)
              
#        print('done')
        return result_list,next_use_list
#    def fix_cluster(self,cluster):
        
    def re_insert(self,cluster_dic,not_full):
        for i in not_full:
            min_dis=100000000000
            c=i.mbr.getCenter()
            for j in cluster_dic:      
                dis=haversine(c.x,c.y,j.x,j.y)
                if dis<min_dis:
                    min_dis=dis
                    clu=j
            #print(len(not_full),len(cluster_dic))
            cluster_dic[clu].append(i)
        return cluster_dic
    def get_rec_from_area(self,k,yslices_core,yslices_next,search_area_mbr,core_use_list,next_use_list):
        hit_list=dict()
        for i in range(len(yslices_core)):
            judge=self.judge_use(i,core_use_list)
            if judge==1:continue
            else:
                if self.judge_inter_mbr(yslices_core[i].mbr,search_area_mbr)==1:
                    hit_list[(0,i)]=yslices_core[i]
        for i in range(len(yslices_next)):
            judge=self.judge_use(i,next_use_list)
            if judge==1:continue
            else:
                if self.judge_inter_mbr(yslices_next[i].mbr,search_area_mbr)==1:
                    hit_list[(1,i)]=yslices_next[i] 
        return hit_list
    def judge_use(self,i,use_list):
        if i in use_list:
            return 1
        else:
            return 0
    def get_search_area(self,core):
        centen=core.mbr.getCenter()
        minx,miny,maxx,maxy=core.mbr.minx,core.mbr.miny,core.mbr.maxx,core.mbr.maxy
        search_lat_min=miny-0.03
        search_lat_max=maxy+0.03
        search_lon_min=minx-0.03
        search_lon_max=maxx+0.03
        return Rect((search_lon_min,search_lat_min,search_lon_max,search_lat_max))
#     def get_search_area(self,core):
#         area_list=[]
#         for i in range(len(yslices_core)):
#             if i in core_use_list:continue
#             else:
#                 area_list.append(yslices_core[i])
#                 if len(area_list)==10:break
#         minx,miny,maxx,maxy=self.get_search_lat(area_list)
#         search_lat_min=miny
#         search_lat_max=maxy+maxy-miny
#         #search_lon_min,search_lon_max=self.get_search_lon(minx,miny,maxx,maxy)  
#         search_lon_min,search_lon_max=self.get_search_lon_2(yslices_core,yslices_next)
#         return Rect((search_lon_min,search_lat_min,search_lon_max,search_lat_max))
    def get_search_lon_2(self,yslices_core,yslices_next):
        t=yslices_core+yslices_next
        minx=10000000
        maxx=0
        for n in t:
            if(n.mbr.minx<minx):
                minx = n.mbr.minx
            if(n.mbr.maxx>maxx):
                maxx = n.mbr.maxx
        return  minx,maxx
    def get_search_lon(self,minx,miny,maxx,maxy):
        lon_last=maxx-minx
        lat=maxy-miny
        if lat>lon_last:
            rec=lat-lon_last
            s=rec/2
            return minx-s,maxx+s
        else:
            return minx,maxx
    def get_search_lat(self,area_list):
        minx=10000000
        maxx=0
        miny=1000000000000
        maxy=0
        for n in area_list:
            if(n.mbr.minx<minx):
                minx = n.mbr.minx
            if(n.mbr.maxx>maxx):
                maxx = n.mbr.maxx
            if(n.mbr.miny<miny):
                miny = n.mbr.miny
            if(n.mbr.maxy>maxy):
                maxy = n.mbr.maxy
        return  minx,miny,maxx,maxy
    def mergeRoot(self,rootnodes): 
        rootmbr=self.get_upper_mbr(rootnodes)
        roothash=''
        for r in rootnodes:
            roothash += r.mbr.toString()+r.hashvalue
        root=RSTRNode(rootmbr,False,rootnodes,roothash,None)    
        return root
    def get_upper_mbr(self,nodelist):
        minx=10000000
        maxx=0
        miny=1000000000000
        maxy=0
        for n in nodelist:
            if(n.mbr.minx<minx):
                minx = n.mbr.minx
            if(n.mbr.maxx>maxx):
                maxx = n.mbr.maxx
            if(n.mbr.miny<miny):
                miny = n.mbr.miny
            if(n.mbr.maxy>maxy):
                maxy = n.mbr.maxy
        return Rect((minx,miny,maxx,maxy))

    def  stripPartition(self,plist,sliceCapacity,tar):    
        sliceCount = int(math.ceil(len(plist) / float(sliceCapacity))) 
        if  tar==1:
            plist=sorted(plist, key=lambda STRNode: float(STRNode.mbr.getCenter().x),reverse =True)
        elif tar==2:
            plist=sorted(plist, key=lambda STRNode: float(STRNode.mbr.getCenter().y),reverse =True)  
        slices=[]
        flag=0
        for i in range(sliceCount):
            tmp=[]
            boundablesAddedToSlice = 0
            while boundablesAddedToSlice<sliceCapacity and flag<len(plist):
                tmp.append(plist[flag])
                flag+=1
                boundablesAddedToSlice+=1
            else:
                slices.append(tmp)
                continue              
        return slices

    def query_rect(self,strroot,rect,result): 
        if(self.isintersects(strroot.mbr,rect)==True):
            #print('root hit',len(strroot.childList))
            for i in range(len(strroot.childList)):
                #print('start')
                if(self.isintersects(strroot.childList[i].mbr,rect)==True and strroot.childList[i].isleaf==False):
                    #print('not leaf')
                    self.query_rect(strroot.childList[i],rect,result)
                else :  
                    #print('secondry')          
                    if(strroot.childList[i].isleaf==True):
                        #print('leaf hit')
                        if(self.isintersects(strroot.childList[i].mbr,rect)==True):
                            result.append(strroot.childList[i].geoline)                  
                    else:
                        continue
        return result
    def isintersects(self,mbr,query_rect):
        mbr_polygon=Polygon(((mbr.minx,mbr.miny),(mbr.maxx,mbr.miny),(mbr.maxx,mbr.maxy),(mbr.minx,mbr.maxy)))
        if query_rect.intersects(mbr_polygon):
            return True
        else:
            return False
    def hit_to_cluster(self,not_full,core,k,Hit_list,core_use_list,next_use_list):
        for i in Hit_list:
            not_full.append(Hit_list[i])
            if i[0]==0:
                core_use_list.append(i[1])  
            elif i[0]==1:
                next_use_list.append(i[1])
        not_full.append(core)
        core_use_list.append(k)
        return not_full,core_use_list,next_use_list
    def hit_to_cluster_half(self,cluster_list,Hit_list,core_use_list,next_use_list,cluster_dic):
        for i in Hit_list:
            cluster_list.append(Hit_list[i])
            if i[0]==0:
                core_use_list.append(i[1])  
            elif i[0]==1:
                next_use_list.append(i[1])
        cluster=self.get_upper_mbr(cluster_list)
        cluster_core=cluster.getCenter()
        if cluster_core in cluster_dic:
            print('error!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        else:
            cluster_dic[cluster_core]=cluster_list
        return cluster_dic,core_use_list,next_use_list
    def get_cluster(self,cluster_list,Hit_list,core_use_list,next_use_list,cluster_dic):
        while len(cluster_list)!=10:
            cluster=self.get_upper_mbr(cluster_list)
            cluster_core=cluster.getCenter()
            #先不考虑重叠判定
            min_dis_node,Hit_list,node_location=self.get_dis(cluster,Hit_list)
            cluster_list.append(min_dis_node)
            if node_location[0]==0:
                core_use_list.append(node_location[1])
            else:
                next_use_list.append(node_location[1])
        if cluster_core in cluster_dic:
            print('error!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        else:
            cluster_dic[cluster_core]=cluster_list
        return cluster_dic,core_use_list,next_use_list

    def  get_dis(self,cluster,Hit_list):  
        s=[]   
        for i in Hit_list:
            cluster_core_center=cluster.getCenter()
            temp_center=Hit_list[i].mbr.getCenter()
            dis=haversine(cluster_core_center.x,cluster_core_center.y,temp_center.x,temp_center.y)
            s.append([dis,i])
        s.sort(key=lambda x: x[0])
        k=s[0][1]
        node=Hit_list[k]
        del Hit_list[k]
        return node,Hit_list,k
    def geodesic_point_transform(self,lon, lat):
        p1 = pyproj.Proj(init="epsg:4326") # 定义数据地理坐标系 WGS84
        p2 = pyproj.Proj(init="epsg:3857") # 定义转换投影坐标系
        x, y = pyproj.transform(p1, p2, lon, lat)
        return [x,y]
    def get_area(self,newmbr):
        ld=self.geodesic_point_transform(newmbr.minx,newmbr.miny)
        ru=self.geodesic_point_transform(newmbr.maxx,newmbr.maxy)
        area=(ru[0]-ld[0])*(ru[1]-ld[1])
        return area
    def judge_inter_mbr(self,mbr1,mbr2):
        mbr_polygon1=Polygon(((mbr1.minx,mbr1.miny),(mbr1.maxx,mbr1.miny),(mbr1.maxx,mbr1.maxy),(mbr1.minx,mbr1.maxy)))
        mbr_polygon2=Polygon(((mbr2.minx,mbr2.miny),(mbr2.maxx,mbr2.miny),(mbr2.maxx,mbr2.maxy),(mbr2.minx,mbr2.maxy)))
        if mbr_polygon1.intersects(mbr_polygon2):
            return True
        else:
            return False
    def query_rect_overlap(self,strroot,rect,result): 
        MBR_RECT=Polygon(((rect.minx,rect.miny),(rect.maxx,rect.miny),(rect.maxx,rect.maxy),(rect.minx,rect.maxy))) 
        for i in range(len(strroot.childList)):
            if(self.isintersects(strroot.childList[i].mbr,MBR_RECT)==True and strroot.childList[i].isleaf==False):
                self.query_rect(strroot.childList[i],MBR_RECT,result)
            else :
                if(strroot.childList[i].isleaf==True):
                    if(self.isintersects(strroot.childList[i].mbr,MBR_RECT)==True):
                        result.append(strroot.childList[i].geoline)                  
                else:continue
        return result
    def find_inter(self,slices):
        re=0
        for i in range(len(slices)-1):
            s=dict()
            for j in range(i+1,len(slices)):
                temp1=slices[i]
                temp2=slices[j]
                strnode1=RSTRNode(self.get_upper_mbr(temp1),False,1,'',None)
                strnode2=RSTRNode(self.get_upper_mbr(temp2),False,1,'',None)
                mbr1=strnode1.mbr
                mbr2=strnode2.mbr
                if self.judge_inter_mbr(mbr1, mbr2)==1:
                    re+=1
        return re   

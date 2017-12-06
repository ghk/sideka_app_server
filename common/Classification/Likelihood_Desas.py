
# coding: utf-8

# In[98]:

import psycopg2 as pg
import sys
import pandas as pd
import numpy as np
import matplotlib as plt
import pandas.io.sql as psql
import pylab as pl
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
get_ipython().magic(u'matplotlib inline')

con = pg.connect("host='database.neon.microvac' dbname='sideka_keuangan_20171120' user='postgres' password='postgres'port=5094")
d = psql.read_sql("select * from learn_kegiatan", con, index_col=None, coerce_float=True, params=None, parse_dates=None, columns=None, chunksize=None)
distinct_uraian = psql.read_sql("select distinct(normalized_uraian) from learn_kegiatan", con, index_col=None, coerce_float=True, params=None, parse_dates=None, columns=None, chunksize=None)



#Filling missing data
d['anggaran'].fillna(0,inplace=True)

#Filter Data
df=d[d.percentage>=0.1]
df=df.reset_index(drop=True)


data=pd.pivot_table(df,index=["fk_region_id"],values=["percentage"],columns=["normalized_uraian"])

#Filling missing data 
data=data.fillna(0)


data_train=pd.DataFrame(data)

from scipy.spatial.distance import pdist, squareform
#Build matrix pdist
distances = pdist(data_train.values, metric='euclidean')
dist_matrix = squareform(distances)

table=pd.DataFrame(dist_matrix)
table['fk_regions']=data.index.tolist()
table = table[['fk_regions'] + table.columns[:-1].tolist()]

#prepare for result matrix
fk_regions=np.array(table['fk_regions'])
distances=np.array(table)

#Transform Matrix
all=[]
for idx_1, dis_1 in enumerate(distances):
    for idx_2, dis_2 in enumerate(dis_1):
        region_distances=[dis_1[0]]
        if idx_1 == idx_2:
            continue
        ref_fk_region=fk_regions[idx_2-1]
        region_distances.append(ref_fk_region)
        region_distances.append(dis_2)
        #print region_distances
        all.append(region_distances)

result=pd.DataFrame(all)
result.columns=["id_desa" , "id_likelihood" , "euclidean_distances"]

#Sort The result
all = sorted(all, key = lambda x: (x[0], x[2]))


split = lambda all, n=len(data): [all[i:i+n] for i in range(0, len(all), n)]
all_splited=split(all);
result = []
for desa in all_splited:
    desa = [x for x in desa if x[2] !=0]
    result.append(desa[0:5])
result
from itertools import chain
zipped=np.concatenate(result)
result=pd.DataFrame(zipped)
result.columns=["fk_region_id", "likelihood_id", "euclidean_score"]

#Adding column rank
rank = [1, 2, 3 , 4 , 5]
#Joining column rank into dataframe
result = result.join(pd.DataFrame(rank * (len(result)/len(rank)+1),columns=['rank']))
result


# In[ ]:




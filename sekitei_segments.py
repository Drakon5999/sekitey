 # coding: utf-8

import sys
import os
import re
import random
import time
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
import numpy as np
import extract_features as exf
import pandas as pd
from sklearn.preprocessing import StandardScaler

quota = []
clusterizer = ""
df = []
classificator = ""
standartizator = ""
def define_segments(QLINK_URLS, UNKNOWN_URLS, QUOTA):
    global quota
    global clusterizer
    global df
    global classificator
    global standartizator
    quota = []
    threshold = 100
    nclusters = 2
    df = pd.DataFrame()
    for url in QLINK_URLS:
        d = exf.extract_features(url)
        d["IsQlink"] = 1
        df = df.append(d, ignore_index=True)
    
    for url in QLINK_URLS:
        d = exf.extract_features(url)
        d["IsQlink"] = 0
        df = df.append(d, ignore_index=True)
    
    cnts = df.count()
    df = df.fillna(0)
    todrop = []
    for i in xrange(len(cnts)):
        if cnts[i] < threshold:
            todrop.append(df.columns[i])
    df = df.drop(todrop, axis=1)
    y = df["IsQlink"].values
    df = df.drop("IsQlink", axis=1)
    X = df.values
    standartizator = StandardScaler()
    X = standartizator.fit_transform(X)
    clusterizer = KMeans(n_clusters=nclusters)
    clusterizer.fit(X)
    #classificator = LDA(solver='lsqr').fit(X, y)
    #classificator = SVC()
    classificator = KNeighborsClassifier()
    classificator.fit(X, y)
    qlInCluster = []
    
    for i in xrange(nclusters):
        qlInCluster.append(sum(y[clusterizer.labels_ == i]))
        quota.append(QUOTA/500 * qlInCluster[i] + QUOTA/100)
    

#
# returns True if need to fetch url
#
def fetch_url(url):
    global quota
    global clusterizer
    global df
    global standartizator
    d = exf.extract_features(url, df.columns).values()
    d = standartizator.transform([d])[0]
    cls = clusterizer.predict([d])[0]
    if classificator.predict_proba([d])[0][1] > 0.6:
        quota[cls] -= 1
        return True
    if quota[cls] > 0:
        quota[cls] -= 1
        return True
    else:
        return False

# coding: utf-8

# In[75]:

import sys
import re
import random
from operator import itemgetter
from collections import defaultdict
import urlparse

how_many_urls = 1000
alpha = 0.1
threshold = how_many_urls * alpha
features = {}

def parse_url(url):
    if (len(url) > 1) and (url[len(url) - 1] == '/'):
        url = url[0:len(url) - 1]
    url = urlparse.unquote(url)
    splited = url.split("/")[3:]
    params = splited[-1].split("?")
    if (len(params) > 1):
        params = params[1]
        params = params.split("&")
    else:
        params = []
    for i in xrange(len(params)):
        params[i] = params[i].split("#")[0]
        params[i] = params[i].split("=")
        
    return [splited, params]

def add_to_dict(label, exist):
    if exist is not None:
        if label in exist:
            features[label] = 1
    else:
        features[label] = 1
    
def extract_features(urls, labels=None):
    global features
    lst = []
    for url in urls:
        features = dict()
        if labels is not None:
            for l in labels:
                features[l] = 0
        segments, params = parse_url(url)
        add_to_dict("segments:" + str(len(segments)), labels)  # 1
        for j in xrange(len(params)):
            add_to_dict("param_name:" + params[j][0], labels)  # 2
            if (len(params[j]) == 2):
                add_to_dict("param:" + params[j][0] + "=" + params[j][1], labels) # 3

        for j in xrange(len(segments)):  # 4
            add_to_dict("segment_name_" + str(j) + ":" + segments[j], labels)  # a
            
            exts = segments[j].split(".")
            if len(exts) > 1:
                add_to_dict("segment_ext_" + str(j) + ":" + exts[-1], labels)  # d
            if re.match("[\d]+$", segments[j]) is not None:
                add_to_dict("segment_[0-9]_" + str(j) + ":1", labels)  # b
            if re.match("[^\d]+\d+[^\d]+$", segments[j]) is not None:
                add_to_dict("segment_substr[0-9]_" + str(j) + ":1", labels)  # c

                exts = segments[j].split(".")
                if len(exts) > 1:
                    add_to_dict("segment_ext_substr[0-9]_" + str(j) + ":" + exts[-1], labels)  # e

            add_to_dict("segment_len_" + str(j) + ":" + str(len(segments[j])), labels)  # f
            lst.append(features)
    return lst
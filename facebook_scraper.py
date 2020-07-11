# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 16:13:06 2020

@author: Sam
"""

#Facebook network analysis



#import modules
from html.parser import HTMLParser
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
from tqdm import tqdm
import pickle
import getpass
import random
#set up function to get the users facebook page

def get_fb_page(url):
    time.sleep(5)
    driver.get(url)

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    html_source = driver.page_source
    return html_source

#create function to find friend from their url
def find_friend_from_url(url):
    if re.search('com\/profile.php\?id=\d+\&',url):
        m=re.search('com\/profile.php\?id=(\d+)\&',url)
        friend=m.group(1)
    else:
        m=re.search('com\/(.*)\?',url)
        friend=m.group(1)
    return friend

class MyHTMLParser(HTMLParser):
    urls=[]
    
    def error(self,message):
        pass
    def handle_starttag(self, tag, attrs):
        #only parse the 'anchor' tag
        if tag=='a':
            #check list of defined attributes
            for name,value in attrs:
                #if href is defined print it
                if name=='href':
                    if re.search('\?href|&href|hc_local|\?fref',value) is not None:
                        if re.search('.com/pages',value) is None:
                            self.urls.append(value)

#execute scraper
                            
username=input('Facebook username: ')
password=getpass.getpass('Password: ')
#so this opens up chrome and logs into facebook
chrome_options=webdriver.ChromeOptions()
prefs={"profile.default_content_setting_values.notifications":2}
chrome_options.add_experimental_option("prefs",prefs)
driver=webdriver.Chrome(options=chrome_options)


driver.get('http://www.facebook.com/')

#authenticate to facebook account
elem=driver.find_element_by_id("email")
elem.send_keys(username)
elem=driver.find_element_by_id("pass")
elem.send_keys(password)
elem.send_keys(Keys.RETURN)
time.sleep(5)
print('Successfully logged into Facebook')

scroll_pause_time=15

#get the urls to friends homepage
my_url='https://www.facebook.com/'+username+'/friends/'

#stores the friend list as a pickle object so it doesn't have to be replaced if a network error happens
UNIQ_FILENAME='uniq_urls.pickle'
if os.path.isfile(UNIQ_FILENAME):
    with open(UNIQ_FILENAME,'rb') as f:
        uniq_urls=pickle.load(f)
    print('We loaded {} unique friends'.format(len(uniq_urls)))
else:
    friends_page=get_fb_page(my_url)
    parser=MyHTMLParser()
    parser.feed(friends_page)
    uniq_urls=set(parser.urls)
    
    print('We found {} friends, saving it'.format(len(uniq_urls)))
    
    with open(UNIQ_FILENAME,'wb') as f:
        pickle.dump(uniq_urls,f)

#use the URLS collected in the pickle file to get the mutual friends of all your friends
#but facebook doesn't like this so it pauses for half an hour every 100 pages
        
#pause every 100 friends
friend_graph={}

GRAPH_FILENAME='friend_graph.pickle'

if os.path.isfile(GRAPH_FILENAME):
    with open(GRAPH_FILENAME,'rb') as f:
        friend_graph=pickle.load(f)
    print('Loaded existing graph, found {} keys'.format(len(friend_graph.keys())))
    
count=0
for url in tqdm(uniq_urls):
    count+=1
    if count%100==0:
        print('Too many queries, pausing for a while')
        time.sleep(1800+random.uniform(20,120))
    friend_username=find_friend_from_url(url)
    if (friend_username in friend_graph.keys()) and (len(friend_graph[friend_username])>1):
        continue
    
    friend_graph[friend_username]=[username]
    mutual_url='https://www.facebook.com/{}/friends_mutual'.format(friend_username)
    mutual_page=get_fb_page(mutual_url)
    
    parser=MyHTMLParser()
    parser.urls=[]
    parser.feed(mutual_page)
    mutual_friends_urls=set(parser.urls)
    print('Found {} urls'.format(len(mutual_friends_urls)))
    
    for mutual_url in mutual_friends_urls:
        mutual_friend=find_friend_from_url(mutual_url)
        friend_graph[friend_username].append(mutual_friend)
        
    with open(GRAPH_FILENAME,'wb') as f:
        pickle.dump(friend_graph,f)
    
    time.sleep(30)


#this is the facebook ID. may be a number
CENTRAL_ID='FACEBOOK_ID'

#this is the pickle file containing the raw graph data

GRAPH_FILENAME='friend_graph.pickle'

#load the friend graph
with open(GRAPH_FILENAME,'rb') as f:
    friend_graph=pickle.load(f) #this gives a dictionary of lists with the key being a friend and the values being all their mutual friends
    
import numpy as np
import networkx as nx
#clean the data
#only keep friends with at least 1 common friends
central_friends={}
for k,v in friend_graph.items():
    #this is the number of mutual friends
    #using len doesnt work because it only returns all the persons friends
    intersection_size=len(np.intersect1d(list(friend_graph.keys()),v))
    
    if intersection_size>0:
        central_friends[k]=v
print('Filtered out {} items'.format(len(friend_graph.keys())-len(central_friends.keys())))

#get edges from the graph
edges=[]
nodes=[]

for k,v in central_friends.items():
    for item in v:
        if item in central_friends.keys() or item==CENTRAL_ID:
            edges.append((k,item))
            
g=nx.Graph()
g.add_nodes_from([CENTRAL_ID])
g.add_nodes_from(central_friends.keys())
g.add_edges_from(edges)


nx.write_gexf(g, "fb_data.gexf")

print('Finished!')


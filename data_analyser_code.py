# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 22:11:57 2020

@author: Sam
"""
#code for analysing the data scraped from facebook

import matplotlib.pyplot as plt
import community 
import numpy as np
import pickle
import networkx as nx
import copy

#this is the facebook ID. may be a number
CENTRAL_ID='FACEBOOK_ID'

#this is the pickle file containing the raw graph data

GRAPH_FILENAME='friend_graph.pickle'

#load the friend graph
with open(GRAPH_FILENAME,'rb') as f:
    friend_graph=pickle.load(f) #this gives a dictionary of lists with the key being a friend and the values being all their mutual friends
    

#clean the data
#only keep friends with at least 2 common friends
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
            
#create and visualise network method 1
g=nx.Graph()
g.add_nodes_from([CENTRAL_ID])
g.add_nodes_from(central_friends.keys())
g.add_edges_from(edges)
print('Added {} edges'.format(len(edges)))
pos=nx.spring_layout(g) #get position using the spring layout algorithm

plt.rcParams['figure.figsize']=[100,100]
nx.draw_networkx(g,pos=pos,with_labels=True,label_size=5,node_size=30,width=0.3,node_color='blue',edge_color='grey')
limits=plt.axis('off') #turns off the graph axis
plt.savefig("Network.png") # save as png
plt.figure()

#detect communities
part = community.best_partition(g)
values=[part.get(node) for node in g.nodes()]

plt.rcParams['figure.figsize']=[100,100]
nx.draw_networkx(g,pos=pos,cmap=plt.get_cmap('tab10'),node_color=values,node_size=30,
                 width=0.3,edge_color='grey',with_labels=False,label_size=7)
plt.savefig("Network_community.png") # save as png
plt.figure()



#centrality
#degree centrality
#remove self from graph
g_f=copy.deepcopy(g)
g_f.remove_node(CENTRAL_ID)

#keep the position
pos_f=copy.deepcopy(pos)
pos_f.pop(CENTRAL_ID,None)

#get degree centrality
#highlights friends with the most mutal friends with me normalised byt the total numper of possible connections within the network
degree=nx.degree_centrality(g_f)
values=[degree.get(node)*500 for node in g_f.nodes()]

plt.rcParams['figure.figsize']=[100,100]
nx.draw_networkx(g_f,pos=pos_f,cmap=plt.get_cmap('Reds'),
                 node_color=values,node_size=values,
                 width=0.2,edge_color='grey',with_labels=True,label_size=7)
limits=plt.axis('off')
plt.title('Degree Centrality')
plt.figure()

#closeness centrality
#deeper coloured nodes show a higher cloeness centreality
close=nx.closeness_centrality(g_f)
values=[close.get(node)*100 for node in g_f.nodes()]

nx.draw_networkx(g_f,pos=pos_f,cmap=plt.get_cmap('Blues'),
                 node_color=values,node_size=values,
                 width=0.2,edge_color='grey',with_labels=False,label_size=7)
limits=plt.axis('off')

plt.figure()
#betweeness centrality
#how often a node lies along the shortest path between 2 other nodes, can be seen as an index of potential for gatekeeping or controlling flow
#may indicate power or access to diversity in the network
between=nx.betweenness_centrality(g_f)
values=[between.get(node)*500 for node in g_f.nodes()]
plt.rcParams['figure.figsize']=[100,100]
nx.draw_networkx(g_f,pos=pos_f, cmap=plt.get_cmap('Greens'),
                 node_color=values,node_size=values,
                 width=0.2,edge_color='grey',with_labels=True,label_size=7)
limits=plt.axis('off')

nx.write_gexf(g_f, "test.gexf")
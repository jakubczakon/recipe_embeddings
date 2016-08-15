# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, '../')
import json

from flask import Flask,jsonify
from utils import pickle_in

from sklearn.neighbors import NearestNeighbors

class NearestFood(NearestNeighbors):
    
    def add_data(self,recipe_titles,recipe_vectors):
        self.recipe_titles = recipe_titles
        self.recipe_vectors = recipe_vectors
    
    def get_closest_recipes(self,recipe_title,k=3):
        nbrs = NearestNeighbors(n_neighbors=k).fit(self.recipe_vectors)
        vector_index = self.recipe_titles.index(recipe_title)
        search_vector = self.recipe_vectors[vector_index].reshape(1, -1)
        distances,indices =  nbrs.kneighbors(search_vector)
        print "Close recipes for %s:"%recipe_title
        for distance, index in zip(distances[0][1:],indices[0][1:]):
            print "   %s with distance %s"%(self.recipe_titles[index],distance)
    
    def generate_d3_json(self,output_filepath,recipe_title,k=3):
        nbrs = NearestNeighbors(n_neighbors=k).fit(self.recipe_vectors)
        vector_index = self.recipe_titles.index(recipe_title)
        search_vector = self.recipe_vectors[vector_index].reshape(1, -1)
        distances,indices =  nbrs.kneighbors(search_vector)
        
        close_recipes =[]
        close_recipes_indices=[]
        normalized_distances =[]
        for distance, index in zip(distances[0][1:],indices[0][1:]):
            close_recipes.append(self.recipe_titles[index])
            close_recipes_indices.append(index)
            normalized_distances.append(distance)
        
        
        nodes_list = []
        nodes_list.append({"name":recipe_title})
        for recipe in close_recipes:
            nodes_list.append({"name":recipe})
            
        all_links_list = []
        for distance,index in zip(normalized_distances,close_recipes_indices):
            all_links_list.append({"source":0,
                                   "target":index,
                                   "value":distance
                                      })

        final_dict = {"nodes":nodes_list,
                      "links":all_links_list
                     }
        print final_dict
        with open(output_filepath,'wb') as f:
            json.dump(final_dict,f)

if __name__ == "__main__":
    nearest_food_search_class = os.path.join("../","notebooks","models","deep_embeddings_models","nearest_food_class.pkl")
    print nearest_food_search_class
    NF = pickle_in(nearest_food_search_class)
    
    json_output_filepath = os.path.join("../","d3_visualization","recipe_neighbourhood.json")
    prediction = NF.generate_d3_json(json_output_filepath,
                                     "Bolo de Carne com Requeijão",
                                     k=10)


import os
from copy import copy

import pandas as pd
import numpy as np

import gensim
from gensim.models import Word2Vec
import nltk
from glove import Glove

from sklearn.cross_validation import train_test_split
from sklearn import linear_model
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn import linear_model
from sklearn.neighbors import NearestNeighbors

from keras.preprocessing import sequence
from keras.utils.np_utils import to_categorical

import matplotlib.pyplot as plt

from utils import pickle_out

class GloveExtended(Glove):
    
    @classmethod
    def load_stanford(cls, filename):
        """
        Load model from the output files generated by
        the C code from http://nlp.stanford.edu/projects/glove/.
        The entries of the word dictionary will be of type
        unicode in Python 2 and str in Python 3.
        """

        dct = {}
        vectors = array.array('d')

        # Read in the data.
        with io.open(filename, 'r', encoding='utf-8') as savefile:
            for i, line in enumerate(savefile):
                tokens = line.split(' ')

                word = tokens[0]
                entries = tokens[1:]

                dct[word] = i
                vectors.extend(float(x) for x in entries)

        # Infer word vectors dimensions.
        no_components = len(entries)
        no_vectors = len(dct)

        # Set up the model instance.
        instance = GloveExtended() # here i change the instance to my current class name
        instance.no_components = no_components
        instance.word_vectors = (np.array(vectors)
                                 .reshape(no_vectors,
                                          no_components))
        instance.word_biases = np.zeros(no_vectors)
        instance.add_dictionary(dct)

        return instance
    
    def most_similar_to_word_vector(self, word_vector, number=5):
        if self.word_vectors is None:
            raise Exception('Model must be fit before querying')

        if self.dictionary is None:
            raise Exception('No word dictionary supplied')

        return self._similarity_query(word_vector, number)[1:]
    
    def similarity(self,word1,word2):
        vector1 = self.word_vectors[glv.dictionary[word1]]
        vector2 = self.word_vectors[glv.dictionary[word2]]
        vector1 =  vector1.reshape(1,vector1.shape[0])
        vector2 =  vector2.reshape(1,vector2.shape[0])
        return cosine_similarity(vector1,vector2)[0][0]     
    
    
class IngredientDataTransformer():
    def __init__(self,dictionary_word_count,maxlen_ingredient,max_ingredients,runs):
        self.word_count = dictionary_word_count
        self.maxlen_ingredient = maxlen_ingredient
        self.max_ingredients = max_ingredients
        self.runs = runs 
        
    def corpus_to_x_y_tensors(self,your_corpus,data_filepath):
        X,y =[],[]
        
        for r in range(self.runs):
            for ingr_list in your_corpus:
                if len(ingr_list)==0:
                    continue 
                n = len(ingr_list)
                k =  np.random.randint(n)

                iy =  ingr_list[k]

                del ingr_list[k]
                iX  = copy(ingr_list)

                iX = sequence.pad_sequences(iX, maxlen=self.maxlen_ingredient)
                if len(iX)<self.max_ingredients:
                    pad_nr = self.max_ingredients - len(iX)
                    ingr_pad = np.array([[0]*self.maxlen_ingredient for j in range(pad_nr)])
                    iX = np.vstack((ingr_pad,iX))
                elif len(iX)>self.max_ingredients:
                    iX = np.stack(iX[:self.max_ingredients])
                iX = np.stack(iX)
                X.append(iX)
                y.append(iy)
        
        X=np.array(X)
        print X.shape            
        
        y= sequence.pad_sequences(y, maxlen=self.maxlen_ingredient)
        y = np.array([to_categorical(i,nb_classes=self.word_count+1) for i in y])
#         y = y.reshape(y.shape[0],1,y.shape[1],y.shape[2])
        print y.shape
        result = (X,y)
        if data_filepath:
            pickle_out(data_filepath,result)
        return result
    
    def corpus_to_x_y_tensors_flat(self,your_corpus,data_filepath):
        X,y =[],[]
        
        for r in range(self.runs):
            for ingr_list in your_corpus:
                
                if len(ingr_list)==0:
                    continue 
                n = len(ingr_list)
                k =  np.random.randint(n)

                iy =  ingr_list[k]

                del ingr_list[k]
                iX  = copy(ingr_list)
      
                iX = [item for sublist in ingr_list for item in sublist]
        
                X.append(iX)
                y.append(iy)
        
        X = sequence.pad_sequences(X, maxlen=self.maxlen_ingredient*self.max_ingredients)      
        X=np.array(X)
        print X.shape            
        
        y= sequence.pad_sequences(y, maxlen=self.maxlen_ingredient)
        y = np.array([to_categorical(i,nb_classes=self.word_count+1) for i in y])
#         y = y.reshape(y.shape[0],1,y.shape[1],y.shape[2])
        print y.shape
        result = (X,y)
        if data_filepath:
            pickle_out(data_filepath,result)
        return result

class NearestFood(NearestNeighbors):
    
    def add_data(self,dataset_dict,recipe_vectors_dict):
        self.dataset_dict = dataset_dict
        self.recipe_vectors_dict = recipe_vectors_dict
        
        X,Y= [],[]
        ind_dict = {}
        i=0
        for key, value in self.recipe_vectors_dict.iteritems():
            Y.append(key)
            X.append(value)
            ind_dict[i] = key
            i+=1
            
        self.X=np.array(X)
        self.Y=Y
        self.ind_dict=ind_dict
    
    def fit_model(self,k):
        self.nbrs = NearestNeighbors(n_neighbors=k).fit(self.X)
        
    def get_closest_recipes(self,recipe_title,mode = "dict"):
        
        if mode =="dict":
            search_vector = self.recipe_vectors_dict[recipe_title].reshape(1, -1)
        elif mode =="index":
            print 
            search_vector = self.recipe_vectors_dict[self.ind_dict[recipe_title]].reshape(1, -1)
        else:
            return Exception("Choose dict or index")
        
        distances,indices =  self.nbrs.kneighbors(search_vector)
        print "Close recipes:"
        for distance, index in zip(distances[0][1:],indices[0][1:]):
            print "  %s with distance %s"%(self.ind_dict[index],distance)
            for ingredients in self.dataset_dict[self.ind_dict[index]]['ingredient']:
                print "   -%s"%" ".join(ingredients)
    
    '''
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
        with open(output_filepath,'wb') as f:
            json.dump(final_dict,f)
        return final_dict
    '''
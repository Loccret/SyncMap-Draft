# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['SyncMap', 'SymmetricalSyncMap']

# %% ../nbs/00_core.ipynb 3
import pandas as pd

import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import DBSCAN
from scipy.spatial import distance
from scipy.stats import entropy
from sklearn.metrics import normalized_mutual_info_score, pairwise_distances
from tqdm import tqdm
import copy
from collections import deque
from sklearn.manifold import TSNE

import sys
# sys.path.insert(0, '../')
# 如果没有 pip install -e . 下面一行就不会成功
from .utility import OverlapChunkTest1, to_categorical, compute_combi_dist

from fastcore.utils import *

# from plotly.subplots import make_subplots
# import plotly.graph_objs as go
# import fastcore.all as fc  # patch会报错
# from ipywidgets import widgets
# from IPython.display import display

# %% ../nbs/00_core.ipynb 5
class SyncMap:
	'''
	The original syncmap
	'''
	def __init__(self, input_size, dimensions, adaptation_rate):
		
		self.organized= False
		self.space_size= 10
		self.dimensions= dimensions
		self.input_size= input_size
		#syncmap= np.zeros((input_size,dimensions))
		np.random.seed(41)
		self.syncmap= np.random.rand(input_size,dimensions)
		self.adaptation_rate= adaptation_rate
		self.total_activation= np.zeros(input_size)
		#self.syncmap= np.random.rand(dimensions, input_size)
	
	def inputGeneral(self, x):
		plus= x > 0.1
		minus = ~ plus

		sequence_size = x.shape[0]
		#print(sequence_size, "asfasdfasdfasd")
		for i in range(sequence_size):
			
			vplus= plus[i,:]
			vminus= minus[i,:]
			plus_mass = vplus.sum()
			minus_mass = vminus.sum()
			self.total_activation+= vplus.astype(int)
			# self.total_activation-= vminus.astype(int)
			#print(plus_mass)
			#print(minus_mass)
			
			if plus_mass <= 1:
				continue
			
			if minus_mass <= 1:
				continue

			#print("vplus")
			#print(vplus)
			# np.dot(vplus,self.syncmap): syncmap的每个分量（1~8）在vplus中的贡献（投影）
			center_plus= np.dot(vplus,self.syncmap)/plus_mass
			center_minus= np.dot(vminus,self.syncmap)/minus_mass
		
			#print(self.syncmap.shape)
			#exit()
			dist_plus= distance.cdist(center_plus[None,:], self.syncmap, 'euclidean') # 质心到每个点的距离，相当于cluster的半径？
			dist_minus= distance.cdist(center_minus[None,:], self.syncmap, 'euclidean')
			dist_plus= np.transpose(dist_plus)
			dist_minus= np.transpose(dist_minus)
			
			update_plus= vplus[:,np.newaxis]*((center_plus - self.syncmap)/dist_plus)# + (self.syncmap - center_minus)/dist_minus)
			update_minus= vminus[:,np.newaxis]*((center_minus -self.syncmap)/dist_minus)
			
			update= update_plus - update_minus
			self.syncmap+= self.adaptation_rate*update
			
			maximum=self.syncmap.max()
			self.syncmap= self.space_size*self.syncmap/maximum
			
		self.total_activation= self.total_activation/sequence_size
		
		self.syncmap = self.syncmap * self.total_activation[:, np.newaxis]


	def input(self, x):
		
		self.inputGeneral(x)

		return

			
	def organize(self):
	
		self.organized= True
		#self.labels= DBSCAN(eps=3, min_samples=2).fit_predict(self.syncmap)
		# self.labels= DBSCAN(eps=3, min_samples=2).fit_predict(self.syncmap)
		self.labels= DBSCAN(eps=0.8, min_samples=2).fit_predict(self.syncmap)

		return self.labels

	def activate(self, x):
		'''
		Return the label of the index with maximum input value
		'''

		if self.organized == False:
			print("Activating a non-organized SyncMap")
			return
		
		#maximum output
		max_index= np.argmax(x)

		return self.labels[max_index]

	def plotSequence(self, input_sequence, input_class,filename="plot.png"):

		input_sequence= input_sequence[1:500]
		input_class= input_class[1:500]

		a= np.asarray(input_class)
		t = [i for i,value in enumerate(a)]
		c= [self.activate(x) for x in input_sequence] 
		

		plt.plot(t, a, '-g')
		plt.plot(t, c, '-.k')
		#plt.ylim([-0.01,1.2])


		# plt.savefig(filename,quality=1, dpi=300)
		plt.show()
		plt.close()
	

	def plot(self, color=None, save = False, filename= "plot_map.png"):

		if color is None:
			color= self.labels
		
		print(self.syncmap)
		#print(self.syncmap)
		#print(self.syncmap[:,0])
		#print(self.syncmap[:,1])
		if self.dimensions == 2:
			#print(type(color))
			#print(color.shape)
			ax= plt.scatter(self.syncmap[:,0],self.syncmap[:,1], c=color)
			
		if self.dimensions == 3:
			fig = plt.figure()
			ax = plt.axes(projection='3d')

			ax.scatter3D(self.syncmap[:,0],self.syncmap[:,1], self.syncmap[:,2], c=color);
			#ax.plot3D(self.syncmap[:,0],self.syncmap[:,1], self.syncmap[:,2])
		
		if save == True:
			plt.savefig(filename)
		
		plt.show()
		plt.close()

# %% ../nbs/00_core.ipynb 7
# extract data from parameter space

@patch
def generate_activity_probs(self:SyncMap, sample_x = 0, sample_y = 0, err = 1e-4):
    '''
    Generate the activity probabilities of each variable in syncmap
    return: np.array, shape = (self.output_size, )
    '''
    sample_cord = np.array([sample_x, sample_y])
    # probs = np.zeros(self.output_size)
    weight_dist = compute_combi_dist(self.syncmap)
    pos = np.where(weight_dist == weight_dist.max())[0]
    # tau = -weight_dist[*pos] / np.log(err)  # set tau to make the smallest prob to be err
    tau = -weight_dist.__getitem__(tuple(pos)) / np.log(err)
    # probs = np.exp(-weight_dist / tau)  
    sample_dist = ((self.syncmap - sample_cord) ** 2 ).sum(axis = -1)
    sample_probs = np.exp(-sample_dist / tau)
    return sample_probs

@patch
def plot_activity_maps(self:SyncMap, x = 0, y = 0):
    fig, axs = plt.subplots(1, 2, figsize = (10, 5))
    sample_probs = self.generate_activity_probs(x, y)
    axs[0].scatter(self.syncmap[:, 0], self.syncmap[:, 1], color = 'blue')
    axs[0].scatter(x, y, color = 'red')
    axs[0].set_xlim(self.syncmap.min()-0.5, self.syncmap.max()+0.5)
    axs[0].set_ylim(self.syncmap.min()-0.5, self.syncmap.max()+0.5)
    sns.barplot(sample_probs, ax = axs[1])
    print(sample_probs)
    plt.show()

# SyncMap.generate_activity_probs = generate_activity_probs
# SyncMap.plot_activity_maps = plot_activity_maps

# %% ../nbs/00_core.ipynb 27
@patch
def extract_act_var(self:SyncMap, sample_x = 0, sample_y = 0, err = 1e-4):
    '''
    check if there is any activated variables
    '''
    probs = self.generate_activity_probs(sample_x, sample_y, err)  # Dim: d
    sampled_vars = np.random.binomial(1, probs)  # Dim: d
    # due to there is only 1 variables should be activated, we randomly choose one
    sampled_vars_idx = np.where(sampled_vars)[0]
    if len(sampled_vars_idx) == 0:
        return None 
    else:
        sampled_var = np.random.choice(sampled_vars_idx)
        return sampled_var


@patch
def create_element(self:SyncMap, sampled_var, env):
    '''
    create an element of the time series of the sampled variable
    '''
    tiny_series = np.zeros(env.output_size)
    if sampled_var is None:
        return tiny_series
    else:
        tiny_series[sampled_var] = 1
        return tiny_series


@patch
def create_series(self:SyncMap, x, y, env, seq_len = 1000):
    '''
    generate time series data
    '''
    time_series = []
    for _ in range(seq_len):
        sampled_var = self.extract_act_var(sample_x = x, sample_y = y)
        tiny_series = self.create_element(sampled_var, env)
        time_series.append(tiny_series)
    return np.array(time_series)

# %% ../nbs/00_core.ipynb 42
class SymmetricalSyncMap:
    def __init__(self, input_size, dimensions=3, 
                adaptation_rate=0.1, space_scale=1.0, space_bound=None,
                leaking_rate=1.0, dropout_positive=0.0, dropout_negative=0.0,
                movmean_window=1000, movmean_interval=10,
                is_symmetrical_activation=False, number_of_selected_node=None,
                is_adaptive_LR=False, adaptive_LR_widrow_hoff=0.1):
        self.input_size = input_size
        self.dimensions = dimensions
        self.adaptation_rate = adaptation_rate
        self.space_scale = space_scale
        self.space_scale_dimensions_sqrt = space_scale * np.sqrt(dimensions)
        self.space_bound = space_bound
        self.leaking_rate = leaking_rate
        self.dropout_positive = dropout_positive
        self.dropout_negative = dropout_negative

        # initialize the sync map
        self.syncmap = np.random.rand(self.input_size, self.dimensions) * self.space_scale
        self.syncmap = ((self.syncmap - np.mean(self.syncmap, axis=0)) / (np.std(self.syncmap, axis=0) + 1e-12)) * self.space_scale

        self.syncmap_movmean_list = deque(maxlen=movmean_window)
        self.syncmap_movmean = self.syncmap.copy()
        self.movmean_interval = movmean_interval

        # symmetrical activation
        self.is_symmetrical_activation = is_symmetrical_activation
        self.number_of_selected_node = number_of_selected_node

        # adaptive learning rate
        self.is_adaptive_LR = is_adaptive_LR
        self.adaptive_LR = 1
        self.adaptive_LR_widrow_hoff = adaptive_LR_widrow_hoff



    def input_sequential(self, input_seq, current_state=None, Verbose_tqdm=True):

        # start processing
        if Verbose_tqdm:
            verbose = tqdm # use tqdm
        else:
            verbose = lambda x: x # do not use tqdm

        for i_state in verbose(range(len(input_seq))):
            state = input_seq[i_state]
            current_state_idx = current_state[i_state] if current_state is not None else None
            self.adapt_chunking(input_state_vec=state)
            if i_state % self.movmean_interval == 0 or i_state == len(input_seq) - 1:
                self.syncmap_movmean_list.append(self.syncmap.copy())

        self.syncmap_movmean = np.mean(np.asarray(self.syncmap_movmean_list), axis=0)


    def adapt_chunking(self, input_state_vec):

        syncmap_previous = self.syncmap.copy()

        set_positive = input_state_vec == True
        set_negative = input_state_vec == False

        # symmetrical activation
        if self.is_symmetrical_activation:
            set_positive, set_negative = self.symmetrical_activation(set_positive.copy())

        if set_positive.sum() <= 1 or set_negative.sum() <= 1:
            return syncmap_previous

        centroid_positive = np.dot(set_positive, self.syncmap) / set_positive.sum()
        centroid_negative = np.dot(set_negative, self.syncmap) / set_negative.sum()

        dist_set2centroid_positive = distance.cdist(centroid_positive[None, :], self.syncmap, 'euclidean').T
        dist_set2centroid_negative = distance.cdist(centroid_negative[None, :], self.syncmap, 'euclidean').T

        # get dropout mask
        isDropout_positive = np.random.rand() > self.dropout_positive
        isDropout_negative = np.random.rand() > self.dropout_negative

        # update syncmap
        update_positive = set_positive[:, np.newaxis] * (centroid_positive - self.syncmap) / dist_set2centroid_positive
        update_negative = set_negative[:, np.newaxis] * (centroid_negative - self.syncmap) / dist_set2centroid_negative

        # adaptive learning rate regularization
        if self.is_adaptive_LR:
            adaptive_LR_positive, adaptive_LR_negative = self.update_adaptive_learning_rate(dist_set2centroid_positive, set_positive)
            update_positive = update_positive * adaptive_LR_positive
            update_negative = update_negative * adaptive_LR_negative

        self.syncmap += self.adaptation_rate * (update_positive * isDropout_positive - update_negative * isDropout_negative)

        # regularization
        # normalize the syncmap to have 0 mean and 1 std
        # self.syncmap = ((self.syncmap - np.mean(self.syncmap, axis=0)) / (np.std(self.syncmap, axis=0) + 1e-12)) * self.space_scale
        self.syncmap = (self.syncmap / self.syncmap.max()) * self.space_scale



        # leaking
        self.syncmap = self.leaking_rate * self.syncmap + (1 - self.leaking_rate) * syncmap_previous

        return self.syncmap


    def get_syncmap(self, isMovMean=False):
        if isMovMean:
            self.syncmap_movmean = np.mean(np.asarray(self.syncmap_movmean_list), axis=0)
            return self.syncmap_movmean
        else:
            return self.syncmap

    def symmetrical_activation(self, input_vector):
        state_vector_plus = input_vector.copy()

        ## version 2 ##
        # Consider those positive nodes which are not selected in positive stochastic selection process
        number_of_selected_node_temp = state_vector_plus.sum()
        state_vector_plus = self.stochastic_selection(input_vector=state_vector_plus,
                                                    number_of_selected_node_overwrite=number_of_selected_node_temp)
        # update number_of_selected_node_temp
        number_of_selected_node_temp = state_vector_plus.sum()
        state_vector_minus = self.stochastic_selection(input_vector=~state_vector_plus,
                                                    number_of_selected_node_overwrite=number_of_selected_node_temp)


        return state_vector_plus, state_vector_minus

    def stochastic_selection(self, input_vector, number_of_selected_node_overwrite=None):
        number_of_activated_node = input_vector.sum()

        if self.number_of_selected_node is None:
            number_of_selected_node = number_of_selected_node_overwrite
        else:
            number_of_selected_node = self.number_of_selected_node



        if number_of_activated_node == 0:
            Pr = 0
        elif number_of_selected_node < number_of_activated_node: # randomly select a subset of nodes from the activated nodes
            Pr = number_of_selected_node / number_of_activated_node
        else: # select all the activated nodes
            Pr = 1

        state_vector_after_masking = np.logical_and(input_vector, np.random.rand(len(input_vector)) < Pr)
        return state_vector_after_masking

    def update_adaptive_learning_rate(self, dist_set2centroid_positive, set_positive):
        dist_avg_positive = np.sum(dist_set2centroid_positive * set_positive[:, None]) / set_positive.sum()
        adaptive_LR_positive = dist_avg_positive / self.space_scale_dimensions_sqrt

        ### version 4:
        self.adaptive_LR += self.adaptive_LR_widrow_hoff * (adaptive_LR_positive - self.adaptive_LR)
        adaptive_LR_positive = copy.deepcopy(self.adaptive_LR)
        adaptive_LR_negative = 1

        adaptive_LR_negative_amplifier_a = 0.01
        adaptive_LR_negative_amplifier_b = 2
        adaptive_LR_negative_amplifier = self.input_size * adaptive_LR_negative_amplifier_a + adaptive_LR_negative_amplifier_b
        adaptive_LR_negative_threshold = 1.5
        adaptive_LR_negative = self.adaptive_LR * adaptive_LR_negative_amplifier
        if adaptive_LR_negative > adaptive_LR_negative_threshold:
            adaptive_LR_negative = adaptive_LR_negative_threshold

        adaptive_LR_positive_threshold = 0.05
        if adaptive_LR_positive < adaptive_LR_positive_threshold:
            return adaptive_LR_positive_threshold, adaptive_LR_negative
        else:
            return adaptive_LR_positive, adaptive_LR_negative

    def set_adaptation_rate(self, adaptation_rate):
        self.adaptation_rate = adaptation_rate


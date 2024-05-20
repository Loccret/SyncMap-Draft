# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_GraphProcessor.ipynb.

# %% auto 0
__all__ = ['GraphProcessor', 'WorkingMemProcessor']

# %% ../nbs/01_GraphProcessor.ipynb 4
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import warnings
from collections import deque
from tqdm import tqdm
import time
from fastcore.utils import *  # for example: patch

import seaborn as sns
sns.set_theme()

# %% ../nbs/01_GraphProcessor.ipynb 5
class GraphProcessor:
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.G = None
        self.labels = None
        self.labels_numpy = None
        self.A = None

        # # initialize the graph
        # self.read_graph_from_dot()

    def read_graph_from_dot(self, file_path=None, show_info=True):
        if file_path is None:
            file_path = self.file_path
        if file_path is None:
            raise ValueError("File path not provided.")

        # Read graph from .dot file
        self.G = nx.DiGraph(nx.nx_agraph.read_dot(file_path))  # MultiDiGraph -> DiGraph
        self.labels = {node: self.G.nodes[node]['label'] for node in self.G.nodes}
        # convert labels to numpy int
        self.labels_numpy = np.array([int(self.labels[node]) for node in self.G.nodes])

        # get connection matrix
        num_nodes = len(self.G.nodes)
        nodes = list(self.G.nodes)
        self.A = np.zeros((num_nodes, num_nodes))

        for edge in self.G.edges:
            source = nodes.index(edge[0])
            target = nodes.index(edge[1])
            self.A[source][target] = 1

        if show_info:
            print("Graph loaded from file:", file_path)
            print("Number of nodes:", num_nodes)
            print("Number of edges:", len(self.G.edges))

# %% ../nbs/01_GraphProcessor.ipynb 10
# visualize the graph
@patch
def visualize_graph(self:GraphProcessor):
    # Visualize the graph
    if self.G is not None:
        options = {
            'node_size': 100,
            'arrowstyle': '-|>',
            'arrowsize': 12,
        }
        nx.draw_networkx(self.G, arrows=True, **options)
        plt.show()
    else:
        print("Graph not yet loaded. Call read_graph() first.")

# %% ../nbs/01_GraphProcessor.ipynb 12
# get the ground truth labels
@patch
def get_groundtruth_labels(self:GraphProcessor, dtype='numpy'):
    # Get groundtruth labels from node attributes
    if self.G is not None:
        if dtype == 'dict':
            return self.labels
        elif dtype == 'numpy':
            return self.labels_numpy
    else:
        print("Graph not yet loaded. Call read_graph() first.")
        return None

# %% ../nbs/01_GraphProcessor.ipynb 14
# get the connection matrix A
@patch
def get_connection_matrix(self:GraphProcessor):
    # Generate connection matrix A
    if self.A is not None:
        return self.A
    else:
        print("Graph not yet loaded. Call read_graph() first.")
        return None

# %% ../nbs/01_GraphProcessor.ipynb 16
# Set graph from adjacency matrix
@patch
def set_graph_from_adjacency_matrix(self:GraphProcessor, A):
    # Set graph from adjacency matrix
    self.A = A
    self.G = nx.DiGraph(A)
    self.labels = {node: i for i, node in enumerate(self.G.nodes)}
    self.labels_numpy = np.array([int(self.labels[node]) for node in self.G.nodes])

# %% ../nbs/01_GraphProcessor.ipynb 18
# ccreate a random walk on the graph for generating trajectories(Syncmap data)
@patch
def random_walk_on_graph(self:GraphProcessor, connection_matrix=None, L=3000, reset_time=None):
    if connection_matrix is None:
        connection_matrix = self.A

    num_nodes = connection_matrix.shape[0]

    # Find nodes with no outgoing connections
    no_outgoing = np.where(np.sum(connection_matrix, axis=1) == 0)[0]
    if len(no_outgoing) != 0:
        warnings.warn("Some nodes have no outgoing connections.")

    starting_node = np.random.choice(num_nodes)

    while starting_node in no_outgoing:
        warnings.warn("Starting node has no outgoing connections. Choosing another node.")
        starting_node = np.random.choice(num_nodes)

    trajectory = []
    one_hot_vectors = []

    current_node = starting_node
    steps_since_reset = 0

    print("Random walk starting node:", current_node)

    for _ in tqdm(range(L)):
        # Record current node index
        trajectory.append(current_node)

        # Generate one-hot vector for current node
        one_hot = np.zeros(num_nodes, dtype=np.bool_)
        one_hot[current_node] = True
        one_hot_vectors.append(one_hot)

        # Choose next node based on outgoing connections
        if np.sum(connection_matrix[current_node]) == 0 or (
                reset_time is not None and steps_since_reset == reset_time):
            current_node = np.random.choice(num_nodes)
            warnings.warn("No outgoing connections from current node. Choosing another node.")
            steps_since_reset = 0
        else:
            prob = connection_matrix[current_node] / np.sum(connection_matrix[current_node])
            current_node = np.random.choice(num_nodes, p=prob)
            steps_since_reset += 1

    return np.array(trajectory), np.array(one_hot_vectors)


# %% ../nbs/01_GraphProcessor.ipynb 23
class WorkingMemProcessor:
    def __init__(self, state_memory, input_size=None, time_delay=0):
        self.state_memory = state_memory
        self.input_size = input_size
        self.time_delay = time_delay

        self.working_memory = deque(maxlen=self.state_memory)

    def set_input_size(self, input_size):
        self.input_size = input_size

    def set_time_delay(self, time_delay):
        self.time_delay = time_delay

    def seq_gen_naive(self, input_seq, verbose = False):
        # input_seq is shaped as (seq_len, input_size)
        if input_seq.shape[1] != self.input_size:
            # update input_size
            self.set_input_size(input_seq.shape[1])
            if verbose:
                print("Input size updated to {}.".format(self.input_size))
            # warnings.warn("Input size updated to {}.".format(self.input_size))
                print("generate sequence...")
        # print("generate sequence...")
        time.sleep(0.1)
        output_seq = []
        for i_state in tqdm(range(len(input_seq))):
            state = input_seq[i_state]
            self.working_memory.append(state)
            # convert to numpy
            current_working_mem = np.asarray(self.working_memory)
            current_working_mem = np.sum(current_working_mem, axis=0).astype(np.bool_)

            # append to output_seq
            output_seq.append(current_working_mem)

        return np.asarray(output_seq)
    
    def __repr__(self):
        return f"Working Memory Processor: state_memory={self.state_memory}, input_size={self.input_size}, time_delay={self.time_delay}"

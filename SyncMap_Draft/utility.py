# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/99_utility.ipynb.

# %% auto 0
__all__ = ['to_categorical', 'OverlapChunkTest1', 'compute_combi_dist', 'reduce_dimension_with_tsne', 'create_trace_plot']

# %% ../nbs/99_utility.ipynb 3
import numpy as np
import matplotlib.pyplot as plt
import math
import warnings
# import fastcore.all as fc
from fastcore.utils import *  # for patch
from sklearn.manifold import TSNE
from IPython.display import HTML

# %% ../nbs/99_utility.ipynb 7
def to_categorical(x, num_classes=None):
    """Converts a class vector (integers) to binary class matrix.

    E.g. for use with `categorical_crossentropy`.

    Args:
        x: Array-like with class values to be converted into a matrix
            (integers from 0 to `num_classes - 1`).
        num_classes: Total number of classes. If `None`, this would be inferred
            as `max(x) + 1`. Defaults to `None`.

    Returns:
        A binary matrix representation of the input as a NumPy array. The class
        axis is placed last.

    Example:

    >>> a = to_categorical([0, 1, 2, 3], num_classes=4)
    >>> print(a)
    [[1. 0. 0. 0.]
     [0. 1. 0. 0.]
     [0. 0. 1. 0.]
     [0. 0. 0. 1.]]
    """
    x = np.array(x, dtype="int64")
    input_shape = x.shape

    # Shrink the last dimension if the shape is (..., 1).
    if input_shape and input_shape[-1] == 1 and len(input_shape) > 1:
        input_shape = tuple(input_shape[:-1])

    x = x.reshape(-1)
    if not num_classes:
        num_classes = np.max(x) + 1
    batch_size = x.shape[0]
    categorical = np.zeros((batch_size, num_classes))
    categorical[np.arange(batch_size), x] = 1
    output_shape = input_shape + (num_classes,)
    categorical = np.reshape(categorical, output_shape)
    return categorical

# %% ../nbs/99_utility.ipynb 9
class OverlapChunkTest1:
	'''
	create a simple time series to examine SyncMap
	'''
	def __init__(self, time_delay):

		self.chunk= 0
		self.output_size = 8
		self.counter = -1
		self.time_delay = time_delay
		self.time_counter = time_delay
		self.output_class= 0
		self.previous_output_class= None

		self.sequenceA_length = 4
		self.sequenceB_length = 4 #np.random.randint(2)+5
		self.previous_previous_output_class= None
	
	def getOutputSize(self):
		return self.output_size
	
	def trueLabel(self):
		truelabel= np.array((0,0,0,1,1,2,2,2))  # label of features
		return truelabel

	def updateTimeDelay(self):
		self.time_counter+= 1
		if self.time_counter > self.time_delay:
			self.time_counter = 0 
			return True
		else:
			return False

	#create an input pattern for the system
	def getInput(self, reset = False):
		
		if reset == True:
			self.chunk=0
			self.counter=-1

		update = self.updateTimeDelay()

		if update == True:
			if self.chunk == 0:
				if self.counter > self.sequenceA_length:
					self.chunk = 1
					self.counter= 0
				else:
					self.counter+= 1
			else:
				if self.counter > self.sequenceB_length:
					#self.sequenceB_length = np.random.randint(20)+5
					self.chunk = 0
					self.counter= 0
				else:
					self.counter+= 1

			if self.chunk == 0:
				#input_value = np.random.randint(10)
				#input_value= self.counter
				self.previous_previous_output_class= self.previous_output_class
				self.previous_output_class= self.output_class
				
				#possible outputs are 0,1,2,3,4
				self.output_class = np.random.randint(5)  
			else:
				self.previous_previous_output_class= self.previous_output_class
				self.previous_output_class= self.output_class
				#possible outputs are 3,4,5,6,7
				self.output_class = 3 + np.random.randint(5)

		noise_intensity= 0.0
		#input_value = np_utils.to_categorical(self.output_class, self.output_size) + np.random.randn(self.output_size)*noise_intensity
		if self.previous_output_class is None or self.previous_output_class == self.output_class:  # 上一个else
			input_value = to_categorical(self.output_class, self.output_size)*np.exp(-0.1*self.time_counter) + np.random.randn(self.output_size)*noise_intensity # input encoding (2)
		else:
			input_value = to_categorical(self.output_class, self.output_size)*np.exp(-0.1*self.time_counter) + np.random.randn(self.output_size)*noise_intensity + to_categorical(self.previous_output_class, self.output_size)*np.exp(-0.1*(self.time_counter+self.time_delay))
			# 对以一个刚转移完的态，加上上一个态的编码

		return input_value

	def getSequence(self, iterations):
		input_class = np.empty(iterations)
		input_sequence = np.empty((iterations, self.output_size))

		for i in range(iterations):
			input_value = self.getInput()
			#input_class.append(self.chunk)
			#input_sequence.append(input_value)
			input_class[i] = self.chunk
			input_sequence[i] = input_value
		


		return input_sequence, input_class

	def plot(self, input_class, input_sequence = None, save = False):
		
		a = np.asarray(input_class)
		t = [i for i,value in enumerate(a)]

		plt.plot(t, a)
	
		if input_sequence is not None:
			sequence = [np.argmax(x) for x in input_sequence]
			plt.plot(t, sequence)

		if save == True:
			plt.savefig("plot.png")
		
		plt.show()
		plt.close()
	
	def plotSuperposed(self, input_class, input_sequence = None, save = False):
		warnings.warn("please use `plot_raw_data` instead", category=DeprecationWarning)
		input_sequence= np.asarray(input_sequence)
		
		t = [i for i,value in enumerate(input_sequence)]

		print(input_sequence.shape)

		#exit()

		for i in range(input_sequence.shape[1]):
			a = input_sequence[:,i]
			plt.plot(t, a, "*-")
		
		a = np.asarray(input_class)
		plt.plot(t, a, "*-")

		if save == True:
			plt.savefig("plot.png")
		
		plt.show()
		plt.close()

		

# %% ../nbs/99_utility.ipynb 15
def compute_combi_dist(data:np.ndarray)->np.ndarray:
    '''
    Compute the distance between all rows of the matrix.
    args:
        data: np.ndarray, shape (n_samples, n_features)
    return:
        np.ndarray, shape (n_samples)
    '''
    n_samples = data.shape[0]
    dist = np.zeros((n_samples, n_samples))
    for i in range(n_samples):
        for j in range(n_samples):
            dist[i, j] = np.linalg.norm(data[i] - data[j])
    return dist

# %% ../nbs/99_utility.ipynb 19
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

@patch
def plot_raw_data(self:OverlapChunkTest1, 
                    values:np.ndarray,  # time series data
                    labels:np.ndarray = None,  # the labels
                    save = False):
    '''
    Plot the encoded data.
    args:
        values: np.ndarray
        input_class: np.ndarray, label
        save: bool, default False
    '''
    values = np.asarray(values)
    if len(values.shape) == 1: values = values.reshape(-1, 1)
    num_channels = values.shape[1]

    fig = make_subplots(rows=num_channels, cols=1, shared_xaxes=True, 
                        shared_yaxes=True,
                        vertical_spacing=0.02
                        );

    # Loop through each channel and add it as a separate subplot
    for i in range(num_channels):
        fig.add_trace(
            go.Scatter(y=values[:, i], mode='lines', name=f'Channel {i+1}'),
            row=i + 1, col=1
        );
        if labels is not None:
            fig.add_trace(
                go.Scatter(y=labels, mode='lines', 
                        name=f'Channel {i+1}', line=dict(color='black', dash='dot', width=1)),
                row=i + 1, col=1
            );

    # Update layout with a range slider and appropriate axes configurations
    fig.update_layout(
        height=50 * num_channels,  # Adjust the height of subplots
        xaxis_title="",  # Clear any axis title
        xaxis_tickfont=dict(size=10),  # Adjust xaxis font size 
        margin=dict(l=20, r=20, t=20, b=20),  # Reduce margins 
        showlegend=False,
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.01,
                xanchor="left",
                y=1.12,
                yanchor="top",
                font=dict(size=10),
                buttons=[dict(
                    label="Set Range to 3000",
                    method="relayout",
                    args=["xaxis.range", [0, 3000]],  # Sets the range from 0 to 100
                )]
            )
        ]
    );

    fig['layout'][f'xaxis{num_channels}'].update(
        rangeslider=dict(visible=True, thickness=0.02),  # Show last range slider
    );

    for j in range(1, num_channels + 1):
        fig.update_layout(**{f'yaxis{j}': dict(showticklabels=False)});
        
    if save:
        fig.write_html("plot.html")
    # fig.show()
    return fig

# %% ../nbs/99_utility.ipynb 26
def reduce_dimension_with_tsne(array):
    '''
    args:
        array(n, m, d): n is the number of time steps, m is the number of nodes, d is the dimension of the syncmap
    return:
        array(n, m, 2): n is the number of time steps, m is the number of nodes, 2 is the reduced dimension
    '''
    # Step 1: Flatten the first two dimensions
    original_shape = array.shape
    reshaped_array = array.reshape(-1, original_shape[-1])
    
    # Step 2: Apply TSNE to reduce dimensions from 15 to 2
    tsne = TSNE(n_components=2, perplexity=5, random_state=42)
    reduced_array = tsne.fit_transform(reshaped_array)
    
    # Step 3: Reshape the result back to the original first two dimensions with the reduced dimension
    final_array = reduced_array.reshape(original_shape[0], original_shape[1], 2)
    
    return final_array


def create_trace_plot(data, colors = None):
    '''
    args:
        data: np.ndarray, shape (n_frames, n_points, 2)
        colors: list, shape (n_points, ), default None
    '''
    # Validate the shape of the input data
    assert data.shape[2] == 2, "The last dimension of the data must be 2 for 2D coordinates."
    
    # Get the number of frames
    num_frames = data.shape[0]
    num_points = data.shape[1]

    # Determine the ranges for x and y axis
    x_min, x_max = data[:, :, 0].min(), data[:, :, 0].max()
    y_min, y_max = data[:, :, 1].min(), data[:, :, 1].max()

    # Create a color array
    if colors is None:
        colors = ['blue'] * 15 + ['red'] * 15 + ['purple'] * 5

    # Create a figure
    fig = make_subplots(rows=1, cols=1)

    # Initialize the first frame
    scatter = go.Scatter(
        x=data[0, :, 0],
        y=data[0, :, 1],
        mode='markers',
        marker=dict(color=colors)
    )
    
    fig.add_trace(scatter)

    # Update layout for animation
    fig.update_layout(
        width=500,  # 10 inches * 100 pixels per inch
        height=500,  # 10 inches * 100 pixels per inch
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(range=[x_min, x_max], constrain='domain'),
        yaxis=dict(range=[y_min, y_max], scaleanchor="x", scaleratio=1, constrain='domain'),
        # xaxis=dict(range=[x_min, x_max], constrain='domain'),
        # yaxis=dict(range=[y_min, y_max], constrain='domain'),
        # xaxis_range=[x_min, x_max],
        # yaxis_range=[y_min, y_max],
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 800, "redraw": True}, "fromcurrent": True}],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }
        ],
        sliders=[
            {
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "prefix": "Frame:",
                    "visible": True,
                    "xanchor": "right"
                },
                "transition": {"duration": 300, "easing": "cubic-in-out"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [
                            [f],
                            {"frame": {"duration": 300, "redraw": True}, "mode": "immediate", "transition": {"duration": 300}}
                        ],
                        "label": str(f),
                        "method": "animate"
                    }
                    for f in range(num_frames)
                ]
            }
        ]
    )

    # Add frames to the figure
    frames = [
        go.Frame(
            data=[
                go.Scatter(
                    x=data[frame, :, 0],
                    y=data[frame, :, 1],
                    mode='markers', 
                    marker=dict(color=colors)
                )
            ],
            name=str(frame)
        )
        for frame in range(num_frames)
    ]

    fig.frames = frames

    return fig

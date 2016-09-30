import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import seaborn
import pandas as pd
import numpy as np


import venture.lite.value as v

def scatter_plot(x, y, dict_of_plotting_parameters={}):
    plt.scatter(x, y, marker="x", s=200, zorder=2,
                linewidths=2, c = "k")
    if "title" in dict_of_plotting_parameters:
        plt.title(dict_of_plotting_parameters["title"].getString(), fontsize=20)

    if "xlabel" in dict_of_plotting_parameters:
        plt.xlabel(dict_of_plotting_parameters["xlabel"].getString(),
            fontsize=15)
    if "ylabel" in dict_of_plotting_parameters:
        plt.ylabel(dict_of_plotting_parameters["ylabel"].getString(),
            fontsize=15)
    if "xlim" in dict_of_plotting_parameters:
        plt.xlim([lim.getNumber() for lim in dict_of_plotting_parameters["xlim"].getArray()])
    if "ylim" in dict_of_plotting_parameters:
        plt.ylim([lim.getNumber() for lim in dict_of_plotting_parameters["ylim"].getArray()])
    return 0

def line_plot(x, y, dict_of_plotting_parameters={}):
    if "alpha" in dict_of_plotting_parameters:
        alpha = dict_of_plotting_parameters["alpha"].getNumber()
    else:
        alpha = 1
    if "color" in dict_of_plotting_parameters:
        color = dict_of_plotting_parameters["color"].getString()
    else:
        color = "green"

    plt.plot(x, y, color=color, alpha=alpha)

    if "title" in dict_of_plotting_parameters:
        plt.title(dict_of_plotting_parameters["title"].getString(), fontsize=20)

    if "xlabel" in dict_of_plotting_parameters:
        plt.xlabel(dict_of_plotting_parameters["xlabel"].getString())
    if "ylabel" in dict_of_plotting_parameters:
        plt.ylabel(dict_of_plotting_parameters["ylabel"].getString())
    if "xlim" in dict_of_plotting_parameters:
        plt.xlim([lim.getNumber() for lim in dict_of_plotting_parameters["xlim"].getArray()])
    if "ylim" in dict_of_plotting_parameters:
        plt.ylim([lim.getNumber() for lim in dict_of_plotting_parameters["ylim"].getArray()])
    return 0


def kde_plot(dataset, dict_of_plotting_parameters):
    
    df = dataset.datum.asPandas()

    if "xlabel" in dict_of_plotting_parameters:
        xlabel = dict_of_plotting_parameters["xlabel"].getString()
    else:
        raise ValueError("""xlabel must be provided in the
            dict for plotting-parameters""")

    if "ylabel" in dict_of_plotting_parameters:
        ylabel = dict_of_plotting_parameters["ylabel"].getString()
    else:
        raise ValueError("""ylabel must be provided in the
            dict for plotting-parameters""")

    ax = seaborn.kdeplot(df[xlabel], df[ylabel], shade=True)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if "title" in dict_of_plotting_parameters:
        plt.title(dict_of_plotting_parameters["title"].getString(), fontsize=20)

    if "xlim" in dict_of_plotting_parameters:
        plt.xlim([lim.getNumber() for lim in dict_of_plotting_parameters["xlim"].getArray()])
    if "ylim" in dict_of_plotting_parameters:
        plt.ylim([lim.getNumber() for lim in dict_of_plotting_parameters["ylim"].getArray()])
        
    return 0
 
def trajectory_plot(dataset, dict_of_plotting_parameters):

    df = dataset.datum.asPandas()

    if "xlabel" in dict_of_plotting_parameters:
        xlabel = dict_of_plotting_parameters["xlabel"].getString()
    else:
        raise ValueError("""xlabel must be provided in the
            dict for plotting-parameters""")

    if "ylabel" in dict_of_plotting_parameters:
        ylabel = dict_of_plotting_parameters["ylabel"].getString()
    else:
        raise ValueError("""ylabel must be provided in the
            dict for plotting-parameters""")
   
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    if "title" in dict_of_plotting_parameters:
        ax.set_title(dict_of_plotting_parameters["title"].getString(), fontsize=20)
    
    number_of_total_sweeps = len(df)
    df = df.drop_duplicates(subset=[xlabel,ylabel])

    transition_color = np.linspace(0,1,len(df)) 

    # TODO - make this more robust
    if "plot_as_scatter_from" in dict_of_plotting_parameters:
        n_trajectory = int(dict_of_plotting_parameters["plot_as_scatter_from"].getNumber() -1)
    else:
        n_trajectory = len(df)

    if n_trajectory > len(df):
        n_trajectory = len(df)

    # Set the colormap and norm to correspond to the data for which
    # the colorbar will be used.
    cmap = "Greens" 

    ax.plot(df[xlabel].iloc[:n_trajectory], df[ylabel].iloc[:n_trajectory],
        color="gray", zorder = 2, label = "" )
    ax.scatter(df[xlabel].iloc[0], df[ylabel].iloc[0],
        c="white", s=100,
        zorder = 0, label="First of the first %d accepted transitions" % (n_trajectory,))
    ax.scatter(df[xlabel].iloc[:n_trajectory], df[ylabel].iloc[:n_trajectory],
        c=range(n_trajectory), cmap=cmap, s=100,
        zorder = 3, label="Last of the first %d accepted transitions" % (n_trajectory,))
    if n_trajectory < len(df):
        ax.scatter(df[xlabel].iloc[n_trajectory:], df[ylabel].iloc[n_trajectory:],
            label = "Rest of the %d accepted transitions" %\
            (len(df),), zorder = 4) 

    if "xlim" in dict_of_plotting_parameters:
        plt.xlim([lim.getNumber() for lim in dict_of_plotting_parameters["xlim"].getArray()])
    if "ylim" in dict_of_plotting_parameters:
        plt.ylim([lim.getNumber() for lim in dict_of_plotting_parameters["ylim"].getArray()])
    plt.xlabel(xlabel, fontsize=15)
    plt.ylabel(ylabel, fontsize=15)
  
    ax.legend()
    leg = ax.get_legend()
    leg.legendHandles[0].set_color("white")
    leg.legendHandles[1].set_color("green")
    
    '''
    Make a colorbar as a separate figure.
    '''

    from matplotlib import pyplot
    import matplotlib as mpl



    # define the colormap
    cmap = plt.cm.Greens
    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]

    # define the bins and normalize
    bounds = np.linspace(0, n_trajectory -1 , n_trajectory)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)


    # create a second axes for the colorbar
    ax2 = fig.add_axes([0.95, 0.1, 0.03, 0.8])
    cb = mpl.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm, spacing='proportional', ticks=bounds, boundaries=bounds, format='%1i')


    ax2.set_ylabel("Color indicates the i'th accepted transition", size=15)  
    return 0

 
def hist_plot(dataset, title):
    df = dataset.datum.asPandas()
    # last of the column is the collected variable
    df[df.columns[-1]].value_counts().plot(kind="bar")
    plt.ylabel("Frequency of Samples", fontsize=15)
    plt.title(title, fontsize=20)
    return 0

def heatmap(dataset, title):
    df = dataset.datum.asPandas()
    import pdb; pdb.set_trace()
    # last of the column is the collected variable
    df[df.columns[-1]].value_counts().plot(kind="bar")
    plt.ylabel("Frequency of Samples", fontsize=15)
    plt.title(title, fontsize=20)
    return 0

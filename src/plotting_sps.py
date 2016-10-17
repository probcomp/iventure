#TODO: clean up this mess of imports
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import BoundaryNorm
from matplotlib.colors import LogNorm
from matplotlib import colors, ticker, cm
import matplotlib
import pandas as pd
import numpy as np
import seaborn

import venture.lite.value as v

def scatter_plot(x, y, dict_of_plotting_parameters={}):
    seaborn.set()
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
    seaborn.set()
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
    seaborn.set_style("white") 
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
    cmap = plt.cm.Greens_r

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
    leg.legendHandles[0].set_color("green")
    leg.legendHandles[1].set_color("white")
    
    '''
    Make a colorbar as a separate figure.
    '''




    # define the colormap
    cmap = plt.cm.Greens_r
    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]

    # define the bins and normalize
    bounds = np.linspace(0, n_trajectory -1 , n_trajectory)
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)


    # create a second axes for the colorbar
    ax2 = fig.add_axes([0.95, 0.1, 0.03, 0.8])
    cb = matplotlib.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm, spacing='proportional', ticks=bounds, boundaries=bounds, format='%1i')


    ax2.set_ylabel("Color indicates the i'th accepted transition", size=15)  
    return 0
 
def density_line_plot(dataset, dict_of_plotting_parameters):
    seaborn.set()

    # got to select subsamples of the pdf.
    df = dataset.datum.asPandas()
    # last of the column is the collected variable
    x = range(len(df))
    y = df["prt. log wgt."]
    plt.plot(x, y, linestyle="--", marker="o")
    #df["prt. log wgt."].iloc[::10].plot(kind="bar")
    if "title" in dict_of_plotting_parameters:
        plt.title(dict_of_plotting_parameters["title"].getString(), fontsize=20)

    if "xlabel" in dict_of_plotting_parameters:
        plt.xlabel(dict_of_plotting_parameters["xlabel"].getString(),
            fontsize=15)
    if "ylabel" in dict_of_plotting_parameters:
        plt.ylabel(dict_of_plotting_parameters["ylabel"].getString(),
            fontsize=15)
    return 0
 

def density_bar_plot(dataset, dict_of_plotting_parameters):
    seaborn.set()

    # got to select subsamples of the pdf.
    df = dataset.datum.asPandas()
    # last of the column is the collected variable
    print df["prt. log wgt."]
    df["prt. log wgt."].plot(kind="bar")
    #df["prt. log wgt."].iloc[::10].plot(kind="bar")
    if "title" in dict_of_plotting_parameters:
        plt.title(dict_of_plotting_parameters["title"].getString(), fontsize=20)

    if "xlabel" in dict_of_plotting_parameters:
        plt.xlabel(dict_of_plotting_parameters["xlabel"].getString(),
            fontsize=15)
    plt.ylabel("Density", fontsize=15)
    return 0
 
def hist_plot(dataset, title):
    seaborn.set()
    df = dataset.datum.asPandas()
    # last of the column is the collected variable
    df[df.columns[-1]].value_counts().plot(kind="bar")
    plt.ylabel("Frequency of Samples", fontsize=15)
    plt.title(title, fontsize=20)
    return 0

def heatmap(dataset, dict_of_plotting_parameters):
    seaborn.set_style("white")
    df = dataset.datum.asPandas()
    # last of the column is the collected variable
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

    x = df[xlabel]
    y = df[ylabel]
    particle_weights = 0 - df["prt. log wgt."]
    plt.hist2d(x,y, bins = 40, weights = particle_weights, # normalize by
    # subtract max, possibly show the max on the side that I subtraced of. : 
        norm=colors.LogNorm(vmin=np.min(particle_weights),
        vmax=np.max(particle_weights)),  cmap = matplotlib.cm.afmhot_r)
    #seaborn.distplot(particle_weights)
    #plt.scatter(x,y,edgecolors='none',s=1,c=particle_weights ,
    #            norm=colors.LogNorm())

    if "xlim" in dict_of_plotting_parameters:
        plt.xlim([lim.getNumber() for lim in dict_of_plotting_parameters["xlim"].getArray()])
    if "ylim" in dict_of_plotting_parameters:
        plt.ylim([lim.getNumber() for lim in dict_of_plotting_parameters["ylim"].getArray()])

    if "title" in dict_of_plotting_parameters:
        plt.title(dict_of_plotting_parameters["title"].getString(), fontsize=20)

    plt.xlabel(xlabel, fontsize=15)
    plt.ylabel(ylabel, fontsize=15)
    
    return 0

def contour_plot(dataset, dict_of_plotting_parameters):
    matplotlib.rcParams['xtick.direction'] = 'out'
    matplotlib.rcParams['ytick.direction'] = 'out'

    df = dataset.datum.asPandas()
    if "parameter_values_x_axis" in dict_of_plotting_parameters:
        grid_x = [10 * pocket for pocket in dict_of_plotting_parameters["parameter_values_x_axis"].getArray()]
    else:
        raise ValueError(""" the grid must be provided in the
            dict that parameterizes (as key ["grid", array(1,2)] for the contour_plot """)

    if "parameter_values_y_axis" in dict_of_plotting_parameters:
        grid_y = [10 * pocket for pocket in dict_of_plotting_parameters["parameter_values_y_axis"].getArray()]
    else:
        raise ValueError(""" the grid must be provided in the
            dict that parameterizes (as key ["grid", array(1,2)] for the contour_plot """)
                

    delta = 0.025
    X, Y = np.meshgrid(grid_x, grid_y)

    # get the particle weights in terms of neg log probability - because
    # matplotlib does n't do well with negative log values.
    particle_weights = 0 - df["prt. log wgt."].values.reshape(len(grid_x), len(grid_y))

    cut_off_value = 400
    cut_off_value_contours = 120
    particle_weights[particle_weights > cut_off_value]  = cut_off_value 

    # undoing the negation and get the min
    min_particle_weight = - np.max(particle_weights)
    max_particle_weight = - np.min(particle_weights)
    
  
    fig = plt.gcf()
    # define the colormap
    cmap = plt.cm.viridis_r
    axes = fig.get_axes()
    if not axes:
        fig, ax = plt.subplots(1,1, figsize=(6,6))
        ax.set_title("Probability Heatmap")
    else:
        ax = axes[0]
    #ax = seaborn.heatmap(particle_weights, vmin=-100, vmax=-80,
    #xticklabels=grid, yticklabels=grid)
    if "xlim" in dict_of_plotting_parameters:
        ax.set_xlim([lim.getNumber() for lim in dict_of_plotting_parameters["xlim"].getArray()])
    if "ylim" in dict_of_plotting_parameters:
        ax.set_ylim([lim.getNumber() for lim in dict_of_plotting_parameters["ylim"].getArray()])

    #CS = ax.contourf(X, Y, particle_weights, 200,cmap=cm.YlOrBr_r)
    plt.figure(2,figsize=(6,6))

    contour_levels = np.logspace(0, np.sqrt(max_particle_weight - min_particle_weight),
    100, base=1.35) - max_particle_weight 
    contour_levels = contour_levels[contour_levels <= cut_off_value]  
    contour_levels = contour_levels.tolist()
    contour_levels = [-max_particle_weight] + contour_levels + [-min_particle_weight] 
    
    CS2 = ax.contourf(grid_x, grid_y, particle_weights.T, 200, levels=contour_levels, cmap=cmap)


    contour_levels_lines = np.logspace(0, np.sqrt(max_particle_weight - min_particle_weight),
        8, base=1.35) + min_particle_weight - max_particle_weight
    contour_levels_lines = [-min_particle_weight] + contour_levels_lines
    contour_levels_lines = contour_levels_lines[contour_levels_lines <= cut_off_value]  

    CS3 = ax.contour(grid_x, grid_y, particle_weights, colors="black",
        levels=contour_levels_lines)
    for c in CS3.collections:
        c.set_linestyle("dashed")
    fmt = {}
    for level in CS3.levels:
        fmt[level] = "-" +  str(np.round(level)) 
    ax.clabel(CS3, inline=1, fontsize=8, fmt=fmt)


    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]

    # define the bins and normalize
    bounds = np.linspace(min_particle_weight, max_particle_weight, 9) 
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)


    # create a second axes for the colorbar
    ax2 = fig.add_axes([0.1, -0.05, 0.8, 0.03])
    cb = matplotlib.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm,
        spacing='proportional', orientation = 'horizontal', boundaries=bounds, format='%1i')

    labels = [item.get_text() for item in ax2.get_xticklabels()]
    labels[0] = "< - %d" % (cut_off_value,)
    ax2.set_xticklabels(labels[::-1])

    ax2.set_xlabel("Global log joint", size=15)  

    return 0


def gradient_trajectory_plot(dataset, dict_of_plotting_parameters):

  
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

    transition_color = np.linspace(0,1,len(df)) 


    # Set the colormap and norm to correspond to the data for which
    # the colorbar will be used.
    cmap = plt.cm.Greens_r

    ax.plot(df[xlabel], df[ylabel],
        color="gray", zorder = 2, label = "" )
    ax.scatter(df[xlabel].iloc[0], df[ylabel].iloc[0],
        c="white", s=100,
        zorder = 0, label="First gradient step")
    ax.scatter(df[xlabel], df[ylabel],
        c=range(len(df)), cmap=cmap, s=100,
        zorder = 3, label="Last of gradient step")

    if "xlim" in dict_of_plotting_parameters:
        plt.xlim([lim.getNumber() for lim in dict_of_plotting_parameters["xlim"].getArray()])
    if "ylim" in dict_of_plotting_parameters:
        plt.ylim([lim.getNumber() for lim in dict_of_plotting_parameters["ylim"].getArray()])
    plt.xlabel(xlabel, fontsize=15)
    plt.ylabel(ylabel, fontsize=15)
  
    ax.legend()
    leg = ax.get_legend()
    leg.legendHandles[0].set_color("green")
    leg.legendHandles[1].set_color("white")
    
    '''
    Make a colorbar as a separate figure.
    '''



    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]

    # define the bins and normalize
    bounds = np.linspace(0, len(df) -1 , len(df))
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)


    # create a second axes for the colorbar
    ax2 = fig.add_axes([0.95, 0.1, 0.03, 0.8])
    cb = matplotlib.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm, spacing='proportional', boundaries=bounds, format='%1i')


    ax2.set_ylabel("Green indicates the i'th gradient step, from dark to light green", size=15)  
    return 0

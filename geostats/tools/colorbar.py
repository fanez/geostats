'''
Created on Mar 12, 2011

@author: ludifan
'''
'''
Make a colorbar as a separate figure.
'''
import os
os.environ["MPLCONFIGDIR"] = "/tmp"
from matplotlib.ticker import NullFormatter, LogLocator, NullLocator
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colorbar import ColorbarBase


def create_colorbar(cmap, norm, title=None):
    # Make a figure and axes with dimensions as desired.
    fig = Figure(figsize=(4,0.2))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_axes([0.005, 0.1, 0.985, 0.85])

    cb = ColorbarBase(ax, cmap=cmap, norm=norm, orientation='horizontal', format=NullFormatter(), ticks=NullLocator() )
    if title:
        cb.set_label(title, fontsize=12)
    fig.savefig('/home/dotcloud/data/media/plot/colorbar.png', format='png', transparent=True)


if __name__ == "__main__":
    from matplotlib.cm import jet, spring, winter
    from matplotlib.colors import Normalize, LogNorm
    create_colorbar(jet, Normalize(0,1))

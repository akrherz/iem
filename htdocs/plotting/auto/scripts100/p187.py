"""To be determined."""

from pyiem.util import get_autoplot_context
from pyiem.plot.use_agg import plt


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['description'] = """Unused plot type yet."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:', network='IACLIMATE'),
        ]
    return desc


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    (fig, ax) = plt.subplots(1, 1)
    ax.text(0.5, 0.5, 'To Be Determined %s.' % (station, ))

    return fig


if __name__ == '__main__':
    plotter(dict())

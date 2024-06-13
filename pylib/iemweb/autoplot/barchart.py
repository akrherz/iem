"""An opinionated autoplot bar chart."""

from matplotlib.figure import Figure
from matplotlib.table import table
from pandas import DataFrame


def _gen_celltext(data, column, labelformat):
    """Generate the cell text for the top/bottom 10 tables."""
    cell_text = []
    rank = 0
    last_value = None
    for idx, row in data.head(10).iterrows():
        if row[column] != last_value:
            rank += 1
        vv = labelformat % (row[column],)
        cell_text.append([f"#{rank}", f"{idx}", f"{vv}"])
        last_value = row[column]
    return cell_text


def barchar_with_top10(
    fig: Figure,
    data: DataFrame,
    column: str,
    **kwargs,
):
    """Generates a bar chart with the top 10 values at the side and bling.

    Args:
        fig (Figure): matplotlib figure object
        data (DataFrame): pandas dataframe with an index used as x-axis
        column (str): column name to plot
        **kwargs: additional keyword arguments
            ax (matplotlib axis): axis to plot on
            color (str or list-like): color of the bars
            labelformat (str): format string for the labels
            width (float): width of the bars, default 1.

    Returns:
        ax: matplotlib axis object
    """
    ax = kwargs.get("ax")
    if ax is None:
        ax = fig.add_axes([0.1, 0.1, 0.7, 0.8])
    ax.bar(
        data.index,
        data[column],
        width=kwargs.get("width", 1.0),
        color=kwargs.get("color", "b"),
    )
    try:
        ax.ticklabel_format(useOffset=False)
    except AttributeError:
        pass
    cell_text = _gen_celltext(
        data.sort_values(column, ascending=False),
        column,
        kwargs.get("labelformat", "%.1f"),
    )

    axpos = ax.get_position()
    tableax = fig.add_axes(
        [axpos.x1 + 0.02, axpos.y0, 0.96 - axpos.x1, axpos.y1 - axpos.y0],
        frame_on=False,
        xticks=[],
        yticks=[],
    )
    tableax.axhspan(0.95, 1, color="black", alpha=0.1)
    tableax.text(0.5, 0.975, "Top 10", ha="center", va="center")
    top10_table = table(
        tableax,
        cellText=cell_text,
        colLabels=["Rank", data.index.name, column],
        bbox=[0, 0.5, 1, 0.45],
        edges="horizontal",
    )
    top10_table.auto_set_font_size(False)

    cell_text = _gen_celltext(
        data.sort_values(column, ascending=True),
        column,
        kwargs.get("labelformat", "%.1f"),
    )

    tableax.axhspan(0.45, 0.5, color="black", alpha=0.1)
    tableax.text(0.5, 0.475, "Bottom 10", ha="center", va="center")
    bottom10_table = table(
        tableax,
        cellText=cell_text,
        colLabels=["Rank", data.index.name, column],
        bbox=[0, 0, 1, 0.45],
        edges="horizontal",
    )
    bottom10_table.auto_set_font_size(False)
    tableax.set_xlim(0, 1)
    tableax.set_ylim(0, 1)

    return ax

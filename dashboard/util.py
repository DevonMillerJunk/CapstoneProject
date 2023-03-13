import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

LOGO_PATH = "../images/frequensea.png"

def gen_scatter(title: str, y_data: list[float], x_data: list[float], y_label: str, x_label: str, colour: str)-> go.Figure:
    fig: go.Figure = go.Figure([go.Scatter(x=x_data, y=y_data, line=dict(color=colour))])
    fig.update_layout(
        title=title,
        title_font =dict(size=24),
        title_y = 0.94,
        xaxis_title=x_label,
        yaxis_title=y_label,
        font = dict(
            size=16,
        ),
        margin=dict(l=60, r=20, t=50, b=80)
    )
    return fig
    

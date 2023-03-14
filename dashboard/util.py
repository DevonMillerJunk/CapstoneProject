import streamlit as st
import plotly.graph_objects as go

LOGO_PATH = "../images/frequensea.png"

def gen_scatter(title: str, y_data: list[float], x_data: list[float], y_label: str, x_label: str, colour: str, yaxis_range=None)-> go.Figure:
    fig: go.Figure = go.Figure([go.Scatter(x=x_data, y=y_data, line=dict(color=colour))])
    fig.update_layout(
        title=title,
        title_font =dict(size=24),
        xaxis = go.layout.XAxis(nticks = 3, tickformat = '%I:%M:%S %p', tickangle=15, minor=dict(showgrid=True)),
        yaxis= go.layout.YAxis(title=y_label, range=yaxis_range),
        font = dict(
            size=16,
        ),
        margin=dict(t=36),
    )
    return fig
    

def gen_metric_delta(data: list[float]):
    cur_value = data[-1]
    if len(data) == 1:
        return cur_value, 0

    prev_value = data[-2]

    delta_value = cur_value - prev_value

    return cur_value, delta_value
    

def select_messages(data: list[str]):
    if len(data) == 1:
        return f"<div> <span class='highlight red'><span class='bold'> <span class='wrap'> \
            {st.session_state['messages'][-1]}</span> </span></span><div>"

    elif len(data) == 2:
        return f"<div> <span class='highlight red'><span class='bold'><span class='wrap'> \
            {st.session_state['messages'][-1]}</span> </span></span> \
            <br><br> \
            <span class='highlight green'><span class='wrap'> \
            <span class='bold'>{st.session_state['messages'][-2]}</span></span></span><div>"

    return f"<div> <span class='highlight red'><span class='bold'><span class='wrap'> {st.session_state['messages'][-1]}</span></span></span>\
            <br><br>\
            <span class='highlight green'> <span class='bold'><span class='wrap'>{st.session_state['messages'][-2]}</span></span></span>\
            <br><br> \
            <span class='highlight blue'> <span class='bold'><span class='wrap'>{st.session_state['messages'][-3]}</span></span></span><div>"
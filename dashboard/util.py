import streamlit as st
import plotly.graph_objects as go

LOGO_PATH = "../images/frequensea.png"

def gen_header(title: str):
    hdr_col1, hdr_col2, hdr_col3, hdr_col4 = st.columns([1,2,2,1])
    with hdr_col1:
        st.write("")
    with hdr_col2:
        st.image(LOGO_PATH)
    with hdr_col3:
        st.title(title)
    with hdr_col4:
        st.write("")

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
    
def gen_message_html(message: str, colour: str) -> str:
    return f"<span class='highlight {colour}'><span class='bold'><span class='wrap'>{message}</span></span></span>"

def select_messages(data: list[str]):
    colours = ["red", "green", "blue"]
    return f"<div>{'<br><br>'.join([gen_message_html(x, colours[i%len(colours)]) for i,x in enumerate(data)])}</div>"
            
def format_bits(num_bits: int) -> str:
    if num_bits < 1000:
        return f'{num_bits}b'
    elif num_bits < 1000 * 1000:
        return f'{round((num_bits / 1000.0),3)}kb'
    elif num_bits < 1000 * 1000 * 1000:
        return f'{round((num_bits / 1000000.0),3)}mb'
    else:
        return f'{round((num_bits / 1000000000.0),3)}gb'
    
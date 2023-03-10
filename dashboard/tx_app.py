import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import plotly.graph_objects as go

LOGO_PATH = "../images/frequensea.png"

# Generate random data for testing dashboard
def generate_random_data(msg):
    bit_rate = random.randint(500, 1000)
    drop = random.randint(0,10)
    return bit_rate, drop

# Generate plots side by side using columns
def generate_side_by_side_plots(bit_rates, dropped_pkts):
    x_data = np.arange(len(bit_rates))

    # plot 1
    br_fig = go.Figure([go.Scatter(x=x_data, y=bit_rates, line=dict(color="#FF9933"))])
    generate_plot_layout(br_fig, "Bit Rate of Transmission", "Bit Rate (bps)")  
    col1.plotly_chart(br_fig, use_container_width=True, theme=None)
    

    # plot 2
    drop_pkt_fig = go.Figure([go.Scatter(x=x_data, y=dropped_pkts, line=dict(color="#23A5A5"))])
    generate_plot_layout(drop_pkt_fig, "Dropped Packets", "% Dropped Packets")  
    col2.plotly_chart(drop_pkt_fig, use_container_width=True, theme=None)

# Generate plots one on top of the other
def generate_stacked_plots(bit_rates, dropped_pkts):
    x_data = np.arange(len(bit_rates))

    # plot 1
    br_fig = go.Figure([go.Scatter(x=x_data, y=bit_rates, line=dict(color="#FF9933"))])
    generate_plot_layout(br_fig, "Bit Rate of Transmission", "Bit Rate (bps)")  
    st.plotly_chart(br_fig, use_container_width=True, theme=None)

    # plot 2
    drop_pkt_fig = go.Figure([go.Scatter(x=x_data, y=dropped_pkts, line=dict(color="#23A5A5"))])
    generate_plot_layout(drop_pkt_fig, "Dropped Packets during Transmission", "% Dropped Packets")  
    st.plotly_chart(drop_pkt_fig, use_container_width=True, theme=None)

# Define Layout Components of Graph Figure 
def generate_plot_layout(fig: go.Figure, title: str, yaxis_title: str):
    fig.update_layout(
        title=title,
        title_font =dict(size=24),
        title_y = 0.94,
        xaxis_title="Sample Number",
        yaxis_title=yaxis_title,
        font = dict(
            size=16,
        ),
        margin=dict(l=60, r=20, t=50, b=80)
    )
    return fig

# Get data and store in session state
def get_data_session_state():

    # Get current state and user input
    tx_str = st.session_state['tx_str']
    session_state_data = st.session_state['msg_data']
    print(f"Sending Message {tx_str}")

    # Display loading spinner
    with st.spinner(text="Sending ... "):
        # Need to send data using Raspberry Pi Here
        # Generating Random Data for now
        cur_br, cur_err = generate_random_data(tx_str)
        session_state_data[tx_str] = [cur_br, cur_err]
        # I added a sleep to try to mimic potential slowness of ssh connection, probably not needed
        time.sleep(1)
    
    print("Create Graph")
    # Format bit rate and dropped_pkts into two lists for graphing
    bit_rates, dropped_pkts = map(list, zip(*session_state_data.values()))

    # Use Plotly to graph
    # generate_side_by_side_plots(bit_rates, dropped_pkts)
    generate_stacked_plots(bit_rates, dropped_pkts)
    print("Done")



# Define session state keys to store required information
# 'msg_data' is a dictionary with key = user input, values = list(bit rate, dropped pkt %)
# 'tx_str' is a string recording the user input into the text input field
if "msg_data" not in st.session_state:
    st.session_state['msg_data'] = {}
if "tx_str" not in st.session_state:
    st.session_state['tx_str'] = ""

# Define Streamlit elements
st.header('Transmitter - Communication Metrics')
st.sidebar.image(LOGO_PATH, width=300)
st.sidebar.title('FYDP Demo - Try it Out!')

# Used for Side By Side Plots - Not currently used
col1, col2 = st.columns(2)

# Define sidebar to have user input part
with st.sidebar:
    send_str = st.text_input("Send a Message", value="", key='tx_str')
    st.write(f"Debugging - Input string - {send_str}")

# If message entered then send data and generate graph
if send_str:
    get_data_session_state()

# No message - prompt user to send message
else: 
    st.write(f"Send a Message to see Results")


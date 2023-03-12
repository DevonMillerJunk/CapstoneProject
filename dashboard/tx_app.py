import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import util as u
from queue import Queue
from ssh_connection import RpiA

def init_state():
    # Define session state keys to store required information
    if "msg_queue" not in st.session_state:
        # Producer queue of messages to send
        st.session_state['msg_queue'] = Queue()
    if "data_queue" not in st.session_state:
        # Consumer queue of data to receive
        st.session_state['data_queue'] = Queue()
    if "bit_rate_data" not in st.session_state:
        # Array of bit rate data
        st.session_state['bit_rate_data'] = []
    if "pkt_drop_data" not in st.session_state:
        # Array of packet drop rate data
        st.session_state['pkt_drop_data'] = []
        
def send_message(msg: str):
    try:
        st.session_state['msg_queue'].put_nowait(msg)
    except Exception as e:
        print(f'Error sending a message: {e}')
    
def recv_messages():
    try:
        while not st.session_state['data_queue'].empty():
            (bit_rate, pkt_drop_rate) = st.session_state['data_queue'].get_nowait()
            st.session_state['bit_rate_data'].append(bit_rate)
            st.session_state['pkt_drop_data'].append(pkt_drop_rate)
    except Exception as e:
        print(f'Error reading from queue: {e}')
        
def init_layout():
    # Title
    st.header('Transmitter - Communication Metrics')
    
    # Sidebar
    st.sidebar.image(u.LOGO_PATH, width=300)
    st.sidebar.title('FYDP Demo - Try it Out!')
    send_str = None
    with st.sidebar:
        send_str = st.text_input("Send a Message", value="", key='tx_str')
        st.write(f"Debugging - Input string - {send_str}")
    if send_str:
        send_message(send_str)
        
    # Graphs
    x_data = np.arange(len(st.session_state['bit_rate_data']))
    bit_rate_graph: go.Figure = u.gen_scatter("Bit Rate", st.session_state['bit_rate_data'], x_data, "Bit Rate", "Time", "#FF9933")
    st.plotly_chart(bit_rate_graph, use_container_width=True, theme=None)
    pkt_drop_graph: go.Figure = u.gen_scatter("Dropped Packet Rate", st.session_state['pkt_drop_data'], x_data, "Dropped Packets", "Time", "#23A5A5")
    st.plotly_chart(pkt_drop_graph, use_container_width=True, theme=None)
        
    

# Message: queue of messages to send
# Data: queue of data from the pi
@st.cache_resource
def init_ssh_connection(_messages: Queue, _data: Queue)-> RpiA:
    r_pi = RpiA(_messages, _data)
    r_pi.exec()
    return r_pi


# Define session state keys to store required information
init_state()
r_pi: RpiA = init_ssh_connection(st.session_state['msg_queue'], st.session_state['data_queue'])
recv_messages()
init_layout()




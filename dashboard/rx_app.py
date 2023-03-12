import streamlit as st
import numpy as np
import plotly.graph_objects as go
import util as u
from queue import Queue
from ssh_connection import RpiB
from streamlit_autorefresh import st_autorefresh

def init_state():
    # Define session state keys to store required information
    if "msg_queue" not in st.session_state:
        # Consumer queue of messages received
        st.session_state['msg_queue'] = Queue()
    if "data_queue" not in st.session_state:
        # Consumer queue of data to received
        st.session_state['data_queue'] = Queue()
    if "bit_rate_data" not in st.session_state:
        # Array of bit rate data
        st.session_state['bit_rate_data'] = []
    if "pkt_drop_data" not in st.session_state:
        # Array of packet drop rate data
        st.session_state['pkt_drop_data'] = []
    if "messages" not in st.session_state:
        # Array of messages received
        st.session_state['messages'] = []
    
def recv_data():
    try:
        while not st.session_state['data_queue'].empty():
            (bit_rate, pkt_drop_rate) = st.session_state['data_queue'].get_nowait()
            st.session_state['bit_rate_data'].append(bit_rate)
            st.session_state['pkt_drop_data'].append(pkt_drop_rate)
        while not st.session_state['msg_queue'].empty():
            msg = st.session_state['msg_queue'].get_nowait()
            st.session_state['messages'].append(msg)
    except Exception as e:
        print(f'Error reading from queue: {e}')
        
def init_layout():
    ### Title
    st.header('Receiver - Communication Result')
    
    ### Sidebar
    st.sidebar.image(u.LOGO_PATH, width=300)
    st.sidebar.title('FYDP Demo - Try it Out!')
    with st.sidebar:
        if st.button("Update Date"):
            recv_data()
            
    col1, col2, col3 = st.columns(3)
        
    ### Graphs
    x_data = np.arange(len(st.session_state['bit_rate_data']))
    # Bit rate
    with col1:
        bit_rate_graph: go.Figure = u.gen_scatter("Bit Rate", st.session_state['bit_rate_data'], x_data, "Bit Rate", "Time", "#FF9933")
        st.plotly_chart(bit_rate_graph, use_container_width=True, theme=None)
    # Packet Drop Rate
    with col2:
        pkt_drop_graph: go.Figure = u.gen_scatter("Dropped Packet Rate", st.session_state['pkt_drop_data'], x_data, "Dropped Packets", "Time", "#23A5A5")
        st.plotly_chart(pkt_drop_graph, use_container_width=True, theme=None)
    # Received Messages
    with col3:
        st.caption(','.join(st.session_state['messages']), unsafe_allow_html=False)

# Message: queue of messages to recv
# Data: queue of data to recv
@st.cache_resource
def init_ssh_connection(_messages: Queue, _data: Queue)-> RpiB:
    r_pi = RpiB(_messages, _data)
    r_pi.exec()
    return r_pi

# Refresh every 10 seconds
st_autorefresh(interval=10 * 1000, key="recv_refresh")

# Define session state keys to store required information
init_state()
r_pi: RpiB = init_ssh_connection(st.session_state['msg_queue'], st.session_state['data_queue'])
recv_data()
init_layout()




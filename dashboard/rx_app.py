import streamlit as st
st.set_page_config(layout="wide")
import numpy as np
import plotly.graph_objects as go
import util as u
from queue import Queue
from ssh_connection import RpiB
from streamlit_autorefresh import st_autorefresh
import base64
from datetime import datetime

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
    if "num_bits_recv" not in st.session_state:
        # Total Bits Received
        st.session_state['num_bits_recv'] = 0
    if "pkt_drop_data" not in st.session_state:
        # Array of packet drop rate data
        st.session_state['pkt_drop_data'] = []
    if "messages" not in st.session_state:
        # Array of messages received
        st.session_state['messages'] = []
    if "num_messages" not in st.session_state:
        # Number of messages received
        st.session_state['num_messages'] = 0
    if "timestamp" not in st.session_state:
        # Number of messages received
        st.session_state['timestamp'] = []

def load_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

def recv_data():
    try:
        while not st.session_state['data_queue'].empty():
            (bit_rate, num_bits, pkt_drop_rate) = st.session_state['data_queue'].get_nowait()
            st.session_state['timestamp'].append(datetime.now())
            st.session_state['bit_rate_data'].append(bit_rate)
            st.session_state['pkt_drop_data'].append(pkt_drop_rate)
            st.session_state['num_bits_recv'] += num_bits
        while not st.session_state['msg_queue'].empty():
            msg = st.session_state['msg_queue'].get_nowait()
            st.session_state['messages'].append(msg)
            st.session_state['num_messages'] += 1
    except Exception as e:
        print(f'Error reading from queue: {e}')

def init_layout():

    num_to_plot = 200 # Maximum # of Data Points to Plot

    ### Title Header
    st.markdown(
        f"""
        <div class="block-container">
            <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(u.LOGO_PATH, "rb").read()).decode()}" style="width:300px;height:80px">
            <p class="logo-text">Receiver - Communication Results</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("""---""")

    recv_data()
            
    col1, col2, col3, col4 = st.columns((2,2,1,1))
        
    ### Graphs
    x_data = st.session_state['timestamp'][-num_to_plot:]

    # Bit Rate Graph
    with col1:
        # Plot Graph
        bit_rate_graph: go.Figure = u.gen_scatter("Bit Rate", st.session_state['bit_rate_data'][-num_to_plot:], x_data, "Bit Rate (bps)", "Time", "#FF9933")
        st.plotly_chart(bit_rate_graph, use_container_width=True, theme=None)
        
    # Packet Drop Rate Graph
    with col2:
        # Create Graph
        pkt_drop_graph: go.Figure = u.gen_scatter("Dropped Packet Rate", st.session_state['pkt_drop_data'][-num_to_plot:], x_data, "% Dropped Packets", "Time", "#23A5A5", [0,100])
        st.plotly_chart(pkt_drop_graph, use_container_width=True, theme=None)
    
    # Metrics
    with col3:

        if len(st.session_state['bit_rate_data']) > 0:
            cur_bit_rate, delta_bit_rate = u.gen_metric_delta(st.session_state['bit_rate_data'])
            st.metric(
                label="Bit Rate", 
                value= f"{cur_bit_rate} bps", 
                delta= f"{delta_bit_rate} bps",
            )

        # Create Metric
        if len(st.session_state['pkt_drop_data']) > 0:
            cur_drop_rate, delta_drop_rate = u.gen_metric_delta(st.session_state['pkt_drop_data'])
            st.metric(
                label="% Dropped Packets", 
                value= f"{cur_drop_rate} %", 
                delta= f"{delta_drop_rate} %",
            )

        st.metric(
                label="Number of Messages Received", 
                value= f"{st.session_state['num_messages']}", 
            )

        st.metric(
                label="Number of Bits Received", 
                value= f"{st.session_state['num_bits_recv']}", 
            )
    
    # Display Received Messages
    with col4:
        st.subheader('Last 3 Messages:')
        if len(st.session_state['messages']) > 0:
            msgs = u.select_messages(st.session_state['messages'])

            st.markdown(msgs, unsafe_allow_html=True)
        
        #st.caption(','.join(st.session_state['messages']), unsafe_allow_html=False)

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
load_css("style.css")
r_pi: RpiB = init_ssh_connection(st.session_state['msg_queue'], st.session_state['data_queue'])
recv_data()
init_layout()




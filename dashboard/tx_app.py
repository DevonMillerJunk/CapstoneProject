import streamlit as st
import util as u
from queue import Queue
from ssh_connection import RpiA

def init_state():
    # Define session state keys to store required information
    if "msg_queue" not in st.session_state:
        # Producer queue of messages to send
        st.session_state['msg_queue'] = Queue()
        
def send_message(msg: str):
    try:
        st.session_state['msg_queue'].put_nowait(msg)
    except Exception as e:
        print(f'Error sending a message: {e}')
        
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
        
# Message: queue of messages to send
@st.cache_resource
def init_ssh_connection(_messages: Queue)-> RpiA:
    r_pi = RpiA(_messages)
    r_pi.exec()
    return r_pi

# Define session state keys to store required information
init_state()
r_pi: RpiA = init_ssh_connection(st.session_state['msg_queue'])
init_layout()
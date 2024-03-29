import streamlit as st
from streamlit_space import space
import util as u
from queue import Queue
from ssh_connection import RpiA
st.set_page_config(layout="wide")


sample_code = """
node = frequensea.LoRa_socket(addr=9)
print("determine if any nearby nodes are active")
conn_address = node.connect()
if conn_address is None:
    raise Exception("Unable to establish connection")
    
print(f'Connection established to node {conn_address}')
while True:
    # Send a message received from the user
    message = input("Message to Send:")
    node.send(message.encode(), conn_address)
    
    # Check if we received a message
    received_message = node.recv(timeout=5)
    if received_message is not None:
        (payload, recv_address) = received_message
        print(payload.decode())
"""

def init_state():
    # Define session state keys to store required information
    if "msg_queue" not in st.session_state:
        # Producer queue of messages to send
        st.session_state['msg_queue'] = Queue()
        
def send_message():
    msg = st.session_state.tx_str
    try:
        st.session_state['msg_queue'].put_nowait(msg)
    except Exception as e:
        print(f'Error sending a message: {e}')
    finally:
        st.session_state.tx_str = ''
        
def display_elements():
    c = st.container()
    with c.expander("LoRa Chirp Spectrum"):
        st.image("../images/chirp-spectrum.png", caption="LoRa Chirp Spread Spectrum Example")
        st.write("""
            LoRa, or Long Range, communication takes advantage of the Chirp Spread Spectrum (CSS) as its modulation technique.
            CSS is a form of frequency modulation in which the carrier frequency increases or decreases across a range for each transmitted symbol (a chirp).
            The result is a continuous waveform with an increasing or decreasing frequency across the symbol. 
            The result is that the signal is wide band, with a lower data rate, but vastly increase range, and ability to deal with interference.
            LoRa is also extremely useful for low power communication. 
            When combined with high-gain and/or directional antennas, LoRa is extremely effective at long range communication, and can reach up to 20km with low power.
            As a result, LoRa is the standard today for all IoT devices, and happens to work perfectly underwater.
        """)
    
    with c.expander("Our Waterproof Container"):
        col1, col2 = st.columns([5,2])
        with col2:
            st.image("../images/container.jpg", caption="Inside Our Container")
        with col1:
            st.write("""
                Our 3D-printed container was designed to keep the electronics safe from water while in operation.
                The initial prototype container was composed of seven modular components used for design iterations. 
                Once the design was finalized, the components were glued together with a plastic bonding epoxy and tested underwater. 
                We chose to use PLA+ to print our container, as it results in a stronger print than regular PLA. 
                The container was printed with three outer layers to increase rigidity and minimize microscopic gaps through which water could enter, and with a cubic infill pattern with a density of 20%. 
                They were also printed with a variable layer height, which allowed us to increase the printing speed while preserving dimensional accuracy and fine details. 
                The final prototypes were printed as three solid pieces with two smaller pieces used to secure the electronics inside. 
                This avoided the need for epoxy and significantly reduced the risk of water entering the container through microscopic gaps between the components. 
                The internal electronics mounting components allow us to easily secure and remove the electronics when maintenance is necessary.

                The biggest concern when waterproofing the container was the design of the lids.
                We chose a threaded lid design that screws into the container, as it maximizes the surface area between the lid and the container, and, when combined with a thin layer of plumber's tape, the extra surface area provided a better barrier between the inside of our container and the water.
                As a precaution, a layer of waterproof caulk was carefully applied to a groove in the top of the container, which creates an extra seal when the lid is fully in place. 
            """)
        
    with c.expander("Testing our Project"):
        col1, col2 = st.columns([2,3])
        with col1:
            st.image("../images/river-testing.jpg", caption="Testing in Waterloo Park")
        with col2:
            st.write("""
                Testing of our underwater radios in different conditions was essential to evaluating the performance of the system.
                We needed to test in different environmental conditions, at different ranges, and at different depths.
                The radios were evaluated in clear (tap) water and murky river water at ranges of up to 12 meters to determine how resilient the system was.
                We can be seen in the picture to the left testing in the Waterloo Park Creek, with extremely murky water, and yet the system performs well and is able to achieve a bit rate of 1.765kbps.
                During testing, it was essential to record and analyze the performance of the radio, including the frequency of dropped packets, frequency of bit errors, and types of bit errors.
                From this information, we ensured that the system met and exceeded our requirements.
            """)
            st.image("../images/river-test-results.png", caption="Test Results from Waterloo River")
        
    with c.expander("Simple Library"):
        col1, col2 = st.columns([3,5])
        with col2:
            st.code(sample_code, language="python")
        with col1:
            st.write("""
                Our easy-to-use Python library for communicating over radio through a Raspberry Pi is the "frequensea" library.
                This library allows users to communicate between our frequensea devices, including underwater! 
                The library abstracts away all the complexity required for controlling radio frequency (RF) transmitters and receivers, such as the packetization, networking, and error encoding. 
                With the frequensea library, users can easily create scripts to send and receive data over radio, making it an ideal tool for projects that require wireless communication. 
                The library is well-documented, with clear examples, making it accessible even to those new to programming or radio communication.
            """)
        
def init_layout():
    # Title
    u.gen_header("Transmitter")
    space(lines=4)
        
    # Input
    inp_col1, inp_col2, inp_col3 = st.columns([2,6,2])
    with inp_col1:
        st.write("")
    with inp_col2:
        st.text_input(label=':orange[Try Sending a Message:]', key='tx_str', on_change=send_message, help="Look at the receiver dashboard to see your message appear!")
    with inp_col3:
        st.write("")
        
    space(lines=8)

    # Images
    img_col1, img_col2, img_col3 = st.columns([1,7,1])
    with img_col1:
        st.write("")
    with img_col2:
        display_elements()
    with img_col3:
        st.write("")
    
        
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
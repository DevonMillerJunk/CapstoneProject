import streamlit as st
import pandas as pd
import random
import string

LOGO_PATH = "../images/frequensea.png"

# Generate random data for testing received Data
def check_for_received_data(lent=6):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(lent))
    st.session_state['rx_data'].append(result_str)
    return result_str

if "rx_data" not in st.session_state:
    st.session_state['rx_data'] = []

# Define Streamlit elements
st.header('Receiver - Communication Result')
st.sidebar.image(LOGO_PATH, width=300)
st.sidebar.title('FYDP Demo - Try it Out!')
rec_msg = None

# Created Button that you could click to check for messages 
with st.sidebar:
    if st.button("Check for New Messages"):
        rec_msg = check_for_received_data()

# if msg is received then print msg and table of all messages with number of bits sent next to it
if rec_msg:
    st.subheader(f'Received New Message: {rec_msg}') 

    st.markdown("""---""")

    str_bytes = [len(s.encode('utf-8'))*8 for s in st.session_state['rx_data']]

    received_data = pd.DataFrame(
        {
            "Received Data": st.session_state['rx_data'],
            "Received Bits": str_bytes
        }
    )

    st.dataframe(received_data)

else:
    st.text("Waiting For Message")

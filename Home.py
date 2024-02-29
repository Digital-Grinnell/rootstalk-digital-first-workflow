# Home.py
#  

import streamlit as st
from streamlit.logger import get_logger
import traceback
import utils

LOGGER = get_logger(__name__)


# Page code goes here...

def main( ):
    
    # Initialize the session_state
    st.session_state.status = False

    st.write("# Welcome to my Streamlit Template! :smile:")

    st.sidebar.success("This is sidebar.success in Home.py!")

    st.markdown(
        """
        **This is some lengthy Markdown...
    
        .............................................................
        .............................................................
        .............................................................
        .............................................................
        """
    )

    # Wrap all of the processing in a nice try...except
    try:

        # Home code here
        pass
 
    # Now, handle all exceptions gracefully
    except Exception as e:
        st.write(traceback.print_exc( ))
        pass

    utils.show_session( )
    utils.show_code(main)


# Other functions here...

def other_functions( ):
    pass


# Config the page and execute it but not when loading!

if __name__ == "__main__":
    st.set_page_config(page_title="Home",page_icon=":smile:")
    main( )


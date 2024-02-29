# Home.py
#   Previously this was `Hello.py`

import streamlit as st
from streamlit.logger import get_logger
import pycaching
import traceback
import utils

LOGGER = get_logger(__name__)


# Page code goes here...

def main( ):
    
    # Initialize the session_state
    st.session_state.username = None
    st.session_state.connected = False
    st.session_state.query_mode = None
    st.session_state.caches = None

    # Show only the available pages
    # utils.show_initial_pages( )

    st.write("# Welcome to Geocaching with Streamlit! :smile:")

    st.sidebar.success("This is sidebar.success in Home.py!")

    st.markdown(
        """
        **Mark's Geocaching.com Nirvana?  Maybe?  Eventually?**

        This app has two modes of operation... 
          - Login and query _Geocaching.com_ for `live` cache data, or
          - Load caches from a pocket query or other available `gpx` file.
        """
    )

    # Wrap all of the processing in a nice try...except
    try:

        # Select the mode you wish to use
        choices = [ "Live", "GPX" ]
        captions = [ ":question: Login and query Geocaching.com for `live` cache data", ":open_file_folder: Load cache data from an available `.gpx` file" ]
        mode = st.radio(f"Select 'Live' or 'GPX' mode.", choices, captions=captions)
        st.session_state.mode = mode

        if mode == "Live":
            pass
    
        if mode == "GPX":
            utils.show_GPX_pages( )
        

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


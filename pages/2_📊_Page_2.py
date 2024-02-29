# Page_1.py
#

import streamlit as st
from utils import show_session, show_code


# Page code goes here...
#-----------------------------------------------------------------------

def main( ):

    # Do some stuff here
    st.sidebar.success(f"This is Page_1 st.sidebar.success( ).")

    show_session( )
    show_code(main)
    
    return 


# Other functions here...
#-----------------------------------------------------------------------

def a_local_function( ):

    # Do some function stuff here
    
    return


# Config the page and execute it but not when loading!
#-----------------------------------------------------------------------

if __name__ == "__main__":
    st.set_page_config(page_title="Page One", page_icon="📂")
    st.markdown("# Page 1 Markdown")
    st.write("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")
    st.sidebar.header("Page 1 Sidebar Header")
    st.session_state.status = "This is session_state.status from Page 1"

    # Call main( )
    main( )

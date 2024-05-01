# utils.py

import streamlit as st
import inspect
import textwrap
import constants
from st_pages import Page, show_pages, add_page_title



# Streamlit icons from https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/

# menu( ) - Define and display our dynamic page menu
# -------------------------------------------------------------------------------
def menu(top_of_page=True):

    # Streamlit icons from https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/

    # Keep the menu expanded.  
    # From https://discuss.streamlit.io/t/how-to-keep-the-pages-menu-expanded-in-multipage-apps/40775/4
    
    st.markdown("""
    <style>
    div[data-testid='stSidebarNav'] ul {max-height:none}</style>
    """, unsafe_allow_html=True)

    # Build the pages
    pages = [   Page("./pages/🏠_Home.py", "Home", "🏠"), 
                Page("./pages/1_🦣_DOCX → Mammoth → HTML.py", "DOCX → 🦣 → HTML", "🦣"),
                Page("./pages/2_🐍_HTML → Python → Markdown.py", "HTML → 🐍 → Markdown", "🐍")  ]
    
    if top_of_page:
        add_page_title( )         # necessary for indentation
    
    show_pages(pages)

    # Put the message level selector in the sidebar.   Cannot disable Error messages!
    if not state('msg_level'):
        st.session_state.msg_level = 'All'
    st.session_state.msg_level = st.sidebar.select_slider("Message Severity", options=['Warning', 'Info', 'Debug', 'All'], value=state('msg_level'))   


# state(key) - Return the value of st.session_state[key] or False
# -------------------------------------------------------------------------------
def state(key):
    try:
        if st.session_state[key]:
            return st.session_state[key]
        else:
            return False
    except Exception as e:
        # st.exception(f"Exception: {e}")
        return False


# show_session( ) - Display st.session_state 
# -------------------------------------------------------------------------------
def show_session( ):
    """Showing the st.session_state."""
    show_session = st.sidebar.checkbox("Show session_state", False)
    if show_session:
        # Showing the st.session_state.
        st.markdown("## Session State")
        st.write("st.session_state object:", st.session_state)


# show_code( ) - Display the named code 
# -------------------------------------------------------------------------------
def show_code(main):
    """Showing the page code."""
    show_code = st.sidebar.checkbox("Show code", False)
    if show_code:
        # Showing the code of the demo.
        st.markdown("## Code")
        sourcelines, _ = inspect.getsourcelines(main)
        st.code(textwrap.dedent("".join(sourcelines[1:])))



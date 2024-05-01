# 🏠_Home.py
#
# ----------------------------------------------------------------------------------
# This is a multi-page Streamlit (https://streamlit.io/) app built from
# https://github.com/SummittDweller/streamlit-multipage-template.  It leverages
# 'mammoth' (the Python version from https://github.com/mwilliamson/python-mammoth)
# to transform a single "article" presented as an MS Word .docx file, one presumably 
# formatted with Rootstalk styles, into an intermediate HTML (.html) file using a 
# special Rootstalk style map (rootstalk-custom-style.map), then into a Markdown (.md) 
# file suitable for clean-up and subsequent publication in the digital edition of 
# Rootstalk (https://rootstalk.grinnell.edu).
# 
# See VSCode Python setup at https://blog.summittdweller.com/posts/2022/09/proper-python/

import streamlit as st
from streamlit.logger import get_logger
from utils import *
import traceback
import constants as c


LOGGER = get_logger(__name__)

if not state('aFrontmatter'):
    st.session_state.aFrontmatter = c.fm_template    # initialize 'aFrontmatter' in our session state


# Page code goes here...
#------------------------------------------------------------------------------

def main( ):
    
    # Initialize the session_state, including some CONSTANTs
    if not state('working_dir'):
        st.session_state.working_dir = c.default_path
    if not state('html_path'):
        st.session_state.html_path = False
    if not state('aIndex'):
        st.session_state.aIndex = 1
    if not state('aName'):
        st.session_state.aName = False
    if not state('aFrontmatter'):
        st.session_state.aFrontmatter = False
    if not state('show_markdown'):
        st.session_state.show_markdown = False

    # Explain the OneDrive prep required before running this app...
    
    md = [ ]

    md.append("This app assumes that you have already COPIED the contents of Professor Baechtel's OneDrive, specifically the `Rootstalk, Spring 2024` : `Digital-Versions` subdirectory, to YOUR OWN OneDrive and subsequently SYNC(hronized) that copy with your workstation.  ")

    md.append("To make a COPY, open the `Digital-Versions` directory in [Mark B's OneDrive](https://grinco-my.sharepoint.com/personal/baechtel_grinnell_edu/Documents/Forms/All.aspx?RootFolder=%2Fpersonal%2Fbaechtel%5Fgrinnell%5Fedu%2FDocuments%2FRootstalk%2FRootstalk%2C%20Spring%202024%2FDigital%2DVersions&FolderCTID=0x012000A6C31E30BF003640A2D7B60A01D853B7&View=%7BB15D8612%2DAF44%2D4DC9%2D8513%2D5154D5D906C9%7D), select one or more files and/or directories, then click `More v` and then `Move or copy`.   Make sure you select the `Copy this item to the selected folder`, then pick your own `OneDrive` and a destination folder (like `Digital-Versions`) within.")

    md.append("Now, to sync with your workstation open YOUR `OneDrive`, navigate to YOUR aforementioned subdirectory and click on the `Sync` option.  You may be prompted for your Grinnell login credentials before the directory is sync'd to your workstation.  On a Mac the sync'd local folder is likely to be `~/Library/CloudStorage/OneDrive-GrinnellCollege/Digital-Versions`, and that is the default path in this app.")

    for paragraph in md:
        st.write(paragraph)

    # Wrap all of the processing in a nice try...except
    try:

        # Home code here
        pass

    # Now, handle all exceptions gracefully
    except Exception as e:
        st.write(traceback.print_exc( ))
        pass

    show_session( )
    show_code(main)


# Other functions here...
# ----------------------------------------------------------------------
def other_functions( ):
    pass


# Config the page and execute it but not when loading!
# ----------------------------------------------------------------------
if __name__ == "__main__":
    st.set_page_config(page_title="Home", page_icon="🏠")
    menu( )
    main( )


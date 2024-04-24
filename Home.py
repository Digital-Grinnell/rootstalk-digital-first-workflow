# Home.py
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

# import os
# import re
# import logging
# import glob
# from datetime import datetime
# from markdownify import markdownify as md
# from bs4 import BeautifulSoup
# import tempfile, shutil
# from azure.storage.blob import BlobServiceClient
# import subprocess, sys


# Define some globals...
# ---------------------------------------------------------------------

LOGGER = get_logger(__name__)

converted_pattern = r"(\d{4})-(spring|fall)/(.+)/converted/(.+)\.html"
file_pattern = r"^\d{4}-(spring|fall)\.md$"
year_term_pattern = r"(\d{4})-(spring|fall)"
image_pattern = r".{3}\(.+/image/(.+)\)$"
reference_pattern = r"\[(\d+)]"
endnote_pattern = r"endnote-(\d+)"

fm_template = '---\n' \
              'index: \n' \
              'azure_dir: \n' \
              'articleIndex: \n' \
              '_title: \n' \
              'subtitle: \n' \
              'byline: \n' \
              'byline2: \n' \
              'categories: \n' \
              '  - category\n'  \
              'tags: \n' \
              '  - \n'  \
              'header_image: \n' \
              '  filename: \n' \
              '  alt_text: \n' \
              'contributors: \n' \
              '  - role: author \n' \
              '    name: \n' \
              '    headshot: \n' \
              '    caption: \n' \
              '    bio: " "\n' \
              'description: \n' \
              'date: \n' \
              'draft: false \n' \
              'no_leaf_bug: false\n' \
              "---\n"

default_path = '/Users/mcfatem/Library/CloudStorage/OneDrive-GrinnellCollege/Digital-Versions'


# Page code goes here...

def main( ):
    
    # Initialize the session_state, including some CONSTANTs
    if not state('html_path'):
        st.session_state.html_path = False

    # Explain the OneDrive prep required before running this app...
    md = "This app assumes that you have already COPIED the contents of Professor Baechtel's OneDrive, specifically the `Rootstalk, Spring 2024` : `Digital-Versions` subdirectory, to YOUR OWN OneDrive and synchronized that copy with your workstation.  To do this open the appropriate OneDrive, navigate to YOUR aforementioned subdirectory and click on the `Sync` option.  You may be prompted for your Grinnell login credentials before the directory is sync'd to your workstation.  On a Mac the sync'd local folder is likely to be `~/Library/CloudStorage/OneDrive-GrinnellCollege/Digital-Versions`, the default path in this app."
    st.write(md)

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
# ----------------------------------------------------------------------
def other_functions( ):
    pass


# Config the page and execute it but not when loading!
# ----------------------------------------------------------------------
if __name__ == "__main__":
    st.set_page_config(page_title="Home",page_icon=":home:")
    main( )


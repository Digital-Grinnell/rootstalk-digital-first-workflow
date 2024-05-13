# pages/3_💾_Copy-MD-to-Issue.py
#

import streamlit as st
import os, re, logging, glob, tempfile, shutil
from utils import *
from datetime import datetime
from azure.storage.blob import BlobServiceClient
import constants as c
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import frontmatter as front


# Page code goes here...
#-----------------------------------------------------------------------

def main( ):

    pattern = r"^\/(.+)\/(.+)\.md$"

    # Prompt for path to LOCAL sync of the 'Digital-Versions' directory (or accept the default)
    local_path = st.text_input("Path to your LOCAL/sync `Digital-Versions` directory", state('working_dir'))
    st.session_state.working_dir = local_path

    # Glob all the .html files recursively from path
    files = glob.glob(f'{local_path}/**/converted/*.md', recursive=True)

    filenames = [ ]
    for file in files:
        no_path = file.removeprefix(local_path)     # remove the known parent directory for better display
        filenames.append(no_path)

    if len(filenames) == 0:
        st.error(f"No `.md` files could be found in `{state('working_dir')}`!")
        return False

    # Now the form...
    with st.form("select_md"):

        selected = st.selectbox(
            "Select an MD file (presumably produced by 'HTML → 🐍 → Markdown') to copy to the `npm-rootstalk` project", filenames)[1:]   # remove / or os.path.join will FAIL

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write(f'You selected {selected}')
            selected_path = os.path.join(local_path, selected)

            # OK, an .md file has been selected
            path = os.path.dirname(selected_path)
            filename = os.path.basename(selected_path)

            logfile = selected_path.replace(".md", ".log")
            logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.DEBUG)
            logging.info(f"Selected .md file: '{selected_path}'.")

            # Go for liftoff
            dst = c.destination_path + filename
            shutil.copyfile(selected_path, dst)

            # Report success and display the Markdown if user asked for it
            st.session_state.md_path = path + "/" + filename
            st.success(f"Success! Markdown file '{st.session_state.md_path}' has been copied.")

            # Suggest follow-up...
            st.info(f"The markdown file '{st.session_state.md_path}' has been copied to `{dst}`, the [npm-rootstalk](https://github.com/Digital-Grinnell/npm-rootstalk) project's `content` directory.")

            st.info(f"Subsequently pushing the addition to the repo (`main` branch) generates a new [review site.](https://yellow-wave-0e513e510.3.azurestaticapps.net)")

            if state('show_markdown'):
                show_markdown( )
            
    return


# Other functions here...
#-----------------------------------------------------------------------


# Config the page and execute it but not when loading!
#-----------------------------------------------------------------------

if __name__ == "__main__":

    st.set_page_config(page_title="Copy MD → Issue", page_icon="💾")

    # st.markdown("# Page 2 Markdown")
    # st.write("This page Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")
    # st.sidebar.header("Page 2 Sidebar Header")
    # st.session_state.status = "This is session_state.status from Page 2"

    menu( )
    main( )

    # Do some stuff here
    # st.sidebar.success(f"This is Page_2 st.sidebar.success( ).")

    show_session( )
    show_code(main)

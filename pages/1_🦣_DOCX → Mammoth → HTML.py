# pages/1_🦣_DOCX → Mammoth → HTML.py
#

import streamlit as st
from utils import *
import glob, os, subprocess, re 
import constants as c

pattern = "^\/(.+)\/(.+)\.docx$"

# Page code goes here...
#-----------------------------------------------------------------------

def main( ):
    st.session_state.html_path = run_mammoth( )
    show_session( )
    show_code(main)
    return 


# Other functions here...
#-----------------------------------------------------------------------

def run_mammoth( ):

    # Prompt the user to enter the path to their LOCAL sync of the 'Digital-Versions' directory (or accept the default)
    local_path = st.text_input("Path to your LOCAL/sync `Digital-Versions` directory", state('working_dir'))
    st.session_state.working_dir = local_path

    # Glob all the .docx files recursively from path
    files = glob.glob(f'{local_path}/**/*.docx', recursive=True) 
    
    if not files:
        st.error(f"No `.docx` files could be found in `{state('working_dir')}`!")
        return False

    filenames = [ ]
    for file in files: 
        no_path = file.removeprefix(local_path)     # remove the known parent directory for better display
        found = re.search(pattern, no_path)         # don't include .docx that are IN the directory,
        if found:                                   #   only those from subdirs!
            filenames.append(no_path)
    
    # Now the form...
    with st.form("select_docx"):                                           # remove leading slash or 
        selected = st.selectbox('Select a Word Document', filenames)[1:]   #   os.path.join will FAIL
    
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write(f'You selected {selected}')
            selected_path = os.path.join(local_path, selected)

            # OK, a .docx has been selected, run 'mammoth'
            dir = os.path.dirname(selected_path)
            doc = os.path.basename(selected_path)

            # Report progress and mkdir
            st.write(f"Creating the `{dir}/converted` subdirectory if it does not already exist.")
            subprocess.run(f"mkdir -p '{dir}/converted'", shell=True, executable="/bin/bash")
            st.success('Done!')

            # Report progress and run 'mammoth'
            html_name = doc[:-5] + ".html"
            html_path = os.path.join(dir, "converted", html_name)
            st.write(f"Running **mammoth** on `{dir}/{doc}` to create `{html_path}`.")

            # With a spinner widget...
            with st.spinner("**Mammoth**s are not quick, wait for it..."):
                result = subprocess.run(f"mammoth '{dir}/{doc}' --output-dir='{dir}/converted' --style-map=rootstalk-custom-style.map", capture_output=True, text=True, shell=True, executable="/bin/bash")

            if result.stdout: 
                st.success(f"Output: \n{result.stdout}")
            if result.stderr: 
                st.error(f"Errors: \n{result.stderr}")
                st.error('Done!')
            else:
                st.success('Done!  There are **NO errors** to report!')

            return html_path
        
    return False



# Config the page and execute it but not when loading!
#-----------------------------------------------------------------------

if __name__ == "__main__":

    page_name = "DOCX → Mammoth → HTML"

    st.set_page_config(page_title=page_name, page_icon="🦣")
    
    # st.markdown("# Page 1 Markdown")
    # st.write("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")
    
    st.sidebar.header(page_name)
    
    # st.session_state.status = "This is session_state.status from Page 1"

    menu( )
    
    # Call main( )
    main( )

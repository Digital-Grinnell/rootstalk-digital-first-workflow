# pages/2_🐍_HTML → Python → Markdown.py
#

import streamlit as st
import os, re, logging, glob, tempfile, shutil
from utils import *
from datetime import datetime
from azure.storage.blob import BlobServiceClient
import constants as c
from bs4 import BeautifulSoup
from markdownify import markdownify as md


# Page code goes here...
#-----------------------------------------------------------------------

def main( ):

    pattern = r"^\/(.+)\/(.+)\.html$"

    # Retrieve the Azure connection string for use with the application. The storage
    # connection string is stored in an environment variable on the machine
    # running the application called AZURE_STORAGE_CONNECTION_STRING. If the environment variable is
    # created after the application is launched in a console or with Visual Studio,
    # the shell or application needs to be closed and reloaded to take the
    # environment variable into account.

    # If not previously defined, create the BlobServiceClient object and save it in session_state
    if not state('blob_service_client'):
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        st.session_state.blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Prompt for path to LOCAL sync of the 'Digital-Versions' directory (or accept the default)
    local_path = st.text_input("Path to your LOCAL/sync `Digital-Versions` directory", state('working_dir'))
    st.session_state.working_dir = local_path

    # Glob all the .html files recursively from path
    files = glob.glob(f'{local_path}/**/*.html', recursive=True)

    filenames = [ ]
    for file in files:
        no_path = file.removeprefix(local_path)     # remove the known parent directory for better display
        found = re.search(pattern, no_path)         # don't include .html that are IN the directory,
        if found:                                   #   only those from subdirs!
            filenames.append(no_path)

    if len(filenames) == 0:
        st.error(f"No `.html` files could be found in `{state('working_dir')}`!")
        return False

    # Now the form...
    with st.form("select_html"):
        st.session_state.show_markdown = st.checkbox("Show generated Markdown", True)

        selected = st.selectbox(
            "Select an HTML file (presumably produced by 'DOCX → 🦣 → HTML') for conversion to Markdown", filenames)[1:]   # remove / or os.path.join will FAIL

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write(f'You selected {selected}')
            selected_path = os.path.join(local_path, selected)

            # OK, an .html file has been selected
            path = os.path.dirname(selected_path)
            filename = os.path.basename(selected_path)

            logfile = selected_path.replace(".html", ".log")
            logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.DEBUG)
            logging.info(f"Selected .html file: '{selected_path}'.")

            # Reset our frontmatter from the template 
            st.session_state.aFrontmatter = c.fm_template    # initialize 'aFrontmatter' in our session state

            # Go for liftoff
            aName = rootstalk_markdownify(selected_path)

            # If a valid (True) article name (aName) was returned, set it in our state and increment aIndex
            if aName:
                st.session_state.aIndex += 1
                st.session_state.aName = aName

            # Report success and display the Markdown if user asked for it
            st.session_state.md_path = path + "/" + aName + ".md"
            st.success(f"Success! Markdown file '{st.session_state.md_path}' has been created.")

            # Suggest follow-up...
            st.info(f"Copy '{st.session_state.md_path}' to the [npm-rootstalk](https://github.com/Digital-Grinnell/npm-rootstalk) project's `content` directory for publication.")

            st.info(f"Subsequently pushing the addition to the repo (`main` branch) generates a new [review site.](https://yellow-wave-0e513e510.3.azurestaticapps.net)")

            if state('show_markdown'):
                show_markdown( )
            
    return


# Other functions here...
#-----------------------------------------------------------------------



# figcaption(element)
# ----------------------------------------------------------------------
def figcaption(element):
    # Is the next element a <figcaption>?
    found = element.find_next('figcaption')
    if found:
        c = ' '.join(map(str,found.contents))
        if c:
            caption = c.lstrip('0123456789').replace('"', "'").replace("\n", '')
            found.decompose( )  # remove the <figcaption> and return it's content
            return caption

    return ""


# upload_to_azure( ) - Just what the name says post-processing
# ----------------------------------------------------------------------------------------------
def upload_to_azure(target, upload_file_path):
    azure_base_url = "https://rootstalk.blob.core.windows.net"

    try:

        container_name = 'rootstalk-2024-spring'
        url = azure_base_url + "/" + container_name

        blob_client = state('blob_service_client').get_blob_client(container=container_name, blob=target)

        if blob_client.exists( ):
            msg = f"Blob '{target}' already exists in Azure Storage container '{container_name}'.  Skipping this upload."
            st.info(msg)
            return url
        else:
            msg = f"Uploading '{target}' to Azure Storage container '{container_name}'"
            st.info(msg)

        # Upload the file
        with open(file=upload_file_path, mode="rb") as data:
            blob_client.upload_blob(data)

        return url

    except Exception as e:
        st.exception(e)
        return False


# Create a temporary file copy for our HTML
# From https://stackoverflow.com/a/6587648
# -------------------------------------------------------------------------
def create_temporary_copy(path):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, 'temp_file_name')
    shutil.copy2(path, temp_path)
    return temp_path


# do_image(i, path)
# Note that <figcaption> MUST come AFTER the <figure>!
# ------------------------------------------------------------------------
def do_image(i, path):

    image_name = False
    markdown = False
    remove_me = "\n\nDescription automatically generated"

    caption = "We need a caption here!"
    alt = False

    try:

        # Working Sample 1:  <img class="Article-Image"><img src="2.jpeg" /></img>
        # Broken Sample 2: <img class="Article-Image"> <img alt="Two men standing together in a...
        #   The space between <img> tags is "next" and unaccounted for...

        # Get the image name and build an Azure path...  if the <img> has no 'src' element look for it in the next element.
        if i.attrs:
            if len(i.attrs) > 0:
                if 'src' in i.attrs:
                    image_name = i.attrs['src']
                if 'alt' in i.attrs:
                    alt = i.attrs['alt']
                    if alt.endswith(remove_me):
                        alt = alt[:-(len(remove_me))]

        # Get the image name and build an Azure path...  if the <img> has no 'src' element 
        #   look for one in the "next" <img> element.  Be sure to account for 
        #   any "empty" elements between the two <img> tags!  See remove_empty( )!
        if not image_name:
            if i.next:
                if i.next.attrs:
                    if len(i.next.attrs) > 0:
                        if 'src' in i.next.attrs:
                            image_name = i.next.attrs['src']

        if image_name:
            image_path = f"{state('aName')}-{image_name}"

            # Upload the image to Azure
            url = upload_to_azure(image_path, path + "/" + image_name)
            if not url:
                st.error(f"Upload of image to {path}/{image_name} to Azure failed!")

            # Now, deal with the alt text as a sibling
            sibling = i.nextSibling
            if sibling:
                if hasattr(sibling, 'attrs'):
                    for a in sibling.attrs:
                        if a == 'alt':
                            alt = sibling.attrs['alt']
                            if alt.endswith(remove_me):
                                alt = alt[:-(len(remove_me))]
                            sibling.decompose( )  # remove the <img> alt

            caption = figcaption(i)
            markdown = f'{c.osc} figure_azure pid="{image_path}" caption="{caption}" alt="{alt}" {c.csc}'

        else:
            st.error(f"Whoa, got an image here with an unidentified <img> tag structre OR no name!")    

        return markdown

    except Exception as e:
        st.exception(e)
        return False


# remove_empty( )
# -----------------------------------------------------------------------------
def remove_empty(soup):
    # Remove all non-essential "empty" tags and internal new-lines!   
    broth = BeautifulSoup( )
    for x in soup.find_all( ):
        if len(x.get_text(strip=True)) > 0 or x.name in ['br', 'img']:         # From https://stackoverflow.com/questions/33500888/how-to-remove-tags-that-have-no-content
            if x.child is None:    # From https://stackoverflow.com/questions/14550288/how-do-i-remove-linebreaks-only-if-they-occur-inside-html-tags
                try:
                    x.child.contents[0].replace('\n', '')
                except AttributeError:
                    pass
            else:
                try:
                    x.contents[0].replace('\n', '')
                except AttributeError:
                    pass
            broth.append(x)
    return broth


# Parse the Mammoth-converted HTML to find key/frontmatter elements from our
#    rootstalk-custom-style.map file.  Substitute them into `aFrontmatter`.
#
# See https://www.geeksforgeeks.org/find-tags-by-css-class-using-beautifulsoup/ for guidance.
#
# -----------------------------------------------------------------------------
def parse_post_mammoth_converted_html(html_file, path):
    import constants as c

    # Fetch the article's current frontmatter for modification
    frontmatter = state('aFrontmatter')

    try:

        # Parse the HTML content
        with open(html_file, 'r') as h:
            html_string = h.read( ).replace('“','"').replace('”','"')     # remove smart quotes!
            soup = BeautifulSoup(html_string, "html.parser")
            soup = remove_empty(soup)   # remove empty non-essential tags and embedded new-lines!

            # Find key tags by CSS class
            title = soup.find("h1", class_= "Primary-Title")
            byline = soup.find("p", class_= "Byline")
            article_type = soup.find("p", class_= "Article-Type")
            hero_image = soup.find("img", class_= "Hero-Image")

            c_role = soup.findAll("p", class_= "Contributor-Role")
            c_name = soup.findAll("p", class_= "Contributor-Name")
            c_bio = soup.findAll("p", class_= "Contributor-Bio")
            c_headshot = soup.findAll("img", class_= "Contributor-Headshot")

            # Drop found elements into the aFrontmatter and remove them from the soup...

            if title:
                frontmatter = frontmatter.replace("_title: ", f"title: \"{title.contents[0]}\"")
                title.decompose( )

            if byline:
                frontmatter = frontmatter.replace("byline: ", f"byline: \"{byline.contents[0]}\"")
                byline.decompose( )

            if article_type:
                frontmatter = frontmatter.replace("- category", f"- {article_type.contents[0]}")
                article_type.decompose( )

            if hero_image:
                if 'src' in hero_image.attrs:
                    image_name = hero_image.attrs['src']
                    hero_image.decompose( )       # get rid of the <img> tag         
                else:    
                    image_name = hero_image.next.attrs['src']
                    hero_image.next.decompose( )  # get rid of the <img> tag

                image_path = f"{state('aName')}-{image_name}"
                frontmatter = frontmatter.replace("  filename: ", f"  filename: {image_path}")

                # Upload the hero image to Azure
                url = upload_to_azure(image_path, path + "/" + image_name)
                if not url:
                    st.error(f"Upload of image to {path}/{image_name} to Azure failed!")

            # Contributor logic only expects ONE contributor for now, add more later!
            c_blocks = 0

            if c_role:
                c_blocks = len(c_role) 
                if c_blocks > 1:
                    st.warning(f"{c_blocks} contributor roles found.  Current logic supports only ONE!")
                for b in c_role:
                    frontmatter = frontmatter.replace("  - role: author", f"  - role: {b.contents[0]}")
                    b.decompose( )

            if c_name:
                c_blocks = len(c_name) 
                if c_blocks > 1:
                    st.warning(f"{c_blocks} contributor names found.  Current logic supports only ONE!")
                for b in c_name:
                    frontmatter = frontmatter.replace("    name: ", f"    name: {b.contents[0]}")
                    b.decompose( )

            if c_bio:
                c_blocks = len(c_bio) 
                if c_blocks > 1:
                    st.warning(f"{c_blocks} contributor bios found.  Current logic supports only ONE!")
                for b in c_bio:
                    frontmatter = frontmatter.replace("    bio: ", f'    bio: "{b.contents[0]}"')
                    b.decompose( )

            if c_headshot:
                c_blocks = len(c_headshot) 
                if c_blocks > 1:
                    st.warning(f"{c_blocks} contributor headshots found.  Current logic supports only ONE!")
                for b in c_headshot:
                    if 'src' in b.attrs:
                        image_name = b.attrs['src']
                        b.decompose( )       # get rid of the <img> tag         
                    else:    
                        image_name = b.next.attrs['src']
                        b.next.decompose( )  # get rid of the <img> tag

                    image_path = f"{state('aName')}-{image_name}"
                    frontmatter = frontmatter.replace("    headshot: ", f"    headshot: {image_path}")

                    # Upload the headshot image to Azure
                    url = upload_to_azure(image_path, path + "/" + image_name)
                    if not url:
                        st.error(f"Upload of image to {path}/{image_name} to Azure failed!")


            # Now, find ALL and rewrite remaining "inline" styles...
            # --------------------------------------------------------

            headings = soup.find_all("h2", class_ = "Title")
            for h in headings:
                h.replace_with(f"## {h.contents[0]} \n\n")

            emphasized = soup.find_all("p", class_ = "Emphasized-Paragraph")
            for e in emphasized:
                e.replace_with(f"_{e.contents[0].strip( )}_ \n\n")

            pull_quotes = soup.find_all("p", class_ = "Intense-Quote")
            for q in pull_quotes:
                q.replace_with(f"{c.osc} pullquote {c.csc}\n{q.contents[0].strip( )}\n{c.osc} /pullquote {c.csc} \n\n")

            attributions = soup.find_all("p", class_ = "Attribution")
            for a in attributions:
                a.replace_with(f"{c.osc} attribution 5 {c.csc}\n{a.contents[0].strip( )}\n{c.osc} /attribution {c.csc} \n\n")

            # images = soup.find_all("img")
            images = soup.find_all("img", class_ = "Article-Image")
            for i in images:
                replacement = do_image(i, path)
                if replacement:
                    i.replace_with(f"{replacement} \n\n")     # valid replacment, swap it in place of <img>
                else:
                    i.decompose( )   # no valid replacement, decompose (remove) the <img> element

            videos = soup.find_all("p", class_ = "Video")
            for v in videos:
                for ct in v.contents:
                    if isinstance(ct, str):
                        if ct.startswith("{{% video"):         # find contents that opens with '{{% video'
                            markdown = f"{ct}"
                            caption = figcaption(v)
                            if caption:
                                markdown = f'{c.osc} caption=\"{caption}\" {c.csc}'
                            v.replace_with(f"{markdown} \n\n")  # replace entire tag with the {{% contents %}}
                            # Upload the video to Azure
                            # url = upload_to_azure(image_path, path + "/" + image_name)

            audios = soup.find_all("p", class_ = "Audio")
            for a in audios:
                for ct in a.contents:
                    if isinstance(ct, str):
                        if ct.startswith("{{% audio"):         # find contents that opens with '{{% audio'
                            markdown = f"{ct}"
                            caption = figcaption(a)
                            if caption:
                                markdown = f'{c.osc} caption=\"{caption}\" {c.csc}'
                            a.replace_with(f"{markdown} \n\n")  # replace entire tag with the {{% contents %}}
                            # Upload the audio to Azure
                            # url = upload_to_azure(image_path, path + "/" + image_name)

            # Sample endnote reference:
            # references<sup><a href="#endnote-2" id="endnote-ref-2">[1]</a></sup> expressed
            # {{% ref 1 %}}

            refs = soup.find_all("sup")

            try:    # This section is problematic so it gets a try...except of its own!
                for r in refs:
                    if r.contents[0] == ' ':       # skip "empty" <sup> elements
                        r.decompose( )
                    else:
                        number_string = r.contents[0].isdigit( )
                        if not number_string:
                            number_string = str(r.next_element.contents[0])
                        else:
                            number_string = str(r.contents[0])

                        m = re.match(c.reference_pattern, number_string)
                        if m:
                            number = m.group(1)
                            r.replace_with(f"{c.osc} ref {number} {c.csc} ")
                            r.decompose( )
                        elif number_string.isdigit( ):
                            number = int(number_string)
                            r.replace_with(f"{c.osc} ref {number} {c.csc} ")
                            r.decompose( )
                        else:
                            st.warning(f"Non-numeric <sup> tag '{number_string}' was ignored.")    

            except Exception as e:
                st.exception(e)
                pass

            # Sample endnotes:
            # <ol>
            #   <li id="endnote-2">
            #     <p> This is endnote #1 referenced...</p>
            #   </li>
            #   <li id="endnote-3">
            #     <p> This is endnote #2. Endnotes...</p>
            #   </li>
            # </ol>
            #
            # {{% endnotes %}}
            # {{% endnote 1 "This is endnote #1 referenced..." %}}

            replacement = f"{c.osc} endnotes {c.csc} "

            has_notes = soup.find("ol")
            if has_notes:
                notes = has_notes.find_all("li")
                for n in notes:
                    id = n.attrs['id']
                    m = re.match(c.endnote_pattern, id)
                    number = int(m.group(1)) - 1
                    p = n.find("p")
                    text = ""
                    for s in p.contents[:-1]:
                        text += str(s).replace('"', r'\"').replace(r"\n", " ")
                    replacement += f"\n{c.osc} endnote {number} \"{text}\" {c.csc} "

                has_notes.replace_with(f"{replacement} \n")
                has_notes.decompose( )

        # All done here, save the frontmatter in session state
        st.session_state.aFrontmatter = frontmatter

    except Exception as e:
        st.exception(e)
        return False

    # Return the decomposed and rewritten HTML as a string
    return str(soup.prettify( ))


# Open the "converted" article.html file and make our Rootstalk-specific additions
# to a new .md copy of the HTML.
#
# This produces a new .md file with the same name.
# ------------------------------------------------------------------------------
def rootstalk_markdownify(filepath):

    with open(filepath, "r") as html:

        # Open a new .md file to receive translated text
        (path, filename) = os.path.split(filepath)
        (article_name, ext) = filename.split('.')
        new_file = '{}/{}.{}'.format(path, article_name, 'md')

        st.session_state.aName = article_name                # set the session state now, we might need it soon!
        logging.info("Creating new .md file: " + new_file)

        timestamp = datetime.now( ).strftime('%d/%m/%Y %H:%M:%S')
        frontmatter = state('aFrontmatter')

        # Customize the front matter before inserting it...
        frontmatter = frontmatter.replace("index: ", f"index: {article_name}")
        frontmatter = frontmatter.replace("articleIndex: ", f"articleIndex: {state('aIndex')}")
        frontmatter = frontmatter.replace("azure_dir: ", f"azure_dir: rootstalk-{c.year}-{c.term}")
        frontmatter = frontmatter.replace("date: ", f"date: '{timestamp}'")

        # Save the modified frontmatter in our session_state!
        st.session_state.aFrontmatter = frontmatter

        # Create a temp copy of the HTML for parsing and removal of elements
        temp = create_temporary_copy(filepath)

        # Parse the Mammoth-converted HTML to make additional substitutions into the frontmatter.
        # Return a reduced (decomposed) HTML string suitable for processing using 'markdownify' (alias 'md')
        reduced = parse_post_mammoth_converted_html(temp, path)

        # Write the front matter (from our session_state!) and content to the article.md file
        if reduced:
            with open(new_file, "w") as mdf:
                frontmatter = state('aFrontmatter')
                print(frontmatter, file=mdf)
                markdown_text = md(reduced, escape_asterisks=False, escape_underscores=False, escape_misc=False)
                clean_markdown = clean_up(markdown_text)
                print(clean_markdown, file=mdf)

    return article_name


# clean_up(markdown)
# --------------------------------------------------------------------------------
def clean_up(markdown):

    # Fix line breaks and spacing around {{% ref X %}} tags
    pattern = re.compile(r"\n ({{% ref \d+ %}})\n")
    clean = re.sub(pattern, r'\1', markdown, re.MULTILINE)

    return clean


# Config the page and execute it but not when loading!
#-----------------------------------------------------------------------

if __name__ == "__main__":

    st.set_page_config(page_title="HTML → 🐍 → Markdown", page_icon="🐍")

    # st.markdown("# Page 2 Markdown")
    # st.write("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")
    # st.sidebar.header("Page 2 Sidebar Header")
    # st.session_state.status = "This is session_state.status from Page 2"

    menu( )
    main( )

    # Do some stuff here
    # st.sidebar.success(f"This is Page_2 st.sidebar.success( ).")

    show_session( )
    show_code(main)

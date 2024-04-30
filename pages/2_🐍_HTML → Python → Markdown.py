# pages/2_🐍_HTML → Python → Markdown.py
#

import streamlit as st
import os, re, logging, glob, tempfile, shutil
from utils import *
from datetime import datetime
import os, uuid
from azure.storage.blob import BlobServiceClient


# Page code goes here...
#-----------------------------------------------------------------------

def main( ):

    global fm_template
    global aIndex
    global frontmatter

    pattern = '^\/(.+)\/(.+)\.html$'

    # Retrieve the Azure connection string for use with the application. The storage
    # connection string is stored in an environment variable on the machine
    # running the application called AZURE_STORAGE_CONNECTION_STRING. If the environment variable is
    # created after the application is launched in a console or with Visual Studio,
    # the shell or application needs to be closed and reloaded to take the
    # environment variable into account.

    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Prompt for path to LOCAL sync of the 'Digital-Versions' directory (or accept the default)
    local_path = st.text_input("Path to your LOCAL/sync `Digital-Versions` directory", state('working_dir'))
    st.session_state.working_dir = local_path

    # Glob all the .html files recursively from path
    files = glob.glob(f'{local_path}/**/*.html', recursive=True)

    filenames = [ ]
    for file in files:
        no_path = file.removeprefix(local_path)     # remove the known parent directory for better display
        found = re.search(pattern, no_path)         # don't include .docx that are IN the directory,
        if found:                                   #   only those from subdirs!
            filenames.append(no_path)

    if len(filenames) == 0:
        st.error(f"No `.html` files could be found in `{state('working_dir')}`!")
        return False

    # Now the form...
    with st.form("select_html"):
        selected = st.selectbox(
            'Select an HTML file from DOCX → 🦣 → HTML', filenames)[1:]   # remove / or os.path.join will FAIL

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write(f'You selected {selected}')
            selected_path = os.path.join(local_path, selected)

            # OK, a .html has been selected
            path = os.path.dirname(selected_path)
            filename = os.path.basename(selected_path)

            logfile = selected_path.replace(".html", ".log")
            logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.DEBUG)
            logging.info(f"Selected .html file: '{selected_path}'.")

            # Reset our frontmatter from the template and increment the article index
            frontmatter = fm_template
            aIndex += 1

            # Go for liftoff
            rootstalk_markdownify(selected_path)

    return


# Other functions here...
#-----------------------------------------------------------------------

# figcaption(element)
# ----------------------------------------------------------------------
def figcaption(element):
    # Is the next element a <figcaption>?
    found = element.find_next('figcaption')
    if found:
        c = found.contents[0]
        if c:
            caption = c.lstrip('0123456789').replace('"', "'")
            found.decompose( )  # remove the <figcaption> and return it's content
            return caption

    return ""


# upload_to_azure( ) - Just what the name says post-processing
# ----------------------------------------------------------------------------------------------
def upload_to_azure(blob_service_client, target, upload_file_path):
    azure_base_url = "https://rootstalk.blob.core.windows.net"

    try:

        container_name = 'rootstalk-2024-spring'
        url = azure_base_url + "/" + container_name

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=target)

        if blob_client.exists( ):
            msg = f"Blob '{target}' already exists in Azure Storage container '{container_name}'.  Skipping this upload."
            print(msg)
            return False
        else:
            msg = f"Uploading '{target}' to Azure Storage container '{container_name}'"
            print(msg)

        # Upload the file
        with open(file=upload_file_path, mode="rb") as data:
            blob_client.upload_blob(data)

        return url

    except Exception as ex:
        st.exception(f'Exception: {ex}')
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
    global a_name
    global open_shortcode
    global close_shortcode
    global blob_service_client

    image_name = False
    markdown = False
    remove_me = "\n\nDescription automatically generated"

    caption = "We need a caption here!"
    alt = False

    try:

        # Get the image name and build an Azure path...  if the <img> has no 'src' element look for it in the next element.
        if i.attrs:
            if len(i.attrs) > 0:
                if i.attrs['src']:
                    image_name = i.attrs['src']
                if i.attrs['alt']:
                    alt = i.attrs['alt']
                    if alt.endswith(remove_me):
                        alt = alt[:-(len(remove_me))]

        # Get the image name and build an Azure path...  if the <img> has no 'src' element, skip it.
        if not image_name:
            if i.next:
                if i.next.attrs:
                    if len(i.next.attrs) > 0:
                        image_name = i.next.attrs['src']

        if image_name:
            image_path = f"{a_name}-{image_name}"

            # Upload the image to Azure
            url = upload_to_azure(blob_service_client, image_path, path + "/" + image_name)

            # Now, deal with the alt text as a sibling
            sibling = i.nextSibling
            if sibling:
                for a in sibling.attrs:
                    if a == 'alt':
                        alt = sibling.attrs['alt']
                        if alt.endswith(remove_me):
                            alt = alt[:-(len(remove_me))]
                        sibling.decompose()  # remove the <img> alt

            caption = figcaption(i)
            markdown = f'{open_shortcode} figure_azure pid="{image_path}" caption="{caption}" alt="{alt}" {close_shortcode}'

        return markdown

    except Exception as e:
        st.exception(f'Exception: {e} ')
        return False


# Parse the Mammoth-converted HTML to find key/frontmatter elements from our
#    rootstalk-custom-style.map file.  Substitute them into `frontmatter`.
#
# See https://www.geeksforgeeks.org/find-tags-by-css-class-using-beautifulsoup/ for guidance.
#
# -----------------------------------------------------------------------------
def parse_post_mammoth_converted_html(html_file, path):
    global frontmatter
    global aIndex
    global blob_service_client
    global index

    # Parse the HTML content
    with open(html_file, 'r') as h:
        html_string = h.read( ).replace('“','"').replace('”','"')     # remove smart quotes!
        soup = BeautifulSoup(html_string, "html.parser")

        # Find key tags by CSS class
        title = soup.find("h1", class_= "Primary-Title")
        byline = soup.find("p", class_= "Byline")
        article_type = soup.find("p", class_= "Article-Type")
        hero_image = soup.find("img", class_= "Hero-Image")

        # Drop found elements into the frontmatter and remove them from the soup...

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
            image_name = hero_image.next.attrs['src']
            image_path = f"{a_name}-{image_name}"
            frontmatter = frontmatter.replace("  filename: ", f"  filename: {image_path}")
            hero_image.next.decompose( )  # get rid of the <img> tag
            hero_image.decompose( )
            # Upload the hero image to Azure
            url = upload_to_azure(blob_service_client, image_path, path + "/" + image_name)

        # Now, find ALL and rewrite remaining "inline" styles...
        # --------------------------------------------------------

        try:

            headings = soup.find_all("h2", class_ = "Title")
            for h in headings:
                h.replace_with(f"## {h.contents[0]} \n\n")

            emphasized = soup.find_all("p", class_ = "Emphasized-Paragraph")
            for e in emphasized:
                e.replace_with(f"_{e.contents[0].strip( )}_ \n\n")

            pull_quotes = soup.find_all("p", class_ = "Intense-Quote")
            for q in pull_quotes:
                q.replace_with(f"{open_shortcode} pullquote {close_shortcode}\n{q.contents[0].strip( )}\n{open_shortcode} /pullquote {close_shortcode} \n\n")

            attributions = soup.find_all("p", class_ = "Attribution")
            for a in attributions:
                a.replace_with(f"{open_shortcode} attribution 5 {close_shortcode}\n{a.contents[0].strip( )}\n{open_shortcode} /attribution {close_shortcode} \n\n")

            images = soup.find_all("img")
            # images = soup.find_all("img", class_ = "Article-Image")
            for i in images:
                replacement = do_image(i, path)
                if replacement:
                    i.replace_with(f"{replacement} \n\n")     # valid replacment, swap it in place of <img>
                else:
                    i.decompose( )   # no valid replacement, decompose (remove) the <img> element

            videos = soup.find_all("p", class_ = "Video")
            for v in videos:
                for c in v.contents:
                    if isinstance(c, str):
                        if c.startswith("{{% video"):         # find contents that opens with '{{% video'
                            markdown = f"{c}"
                            caption = figcaption(v)
                            if caption:
                                markdown = markdown.replace(close_shortcode, f"caption=\"{caption}\" {close_shortcode}")
                            v.replace_with(f"{markdown} \n\n")  # replace entire tag with the {{% contents %}}
                            # Upload the video to Azure
                            # url = upload_to_azure(blob_service_client, image_path, path + "/" + image_name)

            audios = soup.find_all("p", class_ = "Audio")
            for a in audios:
                for c in a.contents:
                    if isinstance(c, str):
                        if c.startswith("{{% audio"):         # find contents that opens with '{{% audio'
                            markdown = f"{c}"
                            caption = figcaption(a)
                            if caption:
                                markdown = markdown.replace(close_shortcode, f"caption=\"{caption}\" {close_shortcode}")
                            a.replace_with(f"{markdown} \n\n")  # replace entire tag with the {{% contents %}}
                            # Upload the audio to Azure
                            # url = upload_to_azure(blob_service_client, image_path, path + "/" + image_name)

            # Sample endnote reference:
            # references<sup><a href="#endnote-2" id="endnote-ref-2">[1]</a></sup> expressed
            # {{% ref 1 %}}

            refs = soup.find_all("sup")
            for r in refs:
                number_string = r.next_element.contents[0]
                m = re.match(reference_pattern, number_string)
                if m:
                    number = m.group(1)
                    r.replace_with(f"{open_shortcode} ref {number} {close_shortcode} ")
                    r.decompose( )

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

            replacement = f"{open_shortcode} endnotes {close_shortcode} "

            has_notes = soup.find("ol")
            if has_notes:
                notes = has_notes.find_all("li")
                for n in notes:
                    id = n.attrs['id']
                    m = re.match(endnote_pattern, id)
                    number = int(m.group(1)) - 1
                    p = n.find("p")
                    text = ""
                    for s in p.contents[:-1]:
                        text += str(s).replace('"', r'\"').replace(r"\n", " ")
                    replacement += f"\n{open_shortcode} endnote {number} \"{text}\" {close_shortcode} "

                has_notes.replace_with(f"{replacement} \n")
                has_notes.decompose( )

        except Exception as e:
            st.exception(f'Exception: {e}')
            return False

    # Return the decomposed and rewritten HTML as a string
    return str(soup.prettify( ))


# Open the "converted" article.html file and make our Rootstalk-specific additions
# to a new .md copy of the HTML.
#
# This produces a new .md file with the same name.
# ------------------------------------------------------------------------------
def rootstalk_markdownify(filepath):
    global aIndex
    global a_name
    global frontmatter

    with open(filepath, "r") as html:

        # Open a new .md file to receive translated text
        (path, filename) = os.path.split(filepath)
        (name, ext) = filename.split('.')
        new_file = '{}/{}.{}'.format(path, name, 'md')
        logging.info("Creating new .md file: " + new_file)

        timestamp = datetime.now( ).strftime('%d/%m/%Y %H:%M:%S')

        # Customize the front matter before inserting it...
        frontmatter = frontmatter.replace("index: ", f"index: {name}")
        frontmatter = frontmatter.replace("articleIndex: ", f"articleIndex: {aIndex}")
        frontmatter = frontmatter.replace("azure_dir: ", f"azure_dir: rootstalk-{year}-{term}")
        frontmatter = frontmatter.replace("date: ", f"date: '{timestamp}'")

        # Create a temp copy of the HTML for parsing and removal of elements
        temp = create_temporary_copy(filepath)

        # Parse the Mammoth-converted HTML to make additional substitutions into the frontmatter.
        # Return a reduced (decomposed) HTML string suitable for processing using 'markdownify' (alias "md")
        reduced = parse_post_mammoth_converted_html(temp, path)

        # Write the front matter and content to the article.md file
        if reduced:
            with open(new_file, "w") as mdf:
                print(frontmatter, file=mdf)
                markdown_text = md(reduced, escape_asterisks=False, escape_underscores=False, escape_misc=False)
                clean_markdown = clean_up(markdown_text)
                print(clean_markdown, file=mdf)

    return


# clean_up(markdown)
# --------------------------------------------------------------------------------
def clean_up(markdown):

    # Fix line breaks and spacing around {{% ref X %}} tags
    pattern = re.compile(r"\n ({{% ref \d+ %}})\n")
    clean = re.sub(pattern, r'\1', markdown, re.MULTILINE)

    return clean


# --------------------------------------------------------------------------------
# def rootstalk_azure_media(year, term, filepath):
#   # ytmd = "{}-{}.md".format(year, term, year, term)
#   ytmd = filepath.replace(".html", ".md")

#   # Open the issue's year-term.md file...
#   logging.info("Attempting to open markdown file: " + ytmd)
#   with open(ytmd, "r") as issue_md:
#     # azure_path = "{}-{}-azure.md".format(year, term)
#     azure_path = filepath.replace(".html", "-azure.md")

#     logging.info("Creating new Azure .md file at '{}'.".format(azure_path))

#     # Open and write a new year-term-azure.md file...
#     with open(azure_path, "w") as azure_md:
#       lines = issue_md.readlines()

#       # Clean-up...
#       # - translate any year-term-web-resources folder references to new Azure format.
#       # - remove any line that entirely matches the pattern:  ^.+ | .+$

#       for line in lines:
#         match_image = re.match(image_pattern, line)
#         match_header = re.match(header_pattern, line)
#         if match_image:  # transform image references
#           new_line = replacement.replace("xPIDx", match_image.group(1))
#           print(new_line, end='\n', file=azure_md)
#         elif not match_header:  # skip page headers
#           print(line, file=azure_md)  # write the line out

#   # Now, remove all repeated blank lines (reduces whitespace)
#   with open(azure_path, "r+") as azure_md:
#     contents = azure_md.read( )
#     # stripped = re.sub(r'^$\n', '', contents, flags=re.MULTILINE)
#     stripped = re.sub(r'\n\s*\n', '\n\n', contents)
#     azure_md.seek(0)  # rewind the file
#     azure_md.writelines(stripped)  # write the stripped version


# # ----------------------------------------------------------------------------------
# def rootstalk_make_articles(year, term, filepath):
#   ytyml = filepath.replace(".html", ".yml")

#   # Look for a year-term.yml file...
#   if not os.path.exists(ytyml):
#     logging.error("ERROR: No {} YAML file found! You need to create this file if you wish to proceed with the {}-{} issue!".format(ytyml, year, term))
#   else:
#     logging.info("Processing the {} file.".format(ytyml))

#     # Check for corresponding -azure.md file in the same directory
#     azure_md = filepath.replace(".html", "-azure.md")
#     if not os.path.exists(azure_md):
#       logging.error(
#             "ERROR: No Azure-formatted markdown file '{}' found! You may need to run the 'rootstalk_azure_media' scripts before proceeding.".format(
#               azure_md))

#     # Everything is in place, read the year-term.yml file...
#     with open(ytyml, "r") as stream:
#       try:
#         yml = yaml.safe_load(stream)
#       except yaml.YAMLError as exc:
#         sys.exit(exc)

#       for key, value in yml.items():
#         logging.info("{}: {}".format(key, value))

#       # Read each article name/index and create a new article_index.md file if one does not already exist
#       for name in yml["articles"]:
#         web_resources = '-web-resources/{}.md'.format(name)
#         md_path = filepath.replace(".html", web_resources)
#         logging.info("Creating article markdown file '{}'...".format(md_path))
#         if os.path.exists(md_path):
#           logging.warning(
#                 "WARNING: Markdown file '{}' already exists and will not be replaced! Be sure to move or remove the existing file if you wish to generate a new copy.".format(
#                   md_path))
#         else:
#           with open(azure_md, "r") as md:
#             issue_md_content = md.read()

#             # Customize the front matter before inserting it...
#             fm = frontmatter.replace("index: ", "index: {}".format(name))
#             fm = fm.replace("articleIndex: ", "articleIndex: {}".format(aIndex))
#             fm = fm.replace("azure_dir: ", "azure_dir: rootstalk-{}-{}".format(year, term))
#             fm = fm.replace("date: ", "date: '{}'".format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')))

#             aIndex += 1

#             # Write the front matter and content to the article.md file
#             with open(md_path, "w") as article_md:
#               print(fm, file=article_md)
#               print(issue_md_content, file=article_md)


# Config the page and execute it but not when loading!
#-----------------------------------------------------------------------

if __name__ == "__main__":

    st.set_page_config(page_title="HTML → 🐍 → Markdown", page_icon="🐍")

    st.markdown("# Page 2 Markdown")
    st.write("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")
    st.sidebar.header("Page 2 Sidebar Header")
    st.session_state.status = "This is session_state.status from Page 2"

    # Call main( )
    main( )

    # Do some stuff here
    st.sidebar.success(f"This is Page_2 st.sidebar.success( ).")

    show_session( )
    show_code(main)

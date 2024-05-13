# constants.py
#

# Define some globals...
# ---------------------------------------------------------------------

year = '2024'
term = 'spring'
issue = f"{year}-{term}"

converted_pattern = r"(\d{4})-(spring|fall)/(.+)/converted/(.+)\.html"
file_pattern = r"^\d{4}-(spring|fall)\.md$"
year_term_pattern = r"(\d{4})-(spring|fall)"
image_pattern = r".{3}\(.+/image/(.+)\)$"
reference_pattern = r"\[(\d+)]"
endnote_pattern = r"endnote-(\d+)"
footnote_pattern = r"footnote-(\d+)"

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
              '  - featured\n' \
              'header_image: \n' \
              '  filename: \n' \
              '  alt_text: \n' \
              'contributors: \n' \
              '  - role: author \n' \
              '    name: \n' \
              '    headshot: \n' \
              '    caption: \n' \
              '    bio: \n' \
              'description: \n' \
              'date: \n' \
              'draft: false \n' \
              'no_leaf_bug: false\n' \
              "---\n"

default_path = '/Users/mcfatem/Library/CloudStorage/OneDrive-GrinnellCollege/Rootstalk/Next-Issue/Digital-Versions'

destination_path = '/Users/mcfatem/GitHub/npm-rootstalk/content/volume-x-issue-1/'

osc = "{{%"   # open_shortcode
csc = "%}}"   # close_shortcode





"""
Created on 2020/03/31

@author: TheDrDOS

Make the landing page website

"""
import os
import markdown
import codecs
import webbrowser
from datetime import datetime
import time

# Log current time
now = datetime.now();
now = now.strftime("%d-%b-%Y (%H:%M:%S)")

# Assign input/output files
md_file = "../site/index.md"
html_file = "../site/index.html"

# Read the markdown document and encoded it
input_file = codecs.open(md_file, mode="r", encoding="utf-8")
text = input_file.read()
text = text+"\n---\n Updated on "+now+"\n"

# Make the webpage from the markdown
html = markdown.markdown(text)

# Write the encoded markdown to a file
output_file = codecs.open(html_file, "w",
                          encoding="utf-8",
                          errors="xmlcharrefreplace"
)
output_file.write(html)
output_file.close();

# Open the webpage to check it locally
# webbrowser.open("file://"+os.path.abspath(html_file))

# Post to the website
os.system('git ca "Updated using ./code/make_website.py script on: '+now+'"'+'; git push')

# Open a webbrowser at the remote location
webbrowser.open("https://covid-interactive-map.netlify.com")

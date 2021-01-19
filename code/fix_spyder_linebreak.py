re.match('\d+\:\d+\s*\-\s*\d+\:\d+',''.join(sd[i]))"""
Fix weird issue with linebreak characters from Spyder.
Linebreaks show up correctly in Spyder but not in Atom or GitHub.

Reads the text in a given file and writes it back to another file.
That seems to fix the issue.

"""
import os
import shutil
import tkinter as tk
from tkinter import filedialog


root = tk.Tk()
root.withdraw()

# GUI request filenames (note, must use askopenfilenames, not askopenfile, because that also opens the files and I had trouble closing them without losing data)
filenames = filedialog.askopenfilenames(initialdir='.',title = "Select file", filetypes=[["Python Files","*.py"],["Script Files","*.sh"]])

for f in filenames:
    fname = os.path.relpath(f)
    forg = shutil.copy(fname,fname+"_org")  # Copy the file for backup purposes
    print(fname+" -> " +os.path.relpath(forg))
    fr = open(forg,'r')     # Read the copied original, and write to a new file, this fixes the stupid end of line problem
    fw = open(fname,'w')
    fw.write(fr.read())
    fw.close()
    fr.close()
    print("Fixed: " +os.path.relpath(fname))
print("Fixed all requested files.")

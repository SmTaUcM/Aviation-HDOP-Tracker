'''#-------------------------------------------------------------------------------------------------------------------------------------------------#
# Name:        compile.py
# Purpose:     Used to compile filename.py into filename.exe.
# Version:     v1.00
# Author:      Stuart. Macintosh
#
# Created:     17/01/2021
# Copyright:   Stuart Macintosh
# Licence:     GNU v3
#-------------------------------------------------------------------------------------------------------------------------------------------------#'''

#----------------------------------------------------------------------------------------------------------------------------------------------------#
#                                                                      Imports.                                                                      #
#----------------------------------------------------------------------------------------------------------------------------------------------------#
import PyInstaller.__main__
import os
import shutil
from zipfile import ZipFile, ZIP_DEFLATED
import platform
import sys
#----------------------------------------------------------------------------------------------------------------------------------------------------#


#----------------------------------------------------------------------------------------------------------------------------------------------------#
#                                                                     Main Program.                                                                  #
#----------------------------------------------------------------------------------------------------------------------------------------------------#
# Detect the location of the source folder.
os.chdir("..")
appDir = os.path.abspath(os.curdir)
appName = appDir.split("\\")[-1]

# Remove any old builds of the app.
print("\nRemoving old build files...")
shutil.rmtree(appDir + "\\_Compiler\\" + appName, ignore_errors=True)
try:
    os.remove(appDir + "\\_Compiler\\%s.zip"%appName)
except FileNotFoundError:
    pass

# Copy the required icon.ico file into the _Compiler folder.
print("\nCopying icon.ico icon file...")
shutil.copy(appDir + "\\_Resource\\icon.ico", appDir + "\\_Compiler\\")

# Compile the app.
print("\nCompiling %s.exe...\n"%appName)
PyInstaller.__main__.run([
     "--clean",
#     "--onefile",
     "--windowed",
     "--icon=icon.ico",
     os.path.join(appDir, "%s.py"%appName),
])
print("\%s.exe created."%appName)

# Clean up the build, copy in 'Settings' and 'Data' folders. Remove unnecessary files and renaming 'dist' to 'appName'.
print("\nCopying data and settings folders...")
shutil.rmtree(appDir + "\\_Compiler\\build", ignore_errors=True)
os.remove(appDir + "\\_Compiler\\%s.spec"%appName)
os.remove(appDir + "\\_Compiler\\icon.ico")
shutil.copytree(appDir + "\\_Compiler\\mpl_toolkits", appDir + "\\_Compiler\\dist\\%s\\mpl_toolkits"%appName)
shutil.copytree(appDir + "\\Logs", appDir + "\\_Compiler\\dist\\%s\\Logs"%appName)
shutil.copy(appDir + "\\README.md", appDir + "\\_Compiler\\dist\\%s\\"%appName)
shutil.copy(appDir + "\\LICENSE", appDir + "\\_Compiler\\dist\\%s\\"%appName)
shutil.copytree(appDir + "\\_Compiler\\dist\\%s"%appName, appDir + "\\_Compiler\\%s"%(appName))
shutil.rmtree(appDir + "\\_Compiler\\dist", ignore_errors=True)

# Create appName.zip for distribution.
print("\nCreating %s.zip. Please wait..."%appName)
with ZipFile('_Compiler\\%s.zip'%appName, 'w', compression=ZIP_DEFLATED, compresslevel=9) as zipObj:
   # Iterate over all the files in directory
    for folderName, subfolders, filenames in os.walk(os.getcwd() + "\\_Compiler\\%s"%appName):
        for filename in filenames:
           # Create complete filepath of file in directory
           filePath = os.path.join(folderName, filename)
           # Add file to zip
           zipObj.write(filePath, filePath.split("_Compiler\\")[1])
print("\n%s.zip created."%appName)

# Tell the user that compilation is complete.
bits = sys.version[ : sys.version.index(" bit")][-3:]
version = platform.platform().split("-")[0] + bits + "-bit"
print("\n\n----------- Compile for %s Complete -----------\n\n" % version)
#----------------------------------------------------------------------------------------------------------------------------------------------------#

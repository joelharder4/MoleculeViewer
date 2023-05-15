### Molecule Viewer
Author: Joel Harder
Last Edited: April 5, 2023

This project is a python 3 based webserver intended for storing and viewing various details about any molecules or atoms. 
To get started, you can upload any molecule (in the official .sdf format). A large amount of these files that you can
download to try can be found at: https://pubchem.ncbi.nlm.nih.gov/ by searching for the name of the molecule.

##### Compiling on Linux
to compile the _molecule library (including swig) use the command: `make`. 
for an extra layer of assurance use: `make clean` beforehand but it is not necessary

##### Running
to run the webserver use the command `python server.py port#` where 'port#' is the port you want to host it on.

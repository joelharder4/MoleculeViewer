# Molecule Viewer
> Course: **CIS\*2750**
> Author: **Joel Harder**
> Last Edited: **April 5, 2023**

## About this Project

This project is a python 3 based webserver that utilizes a c library imported to python using the swig development tool. It is intended for storing and viewing various details about any molecules or atoms. 

To get started, you can upload any molecule (in the official .sdf format). A large amount of these files can be found at: https://pubchem.ncbi.nlm.nih.gov/ by searching for the name of the molecule.

## Compiling
to compile the program type
```
make all
``` 
If an issue occurs while compiling, run `make clean` then try again.

## Running
to start the web server use the command 
```
python server.py <port#>
``` 
where `<port#>` is the port number you want to host it on.

Once the server is running, open `http://localhost:<port#>/` in your preferred browser. Replace `<port#>` with the port number you used earlier

## Screenshots

### Home Page
![A screenshot of the home page](images/screenshots/home_page.png?raw=true "Home Page")
<br><br><br>

### Molecule Database
![A screenshot of the page that lists all molecules in the database](images/screenshots/molecule_database.png?raw=true "Molecule Database")

### Element Database
![A screenshot of the page that lists all elements in the database](images/screenshots/element_database.png?raw=true "Element Database")

### Viewing Molecules
![A screenshot of the page that displays an svg of a molecule](images/screenshots/view_caffeine.png?raw=true "View of Caffeine")
<br><br>

### Rotating Molecules
![A screenshot of the page that displays an svg of a molecule and the view is rotated](images/screenshots/view_rotated_isopentanol.png?raw=true "Rotated View of Isopentanol")

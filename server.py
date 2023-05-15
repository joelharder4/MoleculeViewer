import MolDisplay
import sys
import urllib
import json
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from string import Template
import re
import molsql
import molecule

# my port is 51485

molRow = Template("""            <tr>
                <td>$name</td>
                <td>$atomnum</td>
                <td>$bondnum</td>
                <td>
                    <a href="/molecules/$name.view">
                        <img src="eye.png" alt="view molecule" class="view">
                    </a>
                </td>
                <td>
                    <a href="/molecules/$name.deleteMol">
                        <img src="trash.png" alt="delete molecule" class="delete">
                    </a>
                </td>
            </tr>\n""")

elemRow = Template("""            <tr>
                <td>$name</td>
                <td>$id</td>
                <td>$number</td>
                <td>$radius</td>
                <td>#$colour1</td>
                <td>#$colour2</td>
                <td>#$colour3</td>
                <td>
                    <a href="/$name.deleteElem">
                        <img src="trash.png" alt="delete element" class="delete">
                    </a>
                </td>
            </tr>\n""")


def copy_mol(mol=molecule.molecule):
    newMol = MolDisplay.Molecule()
    for i in range(mol.atom_no):
        atom = mol.get_atom(i)
        newMol.append_atom( atom.element, atom.x, atom.y, atom.z )
    for i in range(mol.bond_no):
        bond = mol.get_bond(i)
        newMol.append_bond( bond.a1, bond.a2, bond.epairs )
    return newMol



def load_img(filename):
    with open("images/" + filename, 'rb') as file_handle:
        return file_handle.read()

def load_html( filename, molname="" ):
    html = ""
    if filename == "view.html":
        with open("html/view.html", "r") as fp:
            html = fp.read()

        html = html.replace("molname", molname)
    
    
    elif filename == "mol.html":
        with open("html/mol.html", "r") as fp:
            html = fp.read()

        db = molsql.Database(reset=False)
        mols,names = db.load_all_mol()
        tablestr = ""
        
        for mol,name in zip(mols, names):
            tablestr += molRow.substitute( name=name[0], atomnum=mol.atom_no, bondnum=mol.bond_no )
        
        html = html.replace("moleculerows", tablestr)
    
    
    elif filename == "elem.html":
        with open("html/elem.html", "r") as fp:
            html = fp.read()
        
        db = molsql.Database(reset=False)
        data = db.conn.execute( """SELECT * FROM Elements;""" )
        elements = data.fetchall()
        tablestr = ""
        
        for el in elements:
            tablestr += elemRow.substitute( number=el[0], id=el[1], name=el[2], colour1=el[3], colour2=el[4], colour3=el[5], radius=el[6] )
        
        html = html.replace("elementrows", tablestr)
    
    else:
        with open("html/" + filename, "r") as fp:
            html = fp.read()
    
    return bytes( str(html), "utf-8" )

def load_js():
    with open( "server.js", "r" ) as js:
        return bytes( js.read(), "utf-8" )

class Handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == "/" or self.path == "/home":
            
            self.send_response( 200 ); # OK
            
            # set headers to say we are sending html text and how long it is
            self.send_header( "Content-type", "text/html" )
            self.end_headers()

            # write the home page html to the client
            self.wfile.write( load_html("home.html") )
            
            
        elif self.path == "/molecules":
            
            self.send_response( 200 ); # OK
            
            self.send_header( "Content-type", "text/html" )
            self.end_headers()
            self.wfile.write( load_html("mol.html") )
            
            
        elif self.path == "/elements":
            
            self.send_response( 200 ); # OK
            
            self.send_header( "Content-type", "text/html" )
            self.end_headers()
            self.wfile.write( load_html("elem.html") )
            
            
        elif self.path.endswith(".png"):
            
            self.send_response( 200 ); # OK
            
            self.send_header( "Content-type", "image/png" )
            self.end_headers()
            
            name = re.split(r"\/|\.", self.path)[-2]
            self.wfile.write( load_img(name + ".png") )
            
        
        elif self.path.endswith( ".js" ):
            self.send_response( 200 ); # OK
            
            self.send_header( "Content-type", "text/js" )
            self.end_headers()
            self.wfile.write( load_js() )
        
        
        elif self.path.endswith( ".view" ):
            self.send_response( 200 ); # OK
            
            name = re.split(r"\/|\.", self.path)[-2]
            
            self.send_header( "Content-type", "text/html" )
            self.end_headers()
            self.wfile.write( load_html("view.html", name) )
        
        
        elif self.path.endswith( ".deleteMol" ):
            self.send_response( 200 ); # OK
            
            name = re.split(r"\/|\.", self.path)[-2]
            name = name.replace("%20", " ")
            db = molsql.Database(reset=False)
            db.rem_molecule( name )
            
            self.send_header( "Content-type", "text/html" )
            self.end_headers()
            self.wfile.write( load_html("mol.html") )
        
        
        elif self.path.endswith( ".deleteElem" ):
            self.send_response( 200 ); # OK
            
            name = re.split(r"\/|\.", self.path)[-2]
            name = name.replace("%20", " ")
            db = molsql.Database(reset=False)
            db.rem_element( name )
            
            self.send_header( "Content-type", "text/html" )
            self.end_headers()
            self.wfile.write( load_html("elem.html") )
        
        elif self.path.endswith( ".svg" ):
            self.send_response( 200 ); # OK
            
            # figure out the name of the molecule
            name = re.split(r"\/|\.", self.path)[-2]
            
            # find the name in the database
            db = molsql.Database(reset=False)
            mol = db.load_mol( name )
            mol.sort()
            MolDisplay.radius = db.radius()
            MolDisplay.element_name = db.element_name()
            MolDisplay.header += db.radial_gradients()
            
            self.send_header( "Content-type", "image/svg+xml" )
            self.end_headers()
            self.wfile.write( bytes(mol.svg(), "utf-8") )
        
        else:
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: not found", "utf-8" ) )
    
  
    def do_POST(self):
        if self.path.endswith(".sdf") and self.path.startswith("/molecule"):
            
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) )
            name = postvars["name"][0]
            sdf = postvars["file"][0]
            
            db = molsql.Database()
            db.add_molecule(name, None, sdf)
            
            self.send_response( 200 ); # OK
            
            self.send_header( "Content-type", "text/html" )
            self.end_headers()
            self.wfile.write( load_html("mol.html") )
            
        
        elif self.path.startswith("/element"):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) )
            name = postvars["name"][0]
            code = postvars["code"][0]
            num = postvars["number"][0]
            rad = postvars["radius"][0]
            c1 = postvars["colour1"][0]
            c2 = postvars["colour2"][0]
            c3 = postvars["colour3"][0]
            
            db = molsql.Database()
            db.add_element(name, code, num, rad, c1, c2, c3)
            
            self.send_response( 200 ); # OK
            
            self.send_header( "Content-type", "text/html" )
            self.end_headers()
            self.wfile.write( load_html("elem.html") )
        
        
        elif self.path.startswith("/view"):
            
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) )
            roll = int(postvars["roll"][0])
            pitch = int(postvars["pitch"][0])
            yaw = int(postvars["yaw"][0])
            
            #print("roll:", roll, "pitch:", pitch, "yaw:", yaw)
            name = re.split(r"\/|\.", self.path)[-2]
            db = molsql.Database()
            mol = db.load_mol(name)
            
            #print(roll, pitch, yaw)
            mol.rotate(roll, pitch, yaw)
            
            # sort before you call svg() method
            mol.sort()
            
            self.send_response( 200 ); # OK
            
            # set the content type
            self.send_header( "Content-type", "text/html" )
            self.end_headers()
            self.wfile.write( bytes(mol.svg(), "utf-8") )
        
        
        elif self.path.startswith("/spin"):
            
            name = re.split(r"\/|\.", self.path)[-2]
            db = molsql.Database()
            mol = db.load_mol(name)
            
            svgs = []
            for i in range(0, 360, 3):
                newMol = copy_mol(mol)
                newMol.rotate(i, 0, 0)
                newMol.sort()
                svgs.append(newMol.svg())
            
            for i in range(0, 360, 3):
                newMol = copy_mol(mol)
                newMol.rotate(0, i, 0)
                newMol.sort()
                svgs.append(newMol.svg())
            
            for i in range(0, 360, 3):
                newMol = copy_mol(mol)
                newMol.rotate(0, 0, i)
                newMol.sort()
                svgs.append(newMol.svg())
            
            self.send_response( 200 ); # OK
            
            # set the content type
            self.send_header( "Content-type", "application/json" )
            self.end_headers()
            
            jsonStr = json.dumps(svgs)
            self.wfile.write(  bytes( jsonStr, "utf-8") )
        
        else:
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: not found", "utf-8" ) )


# testing
if __name__ == "__main__":
    httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), Handler )
    try:
        print("Server open on port", sys.argv[1], "use CTRL+C to close")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer closing")
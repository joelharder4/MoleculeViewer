import molecule
import math
import molsql
from string import Template
from numpy import degrees

##############################################
# CHANGE THIS TO TRUE TO VIEW NIGHTMARE MODE #
##############################################
nightmare = True



svgSize = 2000
# svg file format header and footer
header = """<svg version="1.1" width="%d" height="%d"
                xmlns="http://www.w3.org/2000/svg">""" % (svgSize, svgSize)
footer = """</svg>"""


bondColour1 = Template("""  <linearGradient id="bond$num" x1="$x1" y1="$y1" x2="$x2" y2="$y2" gradientUnits="userSpaceOnUse">
    <stop offset="0%" stop-color="#454545" />
    <stop offset="25%" stop-color="#606060" />
    <stop offset="50%" stop-color="#454545" />
    <stop offset="100%" stop-color="#252525" />
  </linearGradient>""")

bondColour2 = Template("""  <linearGradient id="bond$num" x1="$x1" y1="$y1" x2="$x2" y2="$y2" gradientUnits="userSpaceOnUse">
    <stop offset="0%" stop-color="#252525" />
    <stop offset="25%" stop-color="#404040" />
    <stop offset="50%" stop-color="#252525" />
    <stop offset="100%" stop-color="#050505" />
  </linearGradient>""")

capColour1 = Template("""  <linearGradient id="cap$num" x1="$x1" y1="$y1" x2="$x2" y2="$y2" gradientUnits="userSpaceOnUse" gradientTransform="rotate($rotX,$rotY,$rotZ)">
    <stop offset="0%" stop-color="#454545" />
    <stop offset="25%" stop-color="#606060" />
    <stop offset="50%" stop-color="#454545" />
    <stop offset="100%" stop-color="#252525" />
  </linearGradient>""")

capColour2 = Template("""  <linearGradient id="cap$num" x1="$x1" y1="$y1" x2="$x2" y2="$y2" gradientUnits="userSpaceOnUse" gradientTransform="rotate($rotX,$rotY,$rotZ)">
    <stop offset="0%" stop-color="#252525" />
    <stop offset="25%" stop-color="#404040" />
    <stop offset="50%" stop-color="#252525" />
    <stop offset="100%" stop-color="#050505" />
  </linearGradient>""")

bondTemplate = Template("""  <polygon points="$p1x,$p1y $p2x,$p2y $p3x,$p3y $p4x,$p4y" fill="url(#bond$num)" />""")
capTemplate = Template("""  <ellipse cx="$cx" cy="$cy" rx="15" ry="$ry" transform="rotate($rotX,$rotY,$rotZ)" fill="url(#cap$num)" />""")

# x and y offset in pixels for displaying molecules
offsetx = svgSize/2
offsety = svgSize/2

radius = {}
element_name = {}

# wrapper class for the atom object
class Atom():
    def __init__(self, atom):
        self.atom = atom
        self.z = atom.z
    
    def __str__(self):
        return "element: %s  (x, y, z): (%lf, %lf, %lf)" % (self.atom.element, self.atom.x, self.atom.y, self.atom.z)
    
    def svg(self):
        global offsetx, offsety
        cx = (self.atom.x * 100.0) + offsetx # x value of the center of the atom
        cy = (self.atom.y * 100.0) + offsety # y value of the center of the atom
        
        try:
            r = radius[self.atom.element]
            c = element_name[self.atom.element]
        except KeyError:
            r = 40
            c = "Default"
            
        return """  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n""" % (cx, cy, r, c)


# wrapper class for the bond object
class Bond():
    def __init__(self, bond):
        self.bond = bond
        self.z = bond.z
    
    def __str__(self):
        b = self.bond
        string = """a1: %d  a2: %d  epairs: %d  
(x1, y1): (%f, %f)  
(x2, y2): (%f, %f)
z: %f  len: %f  dx: %f  dy: %f""" % (b.a1, b.a2, b.epairs, b.x1, b.y1, b.x2, b.y2, b.z, b.len, b.dx, b.dy)
        return string
    
    def svg(self):
        global offsetx, offsety
        # calculate the coordinates of the four points
        # in the rectangle that represents the bond
        p1x = (self.bond.x1*100.0 + offsetx) + self.bond.dy*10.0
        p1y = (self.bond.y1*100.0 + offsety) - self.bond.dx*10.0
        p2x = (self.bond.x1*100.0 + offsetx) - self.bond.dy*10.0
        p2y = (self.bond.y1*100.0 + offsety) + self.bond.dx*10.0
        
        p3x = (self.bond.x2*100.0 + offsetx) - self.bond.dy*10.0
        p3y = (self.bond.y2*100.0 + offsety) + self.bond.dx*10.0
        p4x = (self.bond.x2*100.0 + offsetx) + self.bond.dy*10.0
        p4y = (self.bond.y2*100.0 + offsety) - self.bond.dx*10.0
        return """  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n""" % (p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y)
    
    def svg2(self, bondNum=0):
        global offsetx, offsety
        # calculate the coordinates of the four points
        # in the rectangle that represents the bond
        p1x = (self.bond.x1*100.0 + offsetx) + self.bond.dy*15
        p1y = (self.bond.y1*100.0 + offsety) - self.bond.dx*15
        p2x = (self.bond.x1*100.0 + offsetx) - self.bond.dy*15
        p2y = (self.bond.y1*100.0 + offsety) + self.bond.dx*15
        
        p3x = (self.bond.x2*100.0 + offsetx) - self.bond.dy*15
        p3y = (self.bond.y2*100.0 + offsety) + self.bond.dx*15
        p4x = (self.bond.x2*100.0 + offsetx) + self.bond.dy*15
        p4y = (self.bond.y2*100.0 + offsety) - self.bond.dx*15
        
        atom1 = molecule.getAtomA1(self.bond)
        atom2 = molecule.getAtomA2(self.bond)
        
        # if bond is closer than a1
        if atom2.z > atom1.z:
            above = [p3x, p3y, p4x, p4y]
            below = [p1x, p1y, p2x, p2y]
            atomBelow = atom1
            atomAbove = atom2
        else:
            above = [p1x, p1y, p2x, p2y]
            below = [p3x, p3y, p4x, p4y]
            atomBelow = atom2
            atomAbove = atom1
        
        cx = (below[0] + below[2])/2
        cy = (below[1] + below[3])/2
        
        x = atomBelow.x - atomAbove.x
        y = atomBelow.y - atomAbove.y
        z = atomBelow.z - atomAbove.z
        
        ax = math.atan2( math.sqrt( y**2 + z**2 ), x)
        ay = math.atan2( math.sqrt( z**2 + x**2 ), y)
        az = math.atan2( math.sqrt( x**2 + y**2 ), z)
        
        if degrees(az) < 90:
            zratio = 1 - degrees(az)/90
        else:
            zratio = (degrees(az)-90)/90
        
        try:
            r = radius[atomBelow.element]
        except KeyError:
            r = 40
        
        lenDif = r - (r * zratio)
        
        minLen = r - math.sqrt(r**2 - (30**2 / 4))
        
        ry = round(zratio*15, 3)
        
        if lenDif > r - minLen:
            lenDif = r - minLen
        
        # if atomBelow is to the right of atomAbove
        if atomBelow.x > atomAbove.x:
            atomLeft = atomAbove
            atomRight = atomBelow
            below[0] -= lenDif * abs(self.bond.dx)
            below[2] -= lenDif * abs(self.bond.dx)
            cx -= lenDif * abs(self.bond.dx)
        else: # if atomBelow is to the left of atomAbove
            atomLeft = atomBelow
            atomRight = atomAbove
            below[0] += lenDif * abs(self.bond.dx)
            below[2] += lenDif * abs(self.bond.dx)
            cx += lenDif * abs(self.bond.dx)
        
        # if atomAbove is higher than atomBelow
        if atomBelow.y > atomAbove.y:
            below[1] -= lenDif * abs(self.bond.dy)
            below[3] -= lenDif * abs(self.bond.dy)
            cy -= lenDif * abs(self.bond.dy)
        else: # if atomAbove is lower than atomBelow
            below[1] += lenDif * abs(self.bond.dy)
            below[3] += lenDif * abs(self.bond.dy)
            cy += lenDif * abs(self.bond.dy)
        
        for i in range(4):
            below[i] = round(below[i], 4)
            above[i] = round(above[i], 4)
        
        m = (atomRight.y - atomLeft.y) / (atomRight.x - atomLeft.x)
        angle = math.degrees( math.atan( m ) ) + 90
        
        string = ""
        
        # if sloping upwards (m is backwards)
        if m < 0:
            if below[0] < below[2]:
                string += bondColour1.substitute( num=bondNum, x1=below[0], y1=below[1], x2=below[2], y2=below[3] ) + "\n"
                string += capColour1.substitute( num=bondNum, x1=below[2], y1=below[3], x2=below[0], y2=below[1], rotX=180-angle, rotY=cx, rotZ=cy ) + "\n"
            else:
                string += bondColour1.substitute( num=bondNum, x1=below[2], y1=below[3], x2=below[0], y2=below[1] ) + "\n"
                string += capColour1.substitute( num=bondNum, x1=below[0], y1=below[1], x2=below[2], y2=below[3], rotX=180-angle, rotY=cx, rotZ=cy ) + "\n"
        else:
            if below[0] < below[2]:
                tempx = below[0] - (30 * abs(self.bond.dy))
                tempy = below[1] + (30 * abs(self.bond.dx))
                string += bondColour2.substitute( num=bondNum, x1=below[2], y1=below[3], x2=tempx, y2=tempy ) + "\n"
                string += capColour2.substitute( num=bondNum, x1=below[2], y1=below[3], x2=tempx, y2=tempy, rotX=180-angle, rotY=cx, rotZ=cy ) + "\n"
            else:
                tempx = below[2] - (30 * abs(self.bond.dy))
                tempy = below[3] + (30 * abs(self.bond.dx))
                string += bondColour2.substitute( num=bondNum, x1=below[0], y1=below[1], x2=tempx, y2=tempy ) + "\n"
                string += capColour2.substitute( num=bondNum, x1=below[0], y1=below[1], x2=tempx, y2=tempy, rotX=180-angle, rotY=cx, rotZ=cy ) + "\n"
        
        string += bondTemplate.substitute( p1x=below[0], p1y=below[1], p2x=below[2], p2y=below[3], p3x=above[0], p3y=above[1], p4x=above[2], p4y=above[3], num=bondNum ) + "\n"
        string += capTemplate.substitute( cx=cx, cy=cy, ry=ry, rotX=angle, rotY=cx, rotZ=cy, num=bondNum ) + "\n"
        
        return string


# subclass for the molecule object
class Molecule(molecule.molecule):
    def __str__(self):
        string = "atoms:\n"
        # loop through every atom
        for i in range(self.atom_no):
            atom = Atom(self.get_atom(i))
            string = string + str(atom) + "\n"
        
        string = string + "bonds:\n"
        # loop through every bond
        for i in range(self.bond_no):
            bond = Bond(self.get_bond(i))
            string = string + str(bond) + "\n"
        
        return string
    
    
    def svg(self):
        # sumX = 0
        # sumY = 0
        # for i in range(self.atom_no):
        #     atom = self.get_atom(i)
        #     sumX += atom.x
        #     sumY += atom.y
        
        # print(sumX, sumY)
        # global offsety, offsetx, svgSize
        
        string = header
        i = 0
        j = 0
        
        # uses 'merge' algorithm from mergesort which
        # means it assumes the molecule is sorted
        while (i < self.atom_no and j < self.bond_no):
            atom = Atom(self.get_atom(i))
            bond = Bond(self.get_bond(j))
            
            # if the atom is farther away
            if (atom.z < bond.z):
                string = string + str(atom.svg())
                i += 1
            else: # if the atom is closer than the bond
                if nightmare == True:
                    string = string + str(bond.svg2(j+1))
                else:
                    string = string + str(bond.svg())
                j += 1
        
        # if all atoms are displayed
        if (i == self.atom_no):
            # add the remaining bonds
            for k in range(j, self.bond_no):
                bond = Bond(self.get_bond(k))
                if nightmare == True:
                    string = string + str(bond.svg2(k+1))
                else:
                    string = string + str(bond.svg())
                
        else: # if all bonds are displayed
            # add the remaining atoms
            for k in range(i, self.atom_no):
                atom = Atom(self.get_atom(k))
                string = string + str(atom.svg())
        
        string = string + footer
        return string
    
    
    
    def parse(self, fileObj, fileStr=""):
        # read the data from fileObj
        data = []
        if fileObj != None:
            for line in fileObj:
                data.append(line[:-1])
                # stop reading once you get the the line "M  END"
                if "M  END" in line:
                    break
        else:
            for line in fileStr.split('\n'):
                data.append(line)
        
        
        start = 3
        # find the line that has the counts
        for i,line in enumerate(data):
            if "V2000" in line:
                start = i
                break
        
        # split the line that has the number of atoms/bonds
        countLine = (data[start]).split()
        start += 1
        
        # get the number of atoms and bonds
        numAtom = int(countLine[0])
        numBond = int(countLine[1])
        
        # parse through the number of atoms
        for i in range(start, start + numAtom):
            split = data[i].split()
            x = float(split[0]) # x value is the first double
            y = float(split[1]) # y value is the second double
            z = float(split[2]) # z value is the third double
            element = split[3] # fourth value is the element
            self.append_atom( element, x, y, z )
        
        # parse through the number of bonds
        for i in range(start + numAtom, start + numAtom + numBond):
            split = data[i].split()
            atom1 = int(split[0]) - 1 # a1 is the first number
            atom2 = int(split[1]) - 1 # a2 is the first number
            electrons = int(split[2]) # epairs is the first number
            self.append_bond(atom1, atom2, electrons)
        


# testing
if __name__ == "__main__":
    mol = Molecule()

    # mol.append_atom( "O", 2.5369, -0.1550, 1.0000 )
    # mol.append_atom( "H", 3.0739, 0.1550, 1.5000 )
    # mol.append_atom( "H", 2.0000, 0.1550, 5.0000 )

    # atom references in append_bond start at 1 NOT 0
    # mol.append_bond( 1, 2, 1 )
    # mol.append_bond( 1, 3, 1 )
    
    # atom1 = Atom(mol.get_atom(0))
    # atom2 = Atom(mol.get_atom(1))
    # atom3 = Atom(mol.get_atom(2))
    
    # bond1 = Bond(mol.get_bond(0))
    # bond2 = Bond(mol.get_bond(1))
    
    # print(atom1)
    # print(atom2)
    # print(atom3)
    # print(bond1)
    # print(bond2)
    # print(atom1.svg(), end="")
    # print(atom2.svg(), end="")
    # print(bond1.svg(), end="")
    # print(mol, end="")
    # print(mol.svg())
    
    # fileObj = open("sdf/water-3D-structure-CT1000292221.sdf", "r")
    # fileObj = open("sdf/CID_31260.sdf", "r")
    # fileObj = open("sdf/caffeine-3D-structure-CT1001987571.sdf", "r")
    # mol.parse(fileObj)
    
    # f = open("test.svg", "w")
    # f.write(mol.svg())
    # f.close()
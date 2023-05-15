import os
import sqlite3
import MolDisplay

radialGradientSVG = """
  <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
     <stop offset="0%%" stop-color="#%s"/>
     <stop offset="50%%" stop-color="#%s"/>
     <stop offset="100%%" stop-color="#%s"/>
  </radialGradient>"""

class Database():
    def __init__(self, reset=False):
        # if we should recreate the database and it already exists
        if (reset == True and os.path.exists("molecules.db")):
            # remove the database file
            os.remove("molecules.db")
            
        # create or open the database
        self.conn = sqlite3.connect("molecules.db")

    def create_tables(self):
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Elements ( 
                                ELEMENT_NO   INTEGER     NOT NULL,
                                ELEMENT_CODE VARCHAR(3)  NOT NULL,
                                ELEMENT_NAME VARCHAR(32) NOT NULL,
                                COLOUR1      CHAR(6)     NOT NULL,
                                COLOUR2      CHAR(6)     NOT NULL,
                                COLOUR3      CHAR(6)     NOT NULL,
                                RADIUS       DECIMAL(3)  NOT NULL,
                                PRIMARY KEY (ELEMENT_CODE) );""" )
        
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Atoms ( 
                                ATOM_ID      INTEGER      NOT NULL  PRIMARY KEY  AUTOINCREMENT  ,
                                ELEMENT_CODE VARCHAR(3)   NOT NULL,
                                X            DECIMAL(7,4) NOT NULL,
                                Y            DECIMAL(7,4) NOT NULL,
                                Z            DECIMAL(7,4) NOT NULL,
                                FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements );""" )
        
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Bonds ( 
                                BOND_ID      INTEGER   NOT NULL  PRIMARY KEY  AUTOINCREMENT,
                                A1           INTEGER   NOT NULL,
                                A2           INTEGER   NOT NULL,
                                EPAIRS       INTEGER   NOT NULL );""" )
        
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Molecules ( 
                                MOLECULE_ID  INTEGER   NOT NULL  PRIMARY KEY  AUTOINCREMENT,
                                NAME         TEXT      NOT NULL  UNIQUE );""" )
        
        self.conn.execute( """CREATE TABLE IF NOT EXISTS MoleculeAtom ( 
                                MOLECULE_ID  INTEGER   NOT NULL,
                                ATOM_ID      INTEGER   NOT NULL,
                                PRIMARY KEY (MOLECULE_ID,ATOM_ID),
                                FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules ON DELETE CASCADE,
                                FOREIGN KEY (ATOM_ID)     REFERENCES Atoms ON DELETE CASCADE);""" )
        
        self.conn.execute( """CREATE TABLE IF NOT EXISTS MoleculeBond ( 
                                MOLECULE_ID  INTEGER   NOT NULL,
                                BOND_ID      INTEGER   NOT NULL,
                                PRIMARY KEY (MOLECULE_ID,BOND_ID),
                                FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules ON DELETE CASCADE,
                                FOREIGN KEY (BOND_ID)     REFERENCES Bonds ON DELETE CASCADE);""" )
        self.conn.commit()
    
    def __setitem__(self, table, values):
        if (values == None):
            print("Did not pass any values to Database.__setitem__()")
            return None
        
        if (table == "Elements"):
            command = """INSERT OR IGNORE
                        INTO   Elements ( ELEMENT_NO, ELEMENT_CODE, ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3, RADIUS )
                        VALUES          ( %s,         '%s',         '%s',         '%s',    '%s',    '%s',    %s);
                        """ % (values)
            self.conn.execute( command )

        elif (table == "Atoms"):
            cur = self.conn.cursor()
            command = """INSERT
                        INTO   Atoms ( ELEMENT_CODE, X,  Y,  Z  )
                        VALUES       ( '%s',         %s, %s, %s );
                        """ % (values)
            cur.execute( command )
            return cur.lastrowid
        
        elif (table == "Bonds"):
            cur = self.conn.cursor()
            command = """INSERT
                        INTO   Bonds ( A1, A2, EPAIRS )
                        VALUES       ( %s, %s, %s     );
                        """ % (values)
            cur.execute( command )
            return cur.lastrowid
        
        elif (table == "Molecules"):
            command = """INSERT OR IGNORE
                        INTO Molecules ( NAME )
                        VALUES         ( '%s' );
                        """ % (values)
            self.conn.execute( command )
        
        elif (table == "MoleculeAtom"):
            command = """INSERT OR IGNORE
                        INTO MoleculeAtom ( MOLECULE_ID, ATOM_ID )
                        VALUES            ( %s,          %s );
                        """ % (values)
            self.conn.execute( command )
        
        elif (table == "MoleculeBond"):
            command = """INSERT OR IGNORE
                        INTO MoleculeBond ( MOLECULE_ID, BOND_ID )
                        VALUES            ( %s,          %s );
                        """ % (values)
            self.conn.execute( command )
        
        else:
            print("Invalid SQL table name passed to Database.__setitem__()")
        
        
        
    
    def add_atom(self, molname, atom):
        atomID = self.__setitem__( "Atoms", (atom.element, atom.x, atom.y, atom.z) )
        
        data = self.conn.execute( """ SELECT MOLECULE_ID FROM Molecules WHERE NAME = '%s' """ % (molname) )
        molID = data.fetchone()[0]
        
        self.__setitem__( "MoleculeAtom", (molID, atomID) )
    
    
    def add_bond(self, molname, bond):
        bondID = self.__setitem__( "Bonds", (bond.a1, bond.a2, bond.epairs) )
        
        data = self.conn.execute( """ SELECT MOLECULE_ID FROM Molecules WHERE NAME = '%s'; """ % (molname) )
        molID = data.fetchone()[0]
        
        self.__setitem__( "MoleculeBond", (molID, bondID) )
    
    
    def add_molecule(self, name, fp, fileStr=""):
        mol = MolDisplay.Molecule()
        mol.parse(fp, fileStr)
        
        self.__setitem__( "Molecules", (name) )
        
        for i in range(mol.atom_no):
            self.add_atom( name, mol.get_atom(i) )
        
        for i in range(mol.bond_no):
            self.add_bond( name, mol.get_bond(i) )
        self.conn.commit()
    
    
    
    def add_element(self, name, code, number, radius, colour1, colour2, colour3):
        self.__setitem__( "Elements", (number, code, name, colour1, colour2, colour3, radius) )
        self.conn.commit()
    
    
    def rem_molecule(self, name):
        # remove all the atoms
        command = """   SELECT Atoms.ATOM_ID FROM Molecules, MoleculeAtom, Atoms 
                        WHERE (Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                        AND    MoleculeAtom.ATOM_ID  = Atoms.ATOM_ID
                        AND    Molecules.NAME        = '%s'); """ % (name)
        atoms = self.conn.execute( command )
        atoms = atoms.fetchall()
        for atom in atoms:
            command = "DELETE FROM Atoms WHERE ATOM_ID=%d" % (atom[0])
            self.conn.execute( command )
            command = "DELETE FROM MoleculeAtom WHERE ATOM_ID=%d" % (atom[0])
            self.conn.execute( command )
        
        # remove all the bonds
        command = """   SELECT Bonds.BOND_ID FROM Molecules, MoleculeBond, Bonds 
                        WHERE (Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                        AND    MoleculeBond.BOND_ID  = Bonds.BOND_ID
                        AND    Molecules.NAME        = '%s'); """ % (name)
        bonds = self.conn.execute( command )
        bonds = bonds.fetchall()
        for bond in bonds:
            command = "DELETE FROM Bonds WHERE BOND_ID=%d" % (bond[0])
            self.conn.execute( command )
            command = "DELETE FROM MoleculeBond WHERE BOND_ID=%d" % (bond[0])
            self.conn.execute( command )
        
        # remove the molecule
        command = "DELETE FROM Molecules WHERE NAME='%s'" % (name)
        self.conn.execute( command )
        
        self.conn.commit()
    
    def rem_element(self, name):
        command = """DELETE FROM Elements WHERE ELEMENT_NAME='%s';""" % (name)
        self.conn.execute( command )
        self.conn.commit()
    
    def load_mol(self, name):
        command = """   SELECT Atoms.*
                        FROM Molecules, MoleculeAtom, Atoms 
                        WHERE (Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                        AND    MoleculeAtom.ATOM_ID  = Atoms.ATOM_ID
                        AND    Molecules.NAME        = '%s'); """ % (name)
        
        dataAtoms = self.conn.execute( command )
        dataAtoms = dataAtoms.fetchall()
        
        command = """   SELECT Bonds.*
                        FROM Molecules, MoleculeBond, Bonds 
                        WHERE (Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                        AND    MoleculeBond.BOND_ID  = Bonds.BOND_ID
                        AND    Molecules.NAME        = '%s'); """ % (name)
        
        dataBonds = self.conn.execute( command )
        dataBonds = dataBonds.fetchall()
        
        # create a new molecule object
        mol = MolDisplay.Molecule()
        
        for atom in dataAtoms:
            mol.append_atom(atom[1], atom[2], atom[3], atom[4])
            
        for bond in dataBonds:
            mol.append_bond(bond[1], bond[2], bond[3])
        
        return mol
    
    
    def load_all_mol(self):
        data = self.conn.execute( """SELECT NAME FROM Molecules;""" )
        names = data.fetchall()
        mols = []
        
        for name in names:
            mols.append(self.load_mol(name))
        
        return mols,names
    
    def radius(self):
        dictionary = {}
        
        elements = self.conn.execute ("""SELECT ELEMENT_CODE,RADIUS FROM Elements;""")
        
        for elem in elements.fetchall():
            dictionary[elem[0]] = elem[1]
        
        return dictionary

    def element_name(self):
        dictionary = {}
        
        elements = self.conn.execute ("""SELECT ELEMENT_CODE,ELEMENT_NAME FROM Elements;""")
        
        for elem in elements.fetchall():
            dictionary[elem[0]] = elem[1]
        
        return dictionary

    def radial_gradients(self):
        elements = self.conn.execute ("""SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3
                                            FROM Elements;""")
        fullStr = radialGradientSVG % ("Default", "9830B3", "2E0E36", "230B29")
        
        for elem in elements.fetchall():
            curSVG = radialGradientSVG % (elem)
            fullStr = fullStr + curSVG
        fullStr += "\n"
        
        return fullStr
    

if __name__ == "__main__":
    db = Database(reset=True)
    db.create_tables()
    db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 )
    db['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 )
    db['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 )
    db['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 )
    
    fp = open( 'sdf/water-3D-structure-CT1000292221.sdf' )
    db.add_molecule( 'Water', fp )
    fp = open( 'sdf/caffeine-3D-structure-CT1001987571.sdf' )
    db.add_molecule( 'Caffeine', fp )
    fp = open( 'sdf/CID_31260.sdf' )
    db.add_molecule( 'Isopentanol', fp )
    
    # db2 = Database(reset=False)
    
    # MolDisplay.radius = db2.radius()
    # MolDisplay.element_name = db2.element_name()
    # for molecule in [ 'Water', 'Caffeine', 'Isopentanol' ]:
    #     mol = db2.load_mol( molecule )
    #     mol.sort()
    #     fp = open( molecule + ".svg", "w" )
    #     fp.write( mol.svg() )
    #     fp.close()
    
    # print( "Elements:\n", db2.conn.execute( "SELECT * FROM Elements;" ).fetchall() )
    # print( "Molecules:\n", db2.conn.execute( "SELECT * FROM Molecules;" ).fetchall() )
    # print( "Atoms:\n", db2.conn.execute( "SELECT * FROM Atoms;" ).fetchall() )
    # print( "Bonds:\n", db2.conn.execute( "SELECT * FROM Bonds;" ).fetchall() )
    # print( "MoleculeAtom:\n", db2.conn.execute( "SELECT * FROM MoleculeAtom;" ).fetchall() )
    # print( "MoleculeBond:\n", db2.conn.execute( "SELECT * FROM MoleculeBond;" ).fetchall() )
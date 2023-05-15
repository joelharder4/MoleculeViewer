/* mol.c
 * Joel Harder
 * Created: January 12, 2023
 * C library to implement representing and manipulating molecules
*/

#include "mol.h"


// set the components of the atom to the values of the other parameters
void atomset( atom *atom, char element[3], double *x, double *y, double *z ) {

    // error detection for dereferencing NULL pointer
    if (atom == NULL) {
        return;
    }
    
    strcpy(atom->element, element); // copy the strings
    atom->x = *x;                   // copy the x value
    atom->y = *y;                   // copy the y value
    atom->z = *z;                   // copy the z value
}

// set the values of other parameters to the components of atom
void atomget( atom *atom, char element[3], double *x, double *y, double *z ) {

    // error detection for dereferencing NULL pointer
    if (atom == NULL) {
        return;
    }
    
    strcpy(element, atom->element); // copy the strings
    *x = atom->x;                   // copy the x value
    *y = atom->y;                   // copy the y value
    *z = atom->z;                   // copy the z value
}

// set the components of the bond to the values of the other parameters
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ) {

    // error detection for dereferencing NULL pointer
    if (bond == NULL) {
        return;
    }

    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->atoms = *atoms;
    bond->epairs = *epairs;
}

// set the values of other parameters to the components of atom
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ) {

    // error detection for dereferencing NULL pointer
    if (bond == NULL) {
        return;
    }

    *a1 = bond->a1;
    *a2 = bond->a2;
    *atoms = bond->atoms;
    *epairs = bond->epairs;
}

// allocates enough memory for a new molecule struct and returns the address of it
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ) {
    molecule* newMol;
    newMol = malloc(sizeof(struct molecule));

    newMol->atom_no = 0;
    newMol->bond_no = 0;
    newMol->atom_max = atom_max;
    newMol->bond_max = bond_max;

    // allocate memory for arrays
    newMol->atoms = malloc(sizeof(struct atom) * atom_max);
    newMol->atom_ptrs = malloc(sizeof(struct atom*) * atom_max);

    newMol->bonds = malloc(sizeof(struct bond) * bond_max);
    newMol->bond_ptrs = malloc(sizeof(struct bond*) * bond_max);

    return newMol;
}


//helper function that I created to copy the values of an atom to another atom
void atomcopy(atom *src, atom* toCopy ) {
    toCopy->x = src->x;
    toCopy->y = src->y;
    toCopy->z = src->z;
    strcpy(toCopy->element, src->element);
} 

// copies all bonds, atoms, and pointers from one molecule into a duplicate and returns the address of the copy
molecule* molcopy( molecule *src ) {

    molecule* copy = NULL;

    if (src == NULL) {
        return copy;
    }

    // create a new molecule to copy values into
    copy = molmalloc( src->atom_max, src->bond_max );

    // molappend copies of all atoms
    for (int i = 0; i < src->atom_no; i++) {
        atom atomCopy;
        atomcopy(&(src->atoms[i]), &atomCopy);
        //printf("ATOMS: %s %lf %lf %lf\n", atomCopy.element, atomCopy.x, atomCopy.y, atomCopy.z); // debug
        molappend_atom(copy, &atomCopy);
    }

    // molappend copies of all bonds
    for (int i = 0; i < src->bond_no; i++) {

        molappend_bond(copy, &(src->bonds[i]));

        (copy->bonds[i]).atoms = copy->atoms;

        // // save the indexes of the atoms in the atoms array
        // index_a = ((src->bonds[i]).a1 - src->atoms);
        // index_b = ((src->bonds[i]).a2 - src->atoms);

        // // update a1 and a2 to point to atoms in new molecule
        // (copy->bonds[i]).a1 = &(copy->atoms[index_a]);
        // (copy->bonds[i]).a2 = &(copy->atoms[index_b]);
    }

    return copy;
}


// frees every value of a molecule
void molfree( molecule *ptr ) {

    // error detection for dereferencing NULL pointer
    if (ptr == NULL) {
        return;
    }

    free(ptr->atoms);
    free(ptr->atom_ptrs);

    free(ptr->bonds);
    free(ptr->bond_ptrs);

    free(ptr);
}


// appends the atom parameter to the atoms array in the molecule given
void molappend_atom( molecule *molecule, atom *atom ) {

    // does the molecule have max atoms
    if (molecule->atom_no >= molecule->atom_max) {
        
        if (molecule->atom_max == 0) {
            molecule->atom_max = 1;
        } else {
            // double the max
            molecule->atom_max = molecule->atom_max * 2;
        }

        // struct atom* old_atoms = molecule->atoms; // address of atoms array before realloc

        // realloc atoms and atom_ptrs arrays
        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * molecule->atom_max);

        // if realloc failed then exit(0)
        if (molecule->atoms == NULL || molecule->atom_ptrs == NULL) {
            exit(0);
        }

        // int index_a, index_b;

        // loop through every bond
        for (int i = 0; i < molecule->bond_no; i++) {

            (molecule->bonds[i]).atoms = molecule->atoms;

            // // save the index of the atom according to the previous
            // // array address (since it may have changed during realloc)
            // index_a = ((molecule->bonds)[i].a1 - old_atoms);
            // index_b = ((molecule->bonds)[i].a2 - old_atoms);

            // // assign the bond a1 and a2 to the same atoms in the new location
            // (molecule->bonds)[i].a1 = &(molecule->atoms[index_a]);
            // (molecule->bonds)[i].a2 = &(molecule->atoms[index_b]);

            // // printf("index_a: %d   index_b: %d\n", index_a, index_b); // debug
        }

        // push atom onto the array
        (molecule->atoms)[molecule->atom_no] = *atom;
        for (int i = 0; i <= molecule->atom_no; i++) {
            (molecule->atom_ptrs)[i] = &(molecule->atoms)[i];
        }

        //printf("atom_max = %d\n",molecule->atom_max); // debug
    } else {
        // dont have to realloc because it has not reached the atom_max atoms
        (molecule->atoms)[molecule->atom_no] = *atom;
        (molecule->atom_ptrs)[molecule->atom_no] = &((molecule->atoms)[molecule->atom_no]);
    }

    molecule->atom_no++;
}


// appends the bond parameter to the atoms array in the molecule given
void molappend_bond( molecule *molecule, bond *bond ) {

    // if the molecule have max bonds
    if (molecule->bond_no >= molecule->bond_max) {
        
        if (molecule->bond_max == 0) {
            molecule->bond_max = 1;
        } else {
            molecule->bond_max = molecule->bond_max * 2;
        }

        // realloc atoms and atom_ptrs arrays
        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * molecule->bond_max);

        if (molecule->bonds == NULL || molecule->bond_ptrs == NULL) {
            exit(0);
        }

        (molecule->bonds)[molecule->bond_no] = *bond;
        for (int i = 0; i <= molecule->bond_no; i++) {
            (molecule->bond_ptrs[i]) = &(molecule->bonds[i]);
        }

        //printf("bond_max = %d\n",molecule->bond_max); // debug
    } else {
        molecule->bonds[molecule->bond_no] = *bond;
        molecule->bond_ptrs[molecule->bond_no] = &(molecule->bonds[molecule->bond_no]);
    }

    molecule->bond_no++;
}


// compare function for qsort on atom_ptrs array
int atom_comp(const void *a, const void *b) {
    atom** atom_a = (atom **)a;
    atom** atom_b = (atom **)b;
    //printf("a: %f    b: %f\n", (**atom_a).z, (**atom_b).z); //debug
    if ((*atom_a)->z > (*atom_b)->z) {
        return 1;
    } else if ((*atom_a)->z < (*atom_b)->z) {
        return -1;
    } else {
        return 0;
    }
}

// compare function for qsort on bond_ptrs array
int bond_comp(const void *a, const void *b) {
    bond** bond_a = (bond **)a;
    bond** bond_b = (bond **)b;

    if ((*bond_a)->z > (*bond_b)->z) {
        return 1;
    } else if ((*bond_a)->z < (*bond_b)->z) {
        return -1;
    } else {
        return 0;
    }
}

// sorts atom_ptrs and bond_ptrs array in molecule
void molsort( molecule *molecule ) {
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(struct atom*), atom_comp);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(struct bond*), bond_comp);
}

// transforms the given xform_matrix into an x rotation matrix of deg degrees
void xrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double radians = (deg * PI)/180;
    //printf("radians: %f\n", radians);

    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(radians);
    xform_matrix[1][2] = -sin(radians);

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(radians);
    xform_matrix[2][2] = cos(radians);
}

// transforms the given xform_matrix into an y rotation matrix of deg degrees
void yrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double radians = (deg * PI)/180;

    xform_matrix[0][0] = cos(radians);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(radians);

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = -sin(radians);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(radians);
}

// transforms the given xform_matrix into an y rotation matrix of deg degrees
void zrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double radians = (deg * PI)/180;

    xform_matrix[0][0] = cos(radians);
    xform_matrix[0][1] = -sin(radians);
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = sin(radians);
    xform_matrix[1][1] = cos(radians);
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

// performs a rotation xform_matrix matrix on a molecule
void mol_xform( molecule *molecule, xform_matrix matrix ) {
    atom temp;

    for (int i = 0; i < molecule->atom_no; i++) {
        temp = molecule->atoms[i];
        //printf("temp: %f     actual: %f\n", temp.x, (molecule->atoms)[i].x);
        (molecule->atoms)[i].x = (matrix[0][0] * temp.x) + (matrix[0][1] * temp.y) + (matrix[0][2] * temp.z);
        (molecule->atoms)[i].y = (matrix[1][0] * temp.x) + (matrix[1][1] * temp.y) + (matrix[1][2] * temp.z);
        (molecule->atoms)[i].z = (matrix[2][0] * temp.x) + (matrix[2][1] * temp.y) + (matrix[2][2] * temp.z);
    }

    for (int i = 0; i < molecule->bond_no; i++) {
        compute_coords( &(molecule->bonds[i]) );
    }
}


rotations* spin( molecule *mol ) {
    rotations* rots = malloc(sizeof(struct rotations));
    xform_matrix xmatrix, ymatrix, zmatrix;
    molecule *tempMolx, *tempMoly, *tempMolz;

    for (int i = 0; i < 360; i += 5) {
        tempMolx = molcopy(mol);
        tempMoly = molcopy(mol);
        tempMolz = molcopy(mol);

        xrotation(xmatrix, i);
        yrotation(ymatrix, i);
        zrotation(zmatrix, i);

        mol_xform(tempMolx, xmatrix);
        mol_xform(tempMoly, ymatrix);
        mol_xform(tempMolz, zmatrix);

        molsort(tempMolx);
        molsort(tempMoly);
        molsort(tempMolz);

        (rots->x)[(i/5)] = tempMolx;
        (rots->y)[(i/5)] = tempMoly;
        (rots->z)[(i/5)] = tempMolz;
    }

    return rots;
}


void rotationsfree( rotations *rotations ) {

    for(int i = 0; i < 72; i++) {
        molfree((rotations->x)[i]);
        molfree((rotations->y)[i]);
        molfree((rotations->z)[i]);
    }

    free(rotations);
}



void compute_coords( bond *bond ) {
    if (bond == NULL) {
        return;
    }

    double z1 = (bond->atoms[bond->a1]).z;
    double z2 = (bond->atoms[bond->a2]).z;

    bond->z = (z1 + z2) / 2;
    bond->x1 = (bond->atoms[bond->a1]).x;
    bond->x2 = (bond->atoms[bond->a2]).x;
    bond->y1 = (bond->atoms[bond->a1]).y;
    bond->y2 = (bond->atoms[bond->a2]).y;

    double difX = pow(bond->x2 - bond->x1, 2);
    double difY = pow(bond->y2 - bond->y1, 2);
    // double difZ = pow(z2 - z1, 2);
    bond->len = sqrt(difX + difY);

    bond->dx = ((bond->x2 - bond->x1) / bond->len);
    bond->dy = ((bond->y2 - bond->y1) / bond->len);
}



atom* getAtomA1(bond* bond) {
    return &(bond->atoms[bond->a1]);
}

atom* getAtomA2(bond* bond) {
    return &(bond->atoms[bond->a2]);
}


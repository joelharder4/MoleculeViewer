/* mol.h
 * Joel Harder
 * Created: January 12, 2023
 * header file for C library to implement representing and manipulating molecules
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265359

typedef struct atom
{
char element[3];
double x, y, z;
} atom;


typedef struct bond
{
unsigned short a1, a2;
unsigned char epairs;
atom *atoms;
double x1, x2, y1, y2, z, len, dx, dy;
} bond;


typedef struct molecule
{
unsigned short atom_max, atom_no;
atom *atoms, **atom_ptrs;
unsigned short bond_max, bond_no;
bond *bonds, **bond_ptrs;
} molecule;


typedef struct rotations
{
molecule *x[72];
molecule *y[72];
molecule *z[72];
} rotations;


typedef double xform_matrix[3][3];

void compute_coords( bond *bond );

void atomset( atom *, char[3], double *, double *, double * );

void atomget( atom *, char[3], double *, double *, double * );

//void bondset( bond *, atom *, atom *, unsigned char  ); // old prototype
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );

//void bondget( bond *, atom **, atom **, unsigned char * ); // old prototype
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );

molecule *molmalloc( unsigned short atom_max, unsigned short bond_max );

void atomcopy( atom *, atom*  ); // I made this helper function

molecule *molcopy( molecule * );

void molfree( molecule * );

void molappend_atom( molecule *, atom * );

void molappend_bond( molecule *, bond * );

int atom_comp(const void *, const void *); // I made this compare function for qsort

int bond_comp(const void *, const void *); // I made this compare function for qsort

void molsort( molecule * );

void xrotation( xform_matrix , unsigned short deg );

void yrotation( xform_matrix , unsigned short deg );

void zrotation( xform_matrix , unsigned short deg );

void mol_xform( molecule *, xform_matrix  );

rotations *spin( molecule * );

void rotationsfree( rotations * );

atom* getAtomA1(bond* bond);
atom* getAtomA2(bond* bond);


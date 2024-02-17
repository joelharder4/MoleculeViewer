CC = clang
CFLAGS = -std=c99 -Wall -pedantic

all: _molecule.so

clean:  
	rm -f *.o *.so molecule_wrap.c molecule.py

libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

_molecule.so: molecule_wrap.o libmol.so
	$(CC) molecule_wrap.o -shared -L. -lmol -L/usr/lib/python3.11/config-3.11m-x86_64-linux-gnu -lpython3.11 -o _molecule.so

molecule_wrap.o: molecule_wrap.c molecule.py
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I/usr/include/python3.11 -o molecule_wrap.o

molecule_wrap.c molecule.py: molecule.i
	swig -python molecule.i
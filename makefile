CC = clang
CFLAGS = -std=c99 -Wall -pedantic

all: _molecule.so

clean:  
	rm -f *.o *.so

libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

_molecule.so: molecule_wrap.o libmol.so
	$(CC) molecule_wrap.o -dynamiclib -shared -L. -lmol -L/usr/lib/python3.7/config-3.7m-x86_64-linux-gnu -lpython3.7m -o _molecule.so

molecule_wrap.o: molecule_wrap.c molecule.py
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I/usr/include/python3.7m -o molecule_wrap.o

molecule_wrap.c molecule.py: molecule.i
	swig3.0 -python molecule.i
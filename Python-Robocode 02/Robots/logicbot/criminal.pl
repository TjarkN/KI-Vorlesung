criminal(X):-american(X),weapon(Y),sells(X,Y,Z),hostile(Z).
owns(nono, m1).
missile(m1).
sells(west,X, nono):- missile(X), owns(nono,X).
weapon(X):-missile(X).
hostile(X):-enemy(X,america).
american(west).
enemy(nono,america).

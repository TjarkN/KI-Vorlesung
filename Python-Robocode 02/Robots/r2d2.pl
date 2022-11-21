:-[asearch].
:-[planning].

%fluents, changing over time, (should be only dynamically added from the python programm
:- dynamic fluent/1.
%e.g.fluent(energy(self,100)).

%facts, unlike fluents, don't change
:- dynamic fact/1.
fact(move_range(RG)):- RG is 50.0.
fact(turn_radian(RAD)):-RAD is pi/4.
fact(robot_size(25.0)).
fact(enemies(self,enemy)):-self\=enemy.

%%precondistions for the actions	
poss(setShotPossibleAt(Self,Enemy), S) :-
	holds(pos(Self,[_,_]), S),
	holds(pos(Enemy,[_,_]), S),
	holds(orientation(Self,_), S),
	fact(robot_size(_)),
	(fact(enemies(Self,Enemy));fact(enemies(Enemy,Self))).
	
poss(addEngery(X,5), S) :-
    holds(energy(X, _), S).

%Results of the actions
result(S1, setShotPossibleAt(Self,Enemy), S2) :-
	(fact(enemies(Self,Enemy));fact(enemies(Enemy,Self))),
	holds(pos(Self,[SX,SY]), S1),
	holds(pos(Enemy,[EX,EY]), S1),
	holds(orientation(Self,SO), S1),
	fact(robot_size(RS)),
	%Vektor, der von Self auf Enemy zeigt
	Dir_EX is EX-SX, 
	Dir_EY is EY-SY,
	%Blickrichtungsvektor von Self 
	Dir_SX is -sin(SO),
	Dir_SY is  cos(SO),
	%Betrag zur Normierung berechnen
	Norm_E is sqrt(Dir_EX * Dir_EX+Dir_EY * Dir_EY),
	Norm_S is sqrt(Dir_SX * Dir_SX+Dir_SY * Dir_SY),
	%Richtungsvektoren Normieren
	Norm_DIR_EX is Dir_EX / Norm_E,
	Norm_DIR_EY is Dir_EY / Norm_E,
	Norm_DIR_SX is Dir_SX / Norm_S,
	Norm_DIR_SY is Dir_SY / Norm_S,
	%winkel zwischen den Richtungsvectoren berechnen)
	GRAD is max(-1,min(Norm_DIR_EX * Norm_DIR_SX + Norm_DIR_EY * Norm_DIR_SY,1)),
	RAD_Between is acos(GRAD),
	%Halbierenden Winkel abhängig von Entfernug und Größe des Roboters berechnen
	Alpha is atan(RS / Norm_E),
	RAD_Between >= -Alpha,
	RAD_Between =< Alpha,
	replace_fluent(S1, shotPossibleAt(Self,Enemy), shotPossibleAt(Self,Enemy), S2).

result(S1, addEngery(X,5), S2) :-
    holds(energy(X, E), S1),
	Eplus5 is E + 5,
    replace_fluent(S1, energy(X, E),
                   energy(X, Eplus5), S2).
                  
%goal state definition	
%goal(orientation(self, O)):- O is pi.
%goal(energy(self,100.0)).
:-[asearch].
:-[planning].

%fluents, changing over time
fluent(location(robbie, hallway)).
fluent(location(car-key, hallway)).
fluent(location(garage-key, hallway)).
fluent(location(vacuum-cleaner, kitchen)).
fluent(door(hallway-kitchen, unlocked)).
fluent(door(kitchen-garage, locked)).
fluent(door(garage-car, locked)).
fluent(holding(nothing)).
fluent(clean(car, false)).

%facts, unlike fluents, don't change
fact(home(car-key, hallway)).
fact(home(garage-key, hallway)).
fact(home(vacuum-cleaner, kitchen)).	
	
% Lots of actions to declare here...
% Still less code than writing out the
% graph we're representing
% 
% Robbie's Action Repertoire :
%  - goTo(Origin, Destination)
%  - pickup(Item)
%  - drop(Item)
%  - put_away(Item) % the tidy version of drop
%  - unlock(Room1-Room2)
%  - lock(Room1-Room2)
%  - clean_car

poss(goto(L), S) :-
    % If robbie is in X and the door is unlocked
    holds(location(robbie, X), S),
    (   holds(door(X-L, unlocked), S)
    ;   holds(door(L-X, unlocked), S)
    ).
poss(pickup(X), S) :-
    % If robbie is in the same place as X and not
    % holding anything
    dif(X, robbie), % Can't pickup itself!
    holds(location(X, L), S),
    holds(location(robbie, L), S),
    holds(holding(nothing), S).
poss(put_away(X), S) :-
    % If robbie is holding X, it belongs in L
    % and robbie is in L (location(X, L) is implicit)
    holds(holding(X), S),
    fact(home(X, L)),
    holds(location(robbie, L), S).
poss(drop(X), S) :-
    % Can drop something if holding it
    % Can't drop nothing!
    dif(X, nothing),
    holds(holding(X), S).
poss(unlock(R1-R2), S) :-
    % Can unlock door between R1 and R2
    % Door is locked
    holds(door(R1-R2, locked), S),
    % Holding the key to the room
    holds(holding(R2-key), S),
    % Located in one of the rooms
    (   holds(location(robbie, R1), S)
    ;   holds(location(robbie, R2), S)
    ).
poss(lock(R1-R2), S) :-
    % Can lock door R1-R2
    % Only if it's locked, robbie has the key
    % and is in one of the rooms
    holds(door(R1-R2, unlocked), S),
    holds(holding(R2-key), S),
    (   holds(location(robbie, R1), S)
    ;   holds(location(robbie, R2), S)
    ).
poss(clean_car, S) :-
    % Robbie is in the car with the vacuum-cleaner
    holds(location(robbie, car), S),
    holds(holding(vacuum-cleaner), S).

result(S1, goto(L), S2) :-
    % Robbie moves
    holds(location(robbie, X), S1),
    replace_fluent(S1, location(robbie, X),
                   location(robbie, L), Sa),
    % If Robbie is carrying something, it moves too
    dif(Item, nothing),
    (   
        holds(holding(Item), S1),
        replace_fluent(Sa, location(Item, X),
                       location(Item, L), S2)
    ;   \+ holds(holding(Item), S1),
        S2 = Sa
    ).
result(S1, pickup(X), S2) :-
    % Robbie is holding X
    replace_fluent(S1, holding(nothing),
                   holding(X), S2).
result(S1, drop(X), S2) :-
    % Robbie is no-longer holding X,
    % its location is not changed
    replace_fluent(S1, holding(X),
                   holding(nothing), S2).
result(S1, put_away(X), S2) :-
    % Robbie is no-longer holding X,
    % its location is not changed
    replace_fluent(S1, holding(X),
                   holding(nothing), S2).
result(S1, unlock(R1-R2), S2) :-
    % Door R1-R2 is unlocked
    replace_fluent(S1, door(R1-R2, locked),
                       door(R1-R2, unlocked), S2).
result(S1, lock(R1-R2), S2) :-
    % Door R1-R2 is locked
    replace_fluent(S1, door(R1-R2, unlocked),
                   door(R1-R2, locked), S2).
result(S1, clean_car, S2) :-
    % The car is clean
    replace_fluent(S1, clean(car, false),
                   clean(car, true), S2).
				   
goal(clean(car, true)).
goal(door(garage-car, locked)).
goal(door(kitchen-garage, locked)).
% Everything must be tidied away
goal(location(X, L)) :- fact(home(X, L)).
goal(holding(nothing)).
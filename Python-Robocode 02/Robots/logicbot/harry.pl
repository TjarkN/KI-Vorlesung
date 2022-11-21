wizard(ron).
wizard(X):- hasBroom(X), hasWand(X).
hasWand(harry).
quidditchPlayer(harry).
hasBroom(X):- quidditchPlayer(X).
birth(harry, 1980).
currentYear(2020).
isOld(harry, Difference):- 
	birth(harry,BY),
	currentYear(CY),
	Difference is CY - BY.


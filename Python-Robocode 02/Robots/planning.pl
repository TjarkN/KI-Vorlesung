% s0, the initial situation, is the (ordered) set
% of fluents
s0(Situation) :-
    setof(S, fluent(S), Situation).

% Take a list of Actions and execute them
execute_process(S1, [], S1). % Nothing to do
execute_process(S1, [Action|Process], S2) :-
    poss(Action, S1), % Ensure valid Process
    result(S1, Action, Sd),
    execute_process(Sd, Process, S2).

% Does a fluent hold (is true) in the Situation?
% This is the query mechanism for Situations
% Use-case 1: check a known fluent
holds(Fluent, Situation) :-
    ground(Fluent), ord_memberchk(Fluent, Situation), !.
% Use-case 2: search for a fluent
holds(Fluent, Situation) :-
    member(Fluent, Situation).

% Utility to replace a fluent in the Situation
replace_fluent(S1, OldEl, NewEl, S2) :-
    ord_del_element(S1, OldEl, Sd),
    ord_add_element(Sd, NewEl, S2).

% The Goal Situation is the (ordered) set of fluents that
% describe a goal
goal_situation(S) :-
    setof(G, goal(G), S).

% Test to see if Situation satifies the Goal
% Note that the Situation can contain fluents
% not described in Goal
reached_goal(GoalSituation, Situation) :-
    ord_subtract(GoalSituation, Situation, []). % [] -> no goals not in Situation

% Checks if something is a proper list,
% with a bonus use of generating lists
% of increasing length
list([]).
list([_|T]) :-
    list(T).
:- use_module(library(heaps)).

% Use to order search
heuristic_distance_to_goal(GoalSituation, Situation, Distance) :-
    ord_subtract(GoalSituation, Situation, Dif),
    length(Dif, Distance).

% Add a Cost-Sit-Process triple to the search heap
% of open nodes. Carrying Process for interest.
add_to_open_nodes(AccCost, H1, Sit-Process, Goal, H2) :-
    heuristic_distance_to_goal(Goal, Sit, D),
    succ(AccCost, ActCost), % one action has been taken, so incr
    Priority is ActCost + D, % Priority cost
    add_to_heap(H1, Priority, ActCost-Sit-Process, H2).

% Add a list of Sit-Process Pairs
open_add_pairs(_, Heap, _, [], _, Heap).
open_add_pairs(AccCost, H1, Sits, [S-P|T], G, H2) :-
    (   ord_memberchk(S, Sits)
    ->  add_to_open_nodes(AccCost, H1, S-P, G, Hd)
    ;   Hd = H1
    ),
    open_add_pairs(AccCost, Hd, Sits, T, G, H2).

% Convenience predicate to heap
get_from_open_nodes(H1, Sit-Process, H2) :-
    get_from_heap(H1, _Priority, Sit-Process, H2).

% convenience predicate to start a_star
% and reverse the process for natural reading
a_star(Sit, Process) :-
    s0(S0),
    goal_situation(GoalSituation),
    a_star(S0, GoalSituation, Sit-Answer),
    reverse(Answer, Process).

% a_star search setup
a_star(StartSituation, GoalSituation, Answer) :-
    % Create heap of open search nodes
    heuristic_distance_to_goal(GoalSituation, StartSituation, D),
    singleton_heap(Open, D, 0-StartSituation-[]),
    % Do the search
    a_star(Open, GoalSituation, [StartSituation], Answer).

a_star(Open, GoalSituation, Closed, Answer) :-
    % Get the most promising Sit-Process pair
    get_from_open_nodes(Open, AccCost-Sit-Process, RemainingSearch),
    % If we've reached the goal, return the Answer
    (   reached_goal(GoalSituation, Sit), Answer = Sit-Process
    % Otherwise (or searching for other solutions), find the
    % reachable situations via some additional action A that is
    % recorded onto the process
    ;   setof(S-[A|Process], (poss(A, Sit), result(Sit, A, S)), AS_Pairs),
        % Exclude visited nodes
        pairs_keys(AS_Pairs, Children),
        ord_union(Closed, Children, Closed1, Sits),
        % Add new open nodes (with tag-along processes) to search heap
        open_add_pairs(AccCost, RemainingSearch, Sits, AS_Pairs, GoalSituation, Open1),
        % Carry on searching
        a_star(Open1, GoalSituation, Closed1, Answer)
    ).
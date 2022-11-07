from .game_agent import GameAgent
from random import shuffle
from rush_logic import Player

class AlphaBetaAgent(GameAgent):

    def __init__(self, problem, max_depth):
        super().__init__(problem)
        self.max_depth = max_depth

    def plan(self, current_state):
        return self.alpha_beta_search(current_state, current_depth=0)

    def alpha_beta_search(self, current_state, current_depth):
        #player = self.problem.get
        value, move = self.max_value(current_state, float('-inf'), float('inf'), current_depth)
        return move

    def max_value(self, state, alpha, beta, current_depth):
        if current_depth == self.max_depth or self.problem.is_goal_state(state):
            eval = self.problem.eval(state)
            return eval, ""
        v = float("-inf")
        possible_action = self.problem.get_applicable_actions(state)[0]
        actions = list(possible_action.values()) if type(possible_action) == dict else possible_action
        for action in actions:
            v2, a2 = self.min_value(self.problem.perform_action(state, action), alpha, beta, current_depth + 1)
            if v2 > v:
                v, move = v2, action
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    def min_value(self, state, alpha, beta, current_depth):
        if self.problem.is_goal_state(state):
            eval = self.problem.eval(state)
            return eval, ""
        v = float("inf")
        possible_action = self.problem.get_applicable_actions(state)[0]
        actions = list(possible_action.values()) if type(possible_action) == dict else possible_action
        for action in actions:
            v2, a2 = self.max_value(self.problem.perform_action(state, action), alpha, beta, current_depth + 1)
            if v2 < v:
                v, move = v2, action
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move
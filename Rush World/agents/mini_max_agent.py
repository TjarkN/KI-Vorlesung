from .game_agent import GameAgent
from random import shuffle
from rush_logic import Player



#
# Lösung von Christian
#

class MiniMaxGameAgent(GameAgent):

    def __init__(self, problem, max_depth):
        super().__init__(problem)
        self.max_depth = max_depth

    def plan(self, current_state):
        return self.__minimax(current_state, current_depth=0)[1]

    def __minimax(self, state, current_depth):

        if current_depth == self.max_depth or self.problem.is_goal_state(state):
            eval = self.problem.eval(state)
            return eval, ""

        possible_action = self.problem.get_applicable_actions(state)[0]
        actions = list(possible_action.values()) if type(possible_action) == dict else possible_action

        is_max_turn = True if state.get_player() == Player.player1 else False

        shuffle(actions)  # randomness
        best_value = float('-inf') if is_max_turn else float('inf')
        action_target = ""
        for action in actions:
            new_state = self.problem.perform_action(state, action)

            eval_child, _ = self.__minimax(new_state, current_depth + 1)

            if is_max_turn and best_value < eval_child:
                best_value = eval_child
                action_target = action

            elif (not is_max_turn) and best_value > eval_child:
                best_value = eval_child
                action_target = action

        return best_value, action_target

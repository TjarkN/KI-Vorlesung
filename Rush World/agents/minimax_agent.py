from .game_agent import GameAgent

class MinimaxAgent(GameAgent):

    def plan(self, current_state):
        action = self.minimax(current_state, True, depth=6)[1]
        return action

    def minimax(self, current_state, ismax, depth):
        if self.problem.is_goal_state(current_state) or depth == 0:
            return self.problem.eval(current_state), None
        possible_action = self.problem.get_applicable_actions(current_state)[0]
        actions = list(possible_action.values()) if type(possible_action) == dict else possible_action
        temp_eval = None
        temp_action = None
        for a in actions:
            new_s = self.problem.perform_action(current_state, a)
            eval, _ = self.minimax(new_s, not ismax, depth-1)
            if temp_eval is None:
                temp_eval = eval
                temp_action = a
            elif ismax and eval > temp_eval:
                temp_eval = eval
                temp_action = a
            elif not ismax and eval < temp_eval:
                temp_eval = eval
                temp_action = a
        return temp_eval, temp_action

    def expectminimax(self, current_state, player, depth):
        if self.problem.is_goal_state(current_state) or depth == 0:
            return self.problem.eval(current_state), None
        possible_action = self.problem.get_applicable_actions(current_state)[0]
        actions = list(possible_action.values()) if type(possible_action) == dict else possible_action
        temp_eval = None
        temp_action = None
        for a in actions:
            new_s = self.problem.perform_action(current_state, a)
            eval, _ = self.minimax(new_s, player, depth - 1)
            if temp_eval is None:
                temp_eval = eval
                temp_action = a
            elif player == "max" and eval > temp_eval:
                temp_eval = eval
                temp_action = a
            elif not player == "min" and eval < temp_eval:
                temp_eval = eval
                temp_action = a
        return temp_eval, temp_action


        """if ismax:
            a = new_states[max(new_states.keys())]
        else:
            a = new_states[min(new_states.keys())]
        new_state = self.problem.perform_action(a)
        minimax(new_state, not ismax)"""



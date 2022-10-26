from .agent import Agent

class AStarAgent(Agent):

    def plan(self, current_state):
        return self.a_star(current_state)

    def a_star(self, current_state):
        eval = self.problem.eval(current_state)
        frontier = [([current_state], [], eval)]
        visited_states = [current_state.to_state()]

        while len(frontier) > 0:
            frontier.sort(key=lambda x: x[2])
            current_node = frontier.pop(0)
            current_state = current_node[0][-1]
            if self.problem.is_goal_state(current_state):
                return current_node[1]

            for action in self.problem.get_applicable_actions(current_state):
                new_state = self.problem.perform_action(state=current_state, action=action)
                if new_state.to_state() not in visited_states:
                    visited_states.append(new_state.to_state())
                    actions = current_node[1][:]
                    actions.append(action)
                    states = current_node[0][:]
                    states.append(new_state)
                    costs = 0
                    for i in range(len(actions) - 1):
                        costs += self.problem.action_cost(states[i], actions[i], states[i + 1])
                    eval = self.problem.eval(new_state)
                    costs += eval  # add the eval for this state to the true costs
                    frontier.append((states, actions, costs))

    #def a_star(self, current_state, actions= []):
        """
        Heuristik: Anzahl der dreckigen Felder*2 außer der Roboter steht auf dem einzigen dreckigen Feld
        :param current_state:
        :return:
        """
    """    frontier = [(current_state, actions)]
        self.visited_states.append(current_state.to_state())
        current_node = frontier.pop(0)
        current_state = current_node[0]
        if self.problem.is_goal_state(current_state):
            return current_node[1]
        for action in self.problem.get_applicable_actions(current_state):
            new_state = self.problem.perform_action(current_state, action)
            a = new_state.to_state()
            if new_state.to_state() not in self.visited_states:
                actions = current_node[1][:]
                actions.append(action)
                plan = self.a_star(new_state, actions)
                if plan is not None:
                    return plan"""
from .agent import Agent

class DFSAgent(Agent):


    def __init__(self, problem):
        super().__init__(problem)
        self.visited_states = []

    def plan(self, current_state):
        return self.dfs(current_state)

    def dfs(self, current_state, actions= []):
        frontier = [(current_state, actions)]
        self.visited_states.append(current_state.to_state())
        current_node = frontier.pop(0)
        current_state = current_node[0]
        if self.problem.is_goal_state(current_state):
            return current_node[1]
        for action in self.problem.get_applicable_actions(current_state):
            new_state = self.problem.perform_action(current_state, action)
            a = new_state.to_state()
            if new_state.to_state() not in self.visited_states: #
                actions = current_node[1][:]
                actions.append(action)
                plan = self.dfs(new_state, actions)
                if plan is not None:
                    return plan

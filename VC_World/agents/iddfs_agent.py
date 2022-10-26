from .agent import Agent

class IDDFSAgent(Agent):

    def __init__(self, problem):
        super().__init__(problem)
        self.visited_states = []


    def plan(self, current_state):
        return self.iddfs(current_state)

    def iddfs(self, current_state):
        true_limit = 1500
        for limit in range(true_limit):
            plan = self.dls(current_state, limit)
            print(limit)
            if plan is not None:
                return plan
            else:
                self.visited_states = []

    def dls(self, current_state, limit, actions = []):
        frontier= [(current_state, actions)]
        self.visited_states.append(current_state.to_state())
        current_node = frontier.pop(0)
        current_state = current_node[0]
        if self.problem.is_goal_state(current_state):
            return current_node[1]
        elif limit == 0:
            return None
        for action in self.problem.get_applicable_actions(current_state):
            new_state = self.problem.perform_action(current_state, action)
            a = new_state.to_state()
            if new_state.to_state() not in self.visited_states:
                actions = current_node[1][:]
                actions.append(action)
                plan = self.dls(new_state, limit-1, actions)
                if plan is not None:
                    return plan
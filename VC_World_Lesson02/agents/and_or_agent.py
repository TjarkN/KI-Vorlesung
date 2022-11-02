from .agent import Agent

class AndOrAgent(Agent):


    def __init__(self, problem):
        super().__init__(problem)
        self.visited_states = []

    def and_or_search(self, current_state):
       return self.or_search(current_state, [])

    def or_search(self, current_state, visited_states):
        if self.problem.is_goal_state(current_state):
            return []
        if current_state.to_state() in visited_states:
            return -1
        for action in self.problem.get_applcable_actions(current_state):
            plan = self.and_search(self.problem.perform_action(current_state, action), visited_states)
            #if plan is not -1:
            #    return plan[] = {action}
        return plan

    def and_search(self, current_states, visited_states):
        for state in current_states:
            plan = self.or_search(state, visited_states)
            if plan == -1:
                return -1
        return
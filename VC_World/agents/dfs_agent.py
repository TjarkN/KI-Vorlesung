from .agent import Agent

class DFSAgent(Agent):


    def __init__(self, problem):
        super().__init__(problem)
        self.visited_states = None
        self.frontier = []
        self.planned = []
        self.reached_goal = False

    def plan(self, current_state):
        return self.dfs(current_state)

    def dfs(self, current_state):
        if self.frontier == []:
            self.frontier.append((current_state, [])) #= []
        if self.visited_states is None:
            self.visited_states = [current_state.to_state()]
        current_node = self.frontier.pop(0)
        current_state = current_node[0]
        if self.problem.is_goal_state(current_state):
            self.planned = current_node[1]
        elif self.reached_goal:
            return self.planned
        #elif self.problem.get_applicable_actions(current_state) is None:
        #    return None
        for action in self.problem.get_applicable_actions(current_state):
            new_state = self.problem.perform_action(current_state, action)
            if new_state.to_state() not in self.visited_states:
                self.visited_states.append(new_state.to_state())
                actions = current_node[1][:]
                actions.append(action)
                self.frontier.append((new_state, actions))
                self.dfs(new_state)
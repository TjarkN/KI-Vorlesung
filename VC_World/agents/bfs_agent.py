from .agent import Agent

class BFSAgent(Agent):

    def plan(self, current_state):
        return self.bfs(current_state)

    def bfs(self, current_state):
        frontier = [(current_state, [])]
        visited_states = [current_state.to_state()]
        while len(frontier) > 0:
            current_node = frontier.pop(0)
            current_state = current_node[0]
            print(current_state)
            if self.problem.is_goal_state(current_state):
                return current_node[1]
            for action in self.problem.get_applicable_actions(current_state):
                new_state = self.problem.perform_action(current_state,action)
                if new_state.to_state() not in visited_states:
                    visited_states.append(new_state.to_state())
                    actions = current_node[1][:]
                    actions.append(action)
                    frontier.append((new_state,actions))
        return []

    def bfs1(self, current_state, frontier= None, visited_states= None):
        if frontier == None:
            frontier = [(current_state, [])]
        if visited_states == None:
            visited_states = [current_state.to_state()]




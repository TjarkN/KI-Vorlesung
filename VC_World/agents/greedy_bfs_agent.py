from .agent import Agent

class GreedyBFSAgent(Agent):

    def __init__(self, problem, size):
        super().__init__(problem)
        self.xdim = size[0]

    def plan(self, current_state):
        return self.greedy_bfs(current_state)

    def get_heuristic(self, state):
        s = list(state.to_state())
        s_piles = s[:len(s)-2:]
        s_sum = sum(s_piles)
        if s_sum == 1:
            pos = s[len(s)-2::]
            if s[pos[0]+pos[1]*self.xdim] == 1:
                return 1
        return s_sum*2

    def greedy_choice(self, current_state):
        heuristics = []
        states = []
        actions = self.problem.get_applicable_actions(current_state)
        for action in actions:
            states.append(self.problem.perform_action(current_state, action))
        for i in states:
            heuristics.append(self.get_heuristic(i))
        minpos = heuristics.index(min(heuristics))
        return states[minpos], actions[minpos]


    def greedy_bfs(self, current_state):
        """
        Heuristik: Anzahl der dreckigen Felder*2 außer der Roboter steht auf dem einzigen dreckigen Feld
        :param current_state:
        :return:
        """
        frontier = [(current_state, [])]
        visited_states = [current_state.to_state()]
        while len(frontier) > 0:
            current_node = frontier.pop(0)
            current_state = current_node[0]
            if self.problem.is_goal_state(current_state):
                return current_node[1]
            new_state, action = self.greedy_choice(current_state)
            if new_state.to_state() not in visited_states:
                visited_states.append(new_state.to_state())
                actions = current_node[1][:]
                actions.append(action)
                frontier.append((new_state, actions))
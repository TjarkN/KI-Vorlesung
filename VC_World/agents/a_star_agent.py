from .agent import Agent

class AStarAgent(Agent):

    def __init__(self, problem, size):
        super().__init__(problem)
        self.xdim = size[0]

    def plan(self, current_state):
        return self.a_star(current_state)

    def get_heuristic(self, state):
        s = list(state.to_state())
        s_piles = s[:len(s)-2:]
        s_sum = sum(s_piles)
        if s_sum == 1:
            pos = s[len(s)-2::]
            if s[pos[0]+pos[1]*self.xdim] == 1:
                return 1
        return s_sum*2

    def a_star_choice(self, current_state):
        pass


    def a_star(self, current_state):
        """
        Heuristik: Anzahl der dreckigen Felder*2 außer der Roboter steht auf dem einzigen dreckigen Feld
        :param current_state:
        :return:
        """
        pass
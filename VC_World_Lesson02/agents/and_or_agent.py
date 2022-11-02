from .agent import Agent

class DFSAgent(Agent):


    def __init__(self, problem):
        super().__init__(problem)
        self.visited_states = []

    def and_or_search(self, current_state, actions= []):
       return self.or_search(current_state, [])

    def or_search(self, current_state, path):
        pass

    def and_search(self, states, path):

        for s in states:
            plan = []
        pass
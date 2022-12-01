"""
Perform random possible actions and tries to map/predict the state variables based on the observations
"""
from agents.agent import Agent
from agents.particle_filter import particle_filtering
import random


class SLAMAgent(Agent):

    def __init__(self, problem, dbn, amount_of_samples=1000):
        self.dbn = dbn
        self.samples = []
        self.belief_state = {}
        self.t = 0
        self.amount_of_samples = amount_of_samples
        super().__init__(problem)

    def map(self, evidences):
        self.samples = particle_filtering(evidences, self.amount_of_samples, self.dbn, self.samples)
        #Todo: Hier einen Beliefstate auf Basis der samples als dict von dicts aufbauen {state variable:{value:probability}}
        self.belief_state = {}
        for sample in self.samples:
            pass

    def plan(self, current_state):
        evidences = self.problem.observe()
        self.map(evidences)
        action = random.choice(self.problem.get_applicable_actions(current_state))
        self.t += 1
        return [action]

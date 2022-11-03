from agents.game_agent import GameAgent
from random import choice


class RandomGameAgent(GameAgent):

    def act(self):
        actions = self.problem.get_applicable_actions(self.problem)[0]
        return actions[choice(list(actions))]


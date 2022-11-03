class Problem:

    def is_goal_state(self, state):
        pass

    def get_applicable_actions(self, state):
        actions = []
        return actions

    def perform_action(self, state, action):
        new_state = None
        return new_state

    def action_cost(self, state, action, new_state):
        costs = 0
        return costs

    def get_current_state(self):
        return self

    def update_belief_state(self, state):
        bs = [[]]
        return bs

    def to_state(self):
        pass

    def copy(self):
        pass

    # heuristic function
    def eval(self, state):
        pass

    def get_all_actions(self):
        actions = []
        return actions

    def get_all_states(self):
        states = []
        return states

    def get_reward(self, state):
        r = 0
        return r

import random
from copy import deepcopy
from grid_pomdp import pomdp_value_iteration
import numpy as np


class BeliefState:
    def __init__(self, state_probs, state_probs_without_norm=None, reward=0.0):
        self.state_probs = state_probs  # b(s)
        self.state_probs_without_norm = state_probs_without_norm  # P(e|a,b)
        self.reward = reward  # rho(b)

class DynamicDecisionNetwork:

    def __init__(self, pomdp, max_depth=3):
        self.pomdp = pomdp
        self.curr_belief_state = self.calculate_initial_belief_state()
        self.max_depth = max_depth
        print("BeliefState: " + str(self.curr_belief_state.state_probs))

    def move_to_goal(self):
        actions = []
        rewards = []
        perceptions = []
        while True:
            action = self.get_best_action()
            actions.append(action)
            print("Action: " + str(action))
            is_terminal, reward, perception = self.act(action)
            print("Perception: " + str(perception))
            rewards.append(reward)
            perceptions.append(perception)
            if is_terminal:
                return actions, rewards, perceptions
            self.curr_belief_state = self.update_belief_state(self.curr_belief_state, perception, action, reward,
                                                              act=True)
            print("BeliefState: " + str(self.curr_belief_state.state_probs))

    def update_belief_state(self, belief_state, perception, action, reward=None, act=False):
        # your code
        new_belief_state = self.calculate_empty_belief_state(belief_state)
        new_belief_state.reward = belief_state.reward
        for state in new_belief_state.state_probs.keys():
            sum_s = 0
            for s in self.pomdp.states:
                transition_probs = self.pomdp.transitions[s][action]
                transition_prob = 0
                for transition in transition_probs:
                    if transition[1] == state:
                        transition_prob += transition[0]
                sum_s += transition_prob * belief_state.state_probs[s]
            new_belief_state.state_probs[state] = self.pomdp.evidences[state][perception][0] * sum_s

        new_belief_state.state_probs_without_norm = new_belief_state.state_probs

        prob_sum = sum(new_belief_state.state_probs.values())

        try:
            for state in new_belief_state.state_probs.keys():
                new_belief_state.state_probs[state] /= prob_sum
        except ZeroDivisionError:
            for state in new_belief_state.state_probs.keys():
                new_belief_state.state_probs[state] = 0
        # Filter algorithm
        # P(X_t+1|e_1:t+1) =
        #   \alpha* (norm result to Sum(prob) = 1
        #   P(e_t+1|X_t+1) (from sensor model)
        #   Sum_x_t(P(X_t+1|x_t)* (from transition model)
        #           P(x_t|e1:t) (recursion step, the old belief_state)
        # Update States based on transitions
        # self.pomdp.terminals (terminal states)
        # self.pomdp.T(s, action) (Transition model)

        # Update States based on perceptions (evidence)
        # self.pomdp.evidences[s] (sensor model)
        # self.pomdp.rewards[s]  (reward function)

        # norm beliefstate properties

        # calculate reward as expected average if not given

        return new_belief_state

    def calculate_empty_belief_state(self, belief_state):
        state_probs = {}
        for s in self.pomdp.states:
            if (s in self.pomdp.terminals):
                state_probs[s] = belief_state.state_probs[s]  # nur bei den Terminal States W'keit beibehalten
            else:
                state_probs[s] = 0.0
        bs = BeliefState(state_probs, belief_state.reward)
        return bs

    def calculate_initial_belief_state(self):
        state_probs = {}
        state_probs_without_norm = {}
        number_none_terminal_states = (len(self.pomdp.states) - len(self.pomdp.terminals))
        reward = 0
        for s in self.pomdp.states:
            if (s in self.pomdp.terminals):
                state_probs[s] = 0.0
            else:
                state_probs[s] = 1 / number_none_terminal_states
                state_probs_without_norm[s] = 1 / number_none_terminal_states
            reward = self.pomdp.rewards[self.pomdp.current_state]
            # reward+= self.pomdp.rewards[s] * state_probs[s]
        bs = BeliefState(state_probs, state_probs_without_norm, reward)
        return bs

    def get_best_action(self):
        # calculates the best action using forward projection in the belief space
        u, action = self.__max_expected_utilty(0, self.curr_belief_state)
        return action

    def estimate_utilty(self, belief_state):
        # Sum (probability of each terminal state * reward)
        estimte_u = 0
        # your code
        for s in belief_state.state_probs.keys():
            if s in self.pomdp.terminals:
                estimte_u += belief_state.state_probs[s] * self.pomdp.rewards[s]
        return estimte_u, None

    def __max_expected_utilty(self, current_depth, belief_state):

        if self.is_terminal(belief_state) or current_depth == self.max_depth:
            u_approx, _ = self.estimate_utilty(belief_state)
            return u_approx, None

        actions = self.pomdp.actlist
        evidence = list(self.get_evidence(belief_state))

        random.shuffle(actions)
        random.shuffle(evidence)
        best_value = float("-inf")
        action_target = None

        for action in actions:
            # a. calculate next belief state b'(s') based on a, e and b(s)
            # evidence = wallsensor
            current_utility = 0
            prob_b_new = 0
            for e in evidence:
                # a. update belief state and get new belief state
                next_belief_state = self.update_belief_state(belief_state, e, action)
                # b. start recursion for the next belief state
                utility, _ = self.__max_expected_utilty(current_depth + 1, next_belief_state)
                for s in next_belief_state.state_probs_without_norm:
                    prob_b_new += next_belief_state.state_probs_without_norm[s]  # sum s' (p(e|a,b))
                sum_s = 0
                for old_state, prob in belief_state.state_probs.items():  # probs = b(s)
                    sum_s_new = 0
                    transition = self.pomdp.transitions[old_state][action]  # [(0.8, (1, 1)), (0.1, (0, 1)), (0.1, (0, 1))] ... (prob, state) pairs
                    transition = {val: key for key, val in transition}
                    for vector_to_new_state, prob_to_new_state in transition.items():  # for new_state in next_belief_state.state_probs.keys():
                        new_state = self.new_state_possible(old_state, vector_to_new_state)
                        sum_s_new += prob_to_new_state * self.pomdp.rewards[new_state]  # P(s'|s,a)R(s,a,s')
                    sum_s += prob * sum_s_new
                # gamma * U(b')
                # für aktuelle action
                current_utility += prob_b_new * (sum_s + self.pomdp.gamma * utility)

                # max(sum_b'(sum_e(prob_b_news)*(sum_s(b)*sum_s'(transition*reward))+gamma u(s')))

            if current_utility > best_value:
                best_value = current_utility
                action_target = action
                #print(current_utility, action_target)

        return best_value, action_target

        # c. return u(b) = max(sum(P(b'|a,b)) * [rho(b, a, b') + gamma * U (b')]
        # am ende die max funktion zum finden von krassester utility und krassester action
        #return utility, action

    def new_state_possible(self, state, vector_to_new_state):
        state = np.array(state)
        new_state = np.array(vector_to_new_state) + state
        # check for walls
        if self.pomdp.cols - 1 < new_state[0] or self.pomdp.rows - 1 < new_state[1] or np.any(new_state < 0):
            return tuple(state)

        # check for Nones
        elif tuple(new_state) not in self.pomdp.states:
            return tuple(state)
        else:
            return tuple(new_state)

    def is_terminal(self, belief_state):
        for s in belief_state.state_probs:
            if s not in self.pomdp.terminals:
                return False
        return True

    def get_actions(self, belief_state):
        actions = set({})
        for s in belief_state.state_probs:
            actions.update(self.pomdp.actions(s))
        return actions

    def get_evidence(self, belief_state):
        evidence = set({})
        for s in belief_state.state_probs:
            for e in self.pomdp.evidences[s]:
                evidence.add(e[1])
        return evidence

    def act(self, action):
        # performing a real action includes receiving perceptions and reward
        # returns if new state terminal state, reward o new state and perception of new state
        return self.pomdp.act(action)

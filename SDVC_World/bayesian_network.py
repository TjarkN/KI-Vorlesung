import random


class BayesianNode:

    def __init__(self, name, values=[True, False], parents=[]):
        self.name = name
        self.values = values
        self.parents = parents
        self.cpt = {}
        for p in parents:
            p.add_child(self)
        self.childs = []

    def add_child(self, child):
        self.childs.append(child)

    def set_ctp_values(self, value_dict):
        for key, value in value_dict.items():
            self.cpt[key] = value

    def get_probability(self, value, conditions):
        """
        Return the ctp value given both variables and condition as tuples with name and value
        :param value: value of the variable of the current node
        :param conditions: parents an values of parents
        :return: ctp(variable|conditions)
        """
        key = []
        for pv in conditions:
            if pv[0] in self.parents:
                key.append(f"{pv[0].name}_{pv[1]}")

        complete_key = [f"{self.name}_{value}"]
        if len(key) > 0:
            complete_key = complete_key+key
        complete_key = tuple(complete_key)
        return self.cpt[complete_key]

    def get_sample(self, parents_values):
        rand_number = random.random()
        value_sum = 0
        for v in self.values:
            value_sum += self.get_probability(v, parents_values)
            if value_sum >= rand_number:
                return v


class BayesianNetwork:

    def __init__(self, start_nodes):
        self.start_nodes = start_nodes


class DynamicBayesianNetwork(BayesianNetwork):

    def __init__(self, priors, state_variables, evidence_variables):
        self.state_variables = state_variables
        self.evidence_variables = evidence_variables
        super().__init__(priors)

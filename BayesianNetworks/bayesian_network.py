import random

class BayesianNode:

    def __init__(self, name, values=[True,False], parents=[]):
        self. name = name
        self.values = values
        self.parents = parents
        self.cpt = {}
        for p in parents:
            p.add_child(self)
        self.cpt={}
        self.childs = []

    def add_child(self, child):
        self.childs.append(child)

    def set_ctp_values(self, value_dict):
        for key, value in value_dict.items():
            self.cpt[key]=value

    def get_sample(self, parents_values):
        key = []
        for pv in parents_values:
            if pv[0] in self.parents:
                key.append(pv[0].name+"_"+str(int(pv[1])))

        rand_number = random.random()
        value_sum = 0
        for v in self.values:
            complete_key=[self.name + "_" + str(int(v))]
            if len(key)>0:
                complete_key = complete_key+key
            complete_key = tuple(complete_key)

            value_sum += self.cpt[complete_key]
            if value_sum >= rand_number:
                return v


class BayesianNetwork:

    def __init__(self, start_nodes):
        self.start_nodes = start_nodes

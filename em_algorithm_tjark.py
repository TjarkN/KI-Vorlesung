import numpy as np
import itertools
from gibbs_sampling import ask
from functools import reduce
import operator
from bayesian_network import DynamicBayesianNetwork


def prod(iterable):
    return reduce(operator.mul, iterable, 1)


def init_child(parent):
    for child in parent.childs:
        for value in parent.values:
            y = np.random.uniform()
            child.cpt[(child.name + '_' + child.values[0], parent.name + '_' + str(value))] = y
            child.cpt[(child.name + '_' + child.values[1], parent.name + '_' + str(value))] = 1 - y
        init_child(child)


def initialize_parameter_values(dbn: DynamicBayesianNetwork):
    # vorhandene Werte löschen und zufällig initialieren
    # alle möglichen Elternkombinationen durchgehen und iwie so initialisieren, dass man zeilenweise auf 1 kommt
    for start_node in dbn.start_nodes:
        assert len(start_node.values) == 2
        x = np.random.uniform()
        start_node.cpt[(start_node.name + '_' + str(start_node.values[0]),)] = x
        start_node.cpt[(start_node.name + '_' + str(start_node.values[1]),)] = 1 - x
        init_child(start_node)


def estimate_parameter_values(dbn, data, amount_of_samples):
    likelihood_old = -np.inf
    likelihood_new = calc_likelihood(dbn, data, amount_of_samples)
    while likelihood_new > likelihood_old:
        nodes_to_visit = [node for node in dbn.start_nodes]
        while len(nodes_to_visit) > 0:
            current_node = nodes_to_visit.pop()

            for value_current_node in current_node.values:
                if len(current_node.parents) > 0:
                    for parent in current_node.parents:
                        for parent_value in parent.values:
                            sum = 0
                            for d in data:
                                if (current_node.name, str(value_current_node)) in d:
                                    sum += current_node.cpt[(current_node.name + '_' + str(value_current_node),
                                                             parent.name + '_' + str(parent_value))] / len(data)
                            # sum *= parent.cpt[(parent.name+'_'+str(parent_value), )]
                            current_node.cpt[(current_node.name + '_' + str(value_current_node),
                                              parent.name + '_' + str(parent_value))] = sum
                else:
                    # theta(1)
                    sum = 0
                    bag_name = current_node.name + '_' + str(current_node.values[0])
                    other_bag_name = current_node.name + '_' + str(current_node.values[1])
                    for j in range(len(data)):
                        zaehler = current_node.cpt[(bag_name,)]
                        for i in range(len(current_node.childs)):
                            zaehler *= current_node.childs[i].cpt[(data[j][i][0] + '_' + data[j][i][1], bag_name)]
                        nenner = current_node.cpt[(other_bag_name,)]
                        for i in range(len(current_node.childs)):
                            nenner *= current_node.childs[i].cpt[(data[j][i][0] + '_' + data[j][i][1], other_bag_name)]
                        nenner += zaehler
                        sum += zaehler / nenner

                    sum /= len(data)
                    current_node.cpt[(bag_name,)] = sum
                    current_node.cpt[(other_bag_name,)] = 1 - sum
            nodes_to_visit += [child for child in current_node.childs]
        likelihood_old = likelihood_new
        likelihood_new = calc_likelihood(dbn, data, amount_of_samples)


def calc_likelihood(dbn, data, amount_of_samples):
    probs = np.zeros(len(data))
    for i, d in enumerate(data):
        probs[i] = ask(d, [], amount_of_samples, dbn)  # gibbs sampling
    likelihood = np.sum(np.log10(probs))
    return likelihood

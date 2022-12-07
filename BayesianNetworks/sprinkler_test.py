from bayesian_network import BayesianNetwork, BayesianNode
from prior_sampling import prior_sample
#from rejection_sampling import rejection_sample

cloudy = BayesianNode("Cloudy")
cloudy.set_ctp_values({(cloudy.name+"_1",):0.5,
                       (cloudy.name+"_0",):0.5})
sprinkler = BayesianNode("Sprinkler", parents=[cloudy])
sprinkler.set_ctp_values({(sprinkler.name+"_1",cloudy.name+"_1"):0.1,
                          (sprinkler.name+"_1",cloudy.name+"_0"):0.5,
                          (sprinkler.name+"_0",cloudy.name+"_1"):0.9,
                          (sprinkler.name+"_0",cloudy.name+"_0"):0.5})
rain= BayesianNode("Rain", parents=[cloudy])
rain.set_ctp_values({(rain.name+"_1",cloudy.name+"_1"):0.8,
                     (rain.name+"_1",cloudy.name+"_0"):0.2,
                     (rain.name+"_0",cloudy.name+"_1"):0.2,
                     (rain.name+"_0",cloudy.name+"_0"):0.8})

wet_grass= BayesianNode("WetGrass", parents=[sprinkler, rain])
wet_grass.set_ctp_values({(wet_grass.name+"_1", sprinkler.name+"_1", rain.name+"_1"): 0.99,
                          (wet_grass.name+"_1", sprinkler.name+"_1", rain.name+"_0"): 0.9,
                          (wet_grass.name+"_1", sprinkler.name+"_0", rain.name+"_1"): 0.9,
                          (wet_grass.name+"_1", sprinkler.name+"_0", rain.name+"_0"): 0.0,
                          (wet_grass.name+"_0", sprinkler.name+"_1", rain.name+"_1"): 0.01,
                          (wet_grass.name+"_0", sprinkler.name+"_1", rain.name+"_0"): 0.1,
                          (wet_grass.name+"_0", sprinkler.name+"_0", rain.name+"_1"): 0.1,
                          (wet_grass.name+"_0", sprinkler.name+"_0", rain.name+"_0"): 1.0})

bn = BayesianNetwork([cloudy])
p = prior_sample((rain, True), 10000, bn)
print(p)
#p = rejection_sample((wet_grass, True),[(sprinkler, False),(cloudy, True)], 10000, bn)
#print(p)

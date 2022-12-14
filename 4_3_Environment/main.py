from ddn import DynamicDecisionNetwork
from grid_pomdp import pomdp_value_iteration, GridPOMDP

r = -0.4
env = GridPOMDP([
                [-1,r,r,r,-1],
                 [None,None,1,None,None],],
              terminals=[(0, 1), (4, 1), (2,0)], init=(1,1))

ddn = DynamicDecisionNetwork(env)
print(ddn)
ddn.move_to_goal()

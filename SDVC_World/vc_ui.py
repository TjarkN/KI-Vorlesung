import pgzrun
from vc_logic import Building, VCBS
from random import choice, seed
from bayesian_network import DynamicBayesianNetwork, BayesianNode
from agents.slam_agent import SLAMAgent
import itertools
import time

# create game environment
seed_value = None
if seed_value is not None:
    seed(seed_value)
size = (3, 3)
dirt_rate = 0.6
building = Building(size, dirt_rate, seed=seed_value)

vc = VCBS(choice([[x, y] for x in range(size[0]) for y in range(size[1])]), building, random_action_rate=0,
          dirt_changing_rate=0.999999, walls_perception_accuracy=0.99, dirt_perception_accuracy=0.99)

priors = []
state_variables = []
evidence_variables = []

location_values = []
for x in range(building.rooms.shape[0]):
    for y in range(building.rooms.shape[1]):
        location_values.append((x, y))

"""p=uniform distributed """
location_0 = BayesianNode("Location_0", location_values)
location_0_ctp = {}
for v in location_values:
    location_0_ctp[(f"{location_0.name}_{v}",)] = 1/len(location_values)
location_0.set_ctp_values(location_0_ctp)
priors.append(location_0)

"""p=1/available actions is reachable, else 0"""
location_1 = BayesianNode("Location_1", location_values, parents=[location_0])
location_1_ctp = {}
for v0 in location_values:
    for v1 in location_values:
        v = 0
        if vc.building.adjacent(v0, v1):
            v = 1/len(vc.get_applicable_actions_by_position([vc], [v0]))
        location_1_ctp[(f"{location_1.name}_{v1}", f"{location_0.name}_{v0}")] = v
location_1.set_ctp_values(location_1_ctp)
state_variables.append(location_1)

wall_sensor_values = []
for v1 in [True, False]:
    for v2 in [True, False]:
        for v3 in [True, False]:
            for v4 in [True, False]:
                wall_sensor_values.append((v1, v2, v3, v4))

"""p=0.8 * matching walls * 0,2 * not matching walls"""
wall_sensor_1 = BayesianNode("WallSensor_1", wall_sensor_values, parents=[location_1])
wall_sensor_1_ctp = {}
for vs in wall_sensor_values:
    for vl in location_values:
        walls = vc.observe_walls_with_prob(1, vl)
        matches = [x == y for (x, y) in zip(walls, vs)]
        v = vc.walls_perception_accuracy ** sum(matches) * (1 - vc.walls_perception_accuracy) ** (len(matches) - sum(matches))
        wall_sensor_1_ctp[(f"{wall_sensor_1.name}_{vs}", f"{location_1.name}_{vl}")] = v
wall_sensor_1.set_ctp_values(wall_sensor_1_ctp)
evidence_variables.append(wall_sensor_1)

dirts_1 = []
for x in range(building.rooms.shape[0]):
    for y in range(building.rooms.shape[1]):
        dirt_0 = BayesianNode(f"Dirt_{x}_{y}_0")
        dirt_0.set_ctp_values({(f"{dirt_0.name}_False",): 1-dirt_rate,
                               (f"{dirt_0.name}_True",): dirt_rate})
        priors.append(dirt_0)
        dirt_1 = BayesianNode(f"Dirt_{x}_{y}_1", parents=[dirt_0])
        dirt_1.set_ctp_values({(f"{dirt_1.name}_False", f"{dirt_0.name}_False"): vc.dirt_changing_rate,
                               (f"{dirt_1.name}_False", f"{dirt_0.name}_True"): 1 - vc.dirt_changing_rate,
                               (f"{dirt_1.name}_True", f"{dirt_0.name}_False"): 1-vc.dirt_changing_rate,
                               (f"{dirt_1.name}_True", f"{dirt_0.name}_True"): vc.dirt_changing_rate})
        dirts_1.append(dirt_1)
        state_variables.append(dirt_1)

dirt_sensor_1 = BayesianNode(f"DirtSensor_1", parents=dirts_1+[location_1])
dirt_sensor_1_ctp = {}
value_combinations = list(itertools.product([False, True], repeat=len(dirts_1)))
for sv in [False, True]:
    key = [f"{dirt_sensor_1.name}_{sv}"]
    for values in value_combinations:
        key_dirt = []
        for i, value in enumerate(values):
            key_dirt.append(f"{dirts_1[i].name}_{value}")
        for j, l_loc in enumerate(location_values):
            key_loc = [f"{location_1.name}_{l_loc}"]
            v = 0
            if values[j] == sv:
                v = 0.9
            else:
                v = 0.1
            dirt_sensor_1_ctp[tuple(key+key_loc+key_dirt)] = v
dirt_sensor_1.set_ctp_values(dirt_sensor_1_ctp)
evidence_variables.append(dirt_sensor_1)

dbn = DynamicBayesianNetwork(priors, state_variables, evidence_variables)

amount_of_samples = 10000
agent = SLAMAgent(vc, dbn, amount_of_samples)

ai_active = True

# GUI
width_room = 274
height_room = 240

TITLE = "Vacuum-cleaner world"
WIDTH = size[0]*width_room
HEIGHT = size[1]*height_room

vc_gui = Actor("vc.png")

dirt = {}
for x in range(building.rooms.shape[0]):
    for y in range(building.rooms.shape[1]):
        pos = (x, y)
        dirt[pos] = Actor("dirt.png")
        dirt[pos].x = pos[0] * width_room + dirt[pos].width/2
        dirt[pos].y = pos[1] * height_room + 1.5*dirt[pos].height


pause = False
action = None


def draw():
    screen.clear()
    screen.fill("white")
    # draw rooms
    for x in range(size[0]):
        screen.draw.line((x * width_room, 0), (x * width_room, HEIGHT), "black")
    for y in range(size[1]):
        screen.draw.line((0, y * height_room), (WIDTH, y * height_room), "black")
    #draw beliefstate
    if len(agent.belief_state) > 0:
        for prior in agent.dbn.start_nodes:
            if prior.name == "Location_0":
                for pos, prob in agent.belief_state[prior].items():
                    textpos = ((pos[0] * width_room) + 5, (pos[1] * height_room) + 5)
                    screen.draw.text(f"Agent:{prob}", textpos, color="black", fontsize=20, alpha=prob)
            else:
                prob = agent.belief_state[prior][True]
                pos = (int(prior.name[5:6]), int(prior.name[7:8]))
                textpos = ((pos[0] * width_room) + 5, (pos[1] * height_room) + 25)
                screen.draw.text(f"Dirt:{prob}", textpos, color="black", fontsize=20, alpha=prob)

    # draw agent
    vc_gui.x = vc.position[0] * width_room + vc_gui.width / 2
    vc_gui.y = vc.position[1] * height_room + vc_gui.height / 2
    vc_gui.draw()
    # draw dirt
    for x in range(building.rooms.shape[0]):
        for y in range(building.rooms.shape[1]):
            position = (x, y)
            if not building.rooms[position]:
                dirt[position].draw()

    if building.dirty_rooms == 0:
        winning_text = f"You won and spent {vc.energy_spend} energy!"
        screen.draw.text(winning_text, (50, 30), color="black", fontsize=40)


def update():
    global action
    global pause
    if action is None and building.dirty_rooms > 0 and ai_active:
        vc.update_dirt()
        print(vc.observe_walls())
        print(vc.observe_dirt())
        action = agent.act()
    elif action is not None and not pause:
            vc.act(action)
            action = None
            time.sleep(0.5)


def on_key_down(key):
    global pause
    if building.dirty_rooms > 0:
        vc.update_dirt()
        if key == keys.LEFT:
            vc.act("left")
        elif key == keys.RIGHT:
            vc.act("right")
        elif key == keys.UP:
            vc.act("up")
        elif key == keys.DOWN:
            vc.act("down")
        elif key == keys.SPACE:
            vc.act("clean")
        elif key == keys.P:
            pause = not pause

        #print(vc.observe_walls())
        #print(vc.observe_dirt())


pgzrun.go()

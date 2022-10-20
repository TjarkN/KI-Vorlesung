#pip install pgzero
import pgzrun
from vc_logic import Building, VC, VCBS
from random import choice, seed
#from agents.prob_dfs_agent import ProbDFSAgent
#from agents.and_or_agent import AndOrAgent
#from agents.dfs_agent import DFSAgent
from agents.bfs_agent import BFSAgent
#from agents.iddfs_agent import IDDFSAgent

import time

#create game environment
seed_value = None
if seed_value is not None:
    seed(seed_value)
size = (2, 3)
dirt_rate = 0.6
building = Building(size, dirt_rate, seed=seed_value)
vc = VC(choice([[x, y] for x in range(size[0]) for y in range(size[1])]), building, random_action_rate=0)
#vc =VCBS(choice([[x,y] for x in range(size[0]) for y in range(size[1])]), building, random_action_rate= 0, perception=True)
#agent = DFSAgent(vc)
#agent = IDDFSAgent(vc)
#agent = GreedyBFSAgent(vc)
#agent = AStarAgent(vc)
agent = BFSAgent(vc)
#agent = ProbDFSAgent(vc)
#agent = AndOrAgent(vc)
ai_active = True

#GUI
width_room = 274
height_room = 240

TITLE = "Vacuum-cleaner world"
WIDTH = size[0]*width_room
HEIGHT = size[1]*height_room

vc_gui = Actor("vc.png")

dirt = {}
for x in range(building.rooms.shape[0]):
    for y in range(building.rooms.shape[1]):
        pos = (x,y)
        dirt[pos] = Actor("dirt.png")
        dirt[pos].x = pos[0] * width_room + dirt[pos].width/2
        dirt[pos].y = pos[1] * height_room + 1.5*dirt[pos].height


def draw():
    screen.clear()
    screen.fill("white")
    # draw rooms
    for x in range(size[0]):
        screen.draw.line((x * width_room, 0), (x * width_room, HEIGHT), "black")
    for y in range(size[1]):
        screen.draw.line((0, y * height_room), (WIDTH, y * height_room),"black")
    # draw agent
    vc_gui.x = vc.position[0] * width_room + vc_gui.width / 2
    vc_gui.y = vc.position[1] * height_room + vc_gui.height / 2
    vc_gui.draw()
    # draw dirt
    for x in range(building.rooms.shape[0]):
        for y in range(building.rooms.shape[1]):
            pos = (x, y)
            if not building.rooms[pos]:
                dirt[pos].draw()

    if building.dirty_rooms == 0:
        winning_text = f"You won and spent {vc.energy_spend} energy!"
        screen.draw.text(winning_text, (50, 30), color="black", fontsize=40)


def update():
    if building.dirty_rooms > 0 and ai_active:
        action = agent.act()
        if action is not None:
            vc.act(action)
            time.sleep(0.5)


def on_key_down(key):
    if building.dirty_rooms > 0:
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


pgzrun.go()

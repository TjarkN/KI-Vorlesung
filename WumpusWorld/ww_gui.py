import pgzrun
from wumpus_world import WumpusWorld
from random import choice,seed
#from agents.prob_dfs_agent import ProbDFSAgent
#from agents.and_or_agent import AndOrAgent
#from agents.dfs_agent import DFSAgent
from agents.hybrid_agent import HybridAgent, KnowledgeBase, set_up_ww

import time

#create game environment
seed_value = 1000
if seed_value is not None:
    seed(seed_value)
size = (3,3)
pit_rate = 0.2
ww = WumpusWorld(*size, pit_rate)

ww_KB = set_up_ww(size)



agent = HybridAgent(ww, ww_KB, *size)
ai_active = True

#GUI
width_field = 224
height_field = 229

TITLE = "Wumpus World"
WIDTH = size[0]*width_field
HEIGHT = size[1]*width_field

player_gui = Actor("player_small.png")
wumpus_gui = Actor("wumpus.png")
wumpus_gui.x = ww.wumpus_pos[0] * width_field + wumpus_gui.width / 1.5
wumpus_gui.y = ww.wumpus_pos[1] * height_field + wumpus_gui.height / 1.5
if ww.player_direction[0] == 1 and ww.player_direction[1] == 0:
    player_gui.angle = 0
elif ww.player_direction[0] == 0 and ww.player_direction[1] == 1:
    player_gui.angle = 270
elif ww.player_direction[0] == -1 and ww.player_direction[1] == 0:
    player_gui.angle = 0
    player_gui.scale_y = -1
elif ww.player_direction[0] == 0 and ww.player_direction[1] == -1:
    player_gui.angle = 90

gold_gui = Actor("gold.png")
gold_gui.x = ww.gold_pos[0] * width_field + gold_gui.width/1.8
gold_gui.y = ww.gold_pos[1] * height_field + gold_gui.height*2


pits = {}
for pit in ww.pits_pos:
    pits[pit] = Actor("pit.png")
    pits[pit].x = pit[0] * width_field + pits[pit].width/1.5
    pits[pit].y = pit[1] * height_field + pits[pit].height/1.5

stenches ={}
for wumpus_neighbours in ww.get_neighbours(ww.wumpus_pos):
    stenches[wumpus_neighbours]=Actor("stench_small.png")
    stenches[wumpus_neighbours].x = wumpus_neighbours[0] * width_field + stenches[wumpus_neighbours].width*3.2
    stenches[wumpus_neighbours].y = wumpus_neighbours[1] * height_field + stenches[wumpus_neighbours].height/1.5

breezes ={}
for pit_position in ww.pits_pos:
    for pits_neighbours in ww.get_neighbours(pit_position):
        breezes[pits_neighbours]=Actor("breeze_small.png")
        breezes[pits_neighbours].x = pits_neighbours[0] * width_field + breezes[pits_neighbours].width*3
        breezes[pits_neighbours].y = pits_neighbours[1] * height_field + breezes[pits_neighbours].height/0.7


def draw():
    screen.clear()
    screen.fill((245,225,217))
    # draw rooms
    for x in range(size[0]):
        screen.draw.line((x * width_field, 0), (x * width_field, HEIGHT), "black")
    for y in range(size[1]):
        screen.draw.line((0, y * height_field), (WIDTH, y * height_field),"black")

    # draw wumpus
    if ww.wumpus_pos is not None:
        if ww.wumpus_pos in ww.player_perception.keys():
            wumpus_gui.draw()

    # draw pits
    for key, pit in pits.items():
        if key in ww.player_perception.keys():
            pit.draw()

    # draw stench
    for key, stench in stenches.items():
        if key not in ww.pits_pos:
            if key in ww.player_perception.keys():
                stench.draw()

    # draw breeze
    for key, breeze in breezes.items():
        if ww.wumpus_pos != key and key not in ww.pits_pos:
            if key in ww.player_perception.keys():
                breeze.draw()

    #draw gold
    if ww.gold_pos is not None:
        if ww.gold_pos in ww.player_perception.keys():
            gold_gui.draw()


    # draw agent
    if ww.player_pos is not None:
        if ww.player_direction[0] == 1 and ww.player_direction[1] == 0:
            player_gui = Actor("player_small.png")
            player_gui.angle = 0
        elif ww.player_direction[0] == 0 and ww.player_direction[1] == 1:
            player_gui = Actor("player_small.png")
            player_gui.angle = 270
        elif ww.player_direction[0] == -1 and ww.player_direction[1] == 0:
            player_gui = Actor("player_small_left.png")
            player_gui.angle = 0
        elif ww.player_direction[0] == 0 and ww.player_direction[1] == -1:
            player_gui = Actor("player_small.png")
            player_gui.angle = 90
        player_gui.x = ww.player_pos[0] * width_field + player_gui.width/1.5
        player_gui.y = ww.player_pos[1] * height_field + player_gui.height/1.5
        player_gui.draw()

    text = f""
    if ww.player_pos is None:
        text = f"You have lost with {ww.points} points!"
    elif ww.player_climbed_out:
        if ww.player_has_gold:
            text = f"You have won with {ww.points} points!"
        else:
            text = f"You have escaped with {ww.points} points!"
    screen.draw.text(text, (50, 30), color="black", fontsize=40)


def update():
    """
    if ai_active:
        action = agent.act()
        if action is not None:
            ww.act(action)
            time.sleep(0.5)
    """


def on_key_down(key):
    if ai_active and key == keys.A:
        action = agent.act()
    if key == keys.LEFT:
        ww.act("left")
    elif key == keys.RIGHT:
        ww.act("right")
    elif key == keys.UP:
        ww.act("forward")
    elif key == keys.DOWN:
        ww.act("grab")
    elif key == keys.SPACE:
        ww.act("shoot")
    elif key == keys.RETURN:
        ww.act("climb")


pgzrun.go()

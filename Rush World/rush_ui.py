# pip install pgzero
import pgzrun

from rush_logic import Environment, Player, Turns
import time
from random import choice
from agents.random_agent import RandomGameAgent
from agents.minimax_agent import MinimaxAgent
from agents.alpha_beta_agent import AlphaBetaAgent


# random_env
env = Environment(board_size=(4, 8), step_range=(1, 3), obstacle_probability=0.2)
ai_active = True

opponent = RandomGameAgent(env.rush)
#agent = MinimaxAgent(env.rush)
agent = AlphaBetaAgent(env.rush, 4)

size = env.rush.board_size
rush = env.rush
width_room = env.width_room
height_room = env.height_room

TITLE = "Rush World"
side_board = 2 * width_room
WIDTH = size[0] * width_room + side_board
HEIGHT = size[1] * height_room

obstacles = {}
rush_player1 = {}
rush_player2 = {}
for x in range(size[0]):
    for y in range(size[1]):
        pos = (x, y)
        obstacles[pos] = Actor("obstacle.png")
        obstacles[pos].x = pos[0] * width_room + width_room / 2 + side_board / 2
        obstacles[pos].y = (size[1]-1-pos[1]) * height_room + height_room / 2
        rush_player1[pos] = Actor("player1.png")
        rush_player1[pos].x = pos[0] * width_room + width_room / 2 + side_board / 2
        rush_player1[pos].y = (size[1]-1-pos[1]) * height_room + height_room / 2
        rush_player2[pos] = Actor("player2.png")
        rush_player2[pos].x = pos[0] * width_room + width_room / 2 + side_board / 2
        rush_player2[pos].y = (size[1]-1-pos[1]) * height_room + height_room / 2

# draw dices
dice_player1 = Actor("dice.png")
dice_player1.x = WIDTH - width_room / 2
dice_player1.y = HEIGHT - height_room / 2

dice_player2 = Actor("dice.png")
dice_player2.x = width_room / 2
dice_player2.y = height_room / 2

#draw skip button
skip = Actor("skip.png")
skip.x = width_room / 2
skip.y = HEIGHT / 2


def draw():
    screen.clear()
    screen.fill("white")
    # draw dices
    dice_player1.draw()
    dice_player2.draw()
    #draw skip button
    skip.draw()

    # draw squares
    for x in range(size[0] + 1):
        screen.draw.line((x * width_room + side_board / 2, 0), (x * width_room + side_board / 2, HEIGHT), "black")
    for y in range(size[1]):
        screen.draw.line((side_board / 2, y * height_room), (WIDTH - side_board / 2, y * height_room), "black")
    # draw pieces and obstacles
    for x in range(size[0]):
        for y in range(size[1]):
            pos = (x, y)
            if env.rush.field[x, y] == Player.player1:
                rush_player1[pos].draw()
            elif env.rush.field[x, y] == Player.player2:
                rush_player2[pos].draw()
            elif env.rush.field[x, y] == Player.obstacle:
                obstacles[pos].draw()

    # draw pieces in goal zone
    for p in range(rush.player1_reached_goal_zone):
        goal_player1 = Actor("player1_small.png")
        goal_player1.x = (WIDTH-side_board / 2) + (0.5 + p) * goal_player1.width
        goal_player1.y = goal_player1.height / 2
        goal_player1.draw()
    for p in range(rush.player2_reached_goal_zone):
        goal_player1 = Actor("player2_small.png")
        goal_player1.x = (0.5 + p) * goal_player1.width
        goal_player1.y = HEIGHT-goal_player1.height / 2
        goal_player1.draw()

    # draw dice results
    if rush.turn == Turns.player1_select_figure:
        screen.draw.text(str(rush.last_step_range), (WIDTH - width_room / 2, HEIGHT - 1.5 * height_room), color="black",
                         fontsize=40)
    if rush.turn == Turns.player2_select_figure:
        screen.draw.text(str(rush.last_step_range), (width_room / 2, 1.5 * height_room),
                         color="black",
                         fontsize=40)
    if env.rush.is_goal_state(env.rush) == Player.player1:
        winning_text = f"Team 1 has won!"
        screen.draw.text(winning_text, (side_board / 2, int(HEIGHT / 2)), color="black", fontsize=40)
    elif env.rush.is_goal_state(env.rush) == Player.player2:
        winning_text = f"Team 2 has won!"
        screen.draw.text(winning_text, (side_board / 2, int(HEIGHT / 2)), color="black", fontsize=40)


def update():
    if not env.rush.is_goal_state(env.rush):
        action = None
        if rush.get_player() == Player.player1 and ai_active:
            action = agent.act()
        elif rush.get_player() == Player.player2:
            action = opponent.act()
        elif rush.get_player() == Player.chance:
            action = choice(rush.get_applicable_actions(rush)[0])
        if action is not None:
            rush.act(action)
            time.sleep(0.5)


def on_mouse_up(pos, button):
    if rush.get_player() == Player.player1 and not env.rush.is_goal_state(env.rush):
        action = None
        if rush.turn == Turns.player1_select_figure:
            position = get_square(pos)
            if position is not None and rush.field[position] == Player.player1 \
                    and rush.is_move_possible(rush, position, rush.last_step_range, rush.get_player()):
                actions = rush.get_applicable_actions(rush)[0]
                action = actions[position]
            elif position == (-1, -1):  # skip
                actions = rush.get_applicable_actions(rush)[0]
                if position in actions:
                    action = actions[position]
        if rush.turn == Turns.player1_move_obstacle_to:
            position = get_square(pos)
            if position is not None and rush.field[position] == 0 and 0 < position[1] < size[1] - 1:
                actions = rush.get_applicable_actions(rush)[0]
                action = actions[position]
            elif position == (-1, -1):  # skip
                actions = rush.get_applicable_actions(rush)[0]
                if position in actions:
                    action = actions[position]
        if rush.turn == Turns.player1_select_initial_square:
            position = get_square(pos)
            if position is not None and rush.field[position] == 0 and 0 == position[1]:
                actions = rush.get_applicable_actions(rush)[0]
                action = actions[position]
        if action is not None:
            rush.act(action)


def get_square(position):
    if right_position(skip, position):
        return -1, -1
    if position[0] < side_board / 2:
        return None
    i = int((position[0] - side_board / 2) / width_room)
    j = int((HEIGHT-position[1]) / height_room)
    return i, j


def right_position(figure, position):
    if position[0] in range(int(figure.x - figure.width / 2), int(figure.x + figure.width / 2)) and \
            position[1] in range(int(figure.y - figure.height / 2), int(figure.y + figure.height / 2)):
        return True
    else:
        return False


pgzrun.go()

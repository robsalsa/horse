import os
import random
import tkinter as tk

BASE = os.path.dirname(os.path.abspath(__file__))

IDLE_DELAY = 220
WALK_DELAY = 120
WALK_SPEED = 15

IDLE_PATHS = [
    os.path.join(BASE, 'assets', 'idle', f'idle{i}.png')
    for i in range(1, 4)
]
LEFT_PATHS = [
    os.path.join(BASE, 'assets', 'walk', 'left', f'walk2left{i}.png')
    for i in range(1, 4)
]
RIGHT_PATHS = [
    os.path.join(BASE, 'assets', 'walk', 'right', f'walk2right{i}.png')
    for i in range(1, 4)
]
UP_PATHS = [
    os.path.join(BASE, 'assets', 'up-down', f'Screenshot (351){suffix}.png')
    for suffix in ('', '2', '3')
]
DOWN_PATHS = UP_PATHS

ACTION_FRAMES = {
    'idle': IDLE_PATHS,
    'walk_left': LEFT_PATHS,
    'walk_right': RIGHT_PATHS,
    'walk_up': UP_PATHS,
    'walk_down': DOWN_PATHS,
}

ACTION_DELAYS = {
    'idle': IDLE_DELAY,
    'walk_left': WALK_DELAY,
    'walk_right': WALK_DELAY,
    'walk_up': WALK_DELAY,
    'walk_down': WALK_DELAY,
}

ACTION_MOVE = {
    'idle': (0, 0),
    'walk_left': (-WALK_SPEED, 0),
    'walk_right': (WALK_SPEED, 0),
    'walk_up': (0, -WALK_SPEED),
    'walk_down': (0, WALK_SPEED),
}

ACTION_WEIGHTS = [5, 2, 2, 2, 2]
ACTIONS = list(ACTION_FRAMES.keys())

root = tk.Tk()
root.overrideredirect(True)
root.wm_attributes('-topmost', True)
root.bind_all('<KeyPress-0>', lambda event: root.destroy())
root.bind_all('<KeyPress-KP_0>', lambda event: root.destroy())

frames = {
    action: [tk.PhotoImage(file=path) for path in paths]
    for action, paths in ACTION_FRAMES.items()
}

pet_w = frames['idle'][0].width()
pet_h = frames['idle'][0].height()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
max_x = max(0, screen_w - pet_w)
max_y = max(0, screen_h - pet_h)

label = tk.Label(root, bd=0)
label.pack()

pet_x = screen_w // 2
pet_y = screen_h // 2
current_action = 'idle'
frame_index = 0
loops_left = random.randint(3, 8)


def start_action(action: str) -> None:
    global current_action, frame_index, loops_left
    current_action = action
    frame_index = 0
    loops_left = random.randint(3, 8) if action == 'idle' else random.randint(1, 4)


def choose_action() -> str:
    return random.choices(ACTIONS, weights=ACTION_WEIGHTS, k=1)[0]


def clamp_position() -> None:
    global pet_x, pet_y
    pet_x = max(0, min(max_x, pet_x))
    pet_y = max(0, min(max_y, pet_y))


def update() -> None:
    global frame_index, loops_left, pet_x, pet_y

    action_frames = frames[current_action]
    label.configure(image=action_frames[frame_index])

    dx, dy = ACTION_MOVE[current_action]
    pet_x += dx
    pet_y += dy

    if pet_x <= 0 and current_action == 'walk_left':
        pet_x = 0
        start_action('walk_right')
        action_frames = frames[current_action]
    elif pet_x >= max_x and current_action == 'walk_right':
        pet_x = max_x
        start_action('walk_left')
        action_frames = frames[current_action]

    if pet_y <= 0 and current_action == 'walk_up':
        pet_y = 0
        start_action('walk_down')
        action_frames = frames[current_action]
    elif pet_y >= max_y and current_action == 'walk_down':
        pet_y = max_y
        start_action('walk_up')
        action_frames = frames[current_action]

    clamp_position()
    root.geometry(f'{pet_w}x{pet_h}+{pet_x}+{pet_y}')

    frame_index += 1
    if frame_index >= len(action_frames):
        frame_index = 0
        loops_left -= 1
        if loops_left <= 0:
            start_action(choose_action())

    root.after(ACTION_DELAYS[current_action], update)


root.geometry(f'{pet_w}x{pet_h}+{pet_x}+{pet_y}')
root.after(0, update)
root.mainloop()

import os
import random
import tkinter as tk

BASE = os.path.dirname(os.path.abspath(__file__))

WALK_SPEED = 3 * 4
IDLE_DELAY = 200
WALK_DELAY = 120

ACTION_FRAMES = {
    'idle': [
        os.path.join(BASE, 'assets', 'idle', f'idle{i}.png')
        for i in range(1, 4)
    ],
    'walk_left': [
        os.path.join(BASE, 'assets', 'walk', 'left', f'walk2left{i}.png')
        for i in range(1, 4)
    ],
    'walk_right': [
        os.path.join(BASE, 'assets', 'walk', 'right', f'walk2right{i}.png')
        for i in range(1, 4)
    ],
    'walk_up': [
        os.path.join(BASE, 'assets', 'up-down', f'Screenshot (351){suffix}.png')
        for suffix in ('', '2', '3')
    ],
    'walk_down': [
        os.path.join(BASE, 'assets', 'up-down', f'Screenshot (351){suffix}.png')
        for suffix in ('', '2', '3')
    ],
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


class RatApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes('-topmost', True)
        self.root.bind_all('<KeyPress-0>', self.shutdown)
        self.root.bind_all('<KeyPress-KP_0>', self.shutdown)

        self.frames = {
            action: [tk.PhotoImage(file=path) for path in paths]
            for action, paths in ACTION_FRAMES.items()
        }

        self.pet_w = self.frames['idle'][0].width()
        self.pet_h = self.frames['idle'][0].height()

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.min_x = 0
        self.min_y = 0
        self.max_x = max(0, self.screen_w - self.pet_w)
        self.max_y = max(0, self.screen_h - self.pet_h)

        self.pet_x = self.screen_w // 2
        self.pet_y = self.screen_h // 2

        self.current_action = 'idle'
        self.frame_index = 0
        self.frames_left = random.randint(3, 8)

        self.label = tk.Label(self.root, bd=0)
        self.label.pack()

        self.root.geometry(f'{self.pet_w}x{self.pet_h}+{self.pet_x}+{self.pet_y}')
        self.root.after(0, self.update)

    def choose_action(self) -> str:
        return random.choices(
            ['idle', 'walk_left', 'walk_right', 'walk_up', 'walk_down'],
            weights=[5, 2, 2, 2, 2],
            k=1,
        )[0]

    def start_action(self, action: str) -> None:
        self.current_action = action
        self.frame_index = 0
        self.frames_left = random.randint(3, 8) if action == 'idle' else random.randint(1, 4)

    def bounce_if_needed(self) -> None:
        if self.pet_x <= self.min_x:
            self.pet_x = self.min_x
            if self.current_action == 'walk_left':
                self.start_action('walk_right')
        elif self.pet_x >= self.max_x:
            self.pet_x = self.max_x
            if self.current_action == 'walk_right':
                self.start_action('walk_left')

        if self.pet_y <= self.min_y:
            self.pet_y = self.min_y
            if self.current_action == 'walk_up':
                self.start_action('walk_down')
        elif self.pet_y >= self.max_y:
            self.pet_y = self.max_y
            if self.current_action == 'walk_down':
                self.start_action('walk_up')

    def update(self) -> None:
        frames = self.frames[self.current_action]
        self.label.configure(image=frames[self.frame_index])

        dx, dy = ACTION_MOVE[self.current_action]
        self.pet_x += dx
        self.pet_y += dy
        self.bounce_if_needed()
        self.root.geometry(f'{self.pet_w}x{self.pet_h}+{self.pet_x}+{self.pet_y}')

        self.frame_index += 1
        if self.frame_index >= len(frames):
            self.frame_index = 0
            self.frames_left -= 1
            if self.frames_left <= 0:
                self.start_action(self.choose_action())

        self.root.after(ACTION_DELAYS[self.current_action], self.update)

    def shutdown(self, event=None) -> None:
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == '__main__':
    RatApp().run()

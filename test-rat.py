import os
import random
import tkinter as tk
from tkinter import ttk
from fractions import Fraction

# ---------------------------------------------------------------------------
# Base tuning
# ---------------------------------------------------------------------------
HORIZONTAL_SPEED = 3 * 3
VERTICAL_SPEED = 3 * 3

SPRITE_SIZE_MODE = 'as_is'  # 'as_is' or 'uniform'
UNIFORM_SPRITE_SIZE = (180, 180)

LAUNCHER_SIZE_MODE = 'uniform'  # 'as_is' or 'uniform'
LAUNCHER_ICON_SIZE = (44, 44)

PLAY_AREA_MODE = 'full'  # 'full' or 'custom'
PLAY_MARGIN_LEFT_PCT = 0.05
PLAY_MARGIN_RIGHT_PCT = 0.05
PLAY_MARGIN_TOP_PCT = 0.05
PLAY_MARGIN_BOTTOM_PCT = 0.10

DEFAULT_ACTION_SETTINGS = {
    'idle': {
        'delay_ms': 220,
        'loops_min': 3,
        'loops_max': 10,
        'weight': 5,
    },
    'walk_left': {
        'delay_ms': 120,
        'loops_min': 2,
        'loops_max': 6,
        'weight': 2,
    },
    'walk_right': {
        'delay_ms': 120,
        'loops_min': 2,
        'loops_max': 6,
        'weight': 2,
    },
    'walk_up': {
        'delay_ms': 140,
        'loops_min': 2,
        'loops_max': 6,
        'weight': 2,
    },
    'walk_down': {
        'delay_ms': 140,
        'loops_min': 2,
        'loops_max': 6,
        'weight': 2,
    },
}

BASE = os.path.dirname(os.path.abspath(__file__))


def scale_frame_to_size(frame: tk.PhotoImage, target_w: int, target_h: int) -> tk.PhotoImage:
    # """Resize a tkinter PhotoImage using integer zoom/subsample ratios."""
    src_w = frame.width()
    src_h = frame.height()
    if src_w == target_w and src_h == target_h:
        return frame

    x_ratio = Fraction(target_w, src_w).limit_denominator(16)
    y_ratio = Fraction(target_h, src_h).limit_denominator(16)

    scaled = frame.zoom(max(1, x_ratio.numerator), max(1, y_ratio.numerator))
    if x_ratio.denominator > 1 or y_ratio.denominator > 1:
        scaled = scaled.subsample(max(1, x_ratio.denominator), max(1, y_ratio.denominator))
    return scaled


class RatDesktopApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes('-topmost', True)

        self.root.bind_all('<KeyPress-0>', self.shutdown)
        self.root.bind_all('<KeyPress-KP_0>', self.shutdown)

        self.base_action_settings = {name: values.copy() for name, values in DEFAULT_ACTION_SETTINGS.items()}
        self.action_settings = {name: values.copy() for name, values in DEFAULT_ACTION_SETTINGS.items()}

        self.sprite_size_mode = tk.StringVar(value=SPRITE_SIZE_MODE)
        self.uniform_width_var = tk.StringVar(value=str(UNIFORM_SPRITE_SIZE[0]))
        self.uniform_height_var = tk.StringVar(value=str(UNIFORM_SPRITE_SIZE[1]))

        self.launcher_size_mode = tk.StringVar(value=LAUNCHER_SIZE_MODE)
        self.launcher_width_var = tk.StringVar(value=str(LAUNCHER_ICON_SIZE[0]))
        self.launcher_height_var = tk.StringVar(value=str(LAUNCHER_ICON_SIZE[1]))

        self.play_area_mode = tk.StringVar(value=PLAY_AREA_MODE)
        self.margin_left_var = tk.StringVar(value=str(PLAY_MARGIN_LEFT_PCT))
        self.margin_right_var = tk.StringVar(value=str(PLAY_MARGIN_RIGHT_PCT))
        self.margin_top_var = tk.StringVar(value=str(PLAY_MARGIN_TOP_PCT))
        self.margin_bottom_var = tk.StringVar(value=str(PLAY_MARGIN_BOTTOM_PCT))

        self.horizontal_speed_var = tk.StringVar(value=str(HORIZONTAL_SPEED))
        self.vertical_speed_var = tk.StringVar(value=str(VERTICAL_SPEED))

        self.action_vars = {
            action: {
                'delay_ms': tk.StringVar(value=str(settings['delay_ms'])),
                'loops_min': tk.StringVar(value=str(settings['loops_min'])),
                'loops_max': tk.StringVar(value=str(settings['loops_max'])),
                'weight': tk.StringVar(value=str(settings['weight'])),
            }
            for action, settings in DEFAULT_ACTION_SETTINGS.items()
        }

        self.root.bind_all('<KeyPress-9>', self.open_settings_window)
        self.root.bind_all('<KeyPress-KP_9>', self.open_settings_window)

        self.main_label = tk.Label(self.root, bd=0)
        self.main_label.pack()
        self.main_label.bind('<ButtonPress-1>', self.on_press)
        self.main_label.bind('<B1-Motion>', self.on_drag)

        self.launcher_window = None
        self.launcher_label = None
        self.launcher_raw_frames_open = []
        self.launcher_raw_frames_closed = []
        self.launcher_frames_open = []
        self.launcher_frames_closed = []
        self.launcher_cycle = 0
        self.launcher_state = 'open'
        self.launcher_after_delay = 160
        self.launcher_w = 0
        self.launcher_h = 0
        self.launcher_x = 0
        self.launcher_y = 0

        self.settings_window = None
        self.settings_dirty = False

        self._drag_start_x = 0
        self._drag_start_y = 0

        self.raw_frames = {}
        self.frames = {}

        self.action = 'idle'
        self.cycle = 0
        self.loops_done = 0
        self.loops_target = 1

        self.pet_w = 0
        self.pet_h = 0
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0
        self.pet_x = 0
        self.pet_y = 0

        self.load_assets()
        self.rebuild_sprite_frames()
        self.rebuild_launcher_frames()
        self.rebuild_play_bounds()
        self.reset_position()
        self.start_action('idle')

        self.build_launcher_window()
        self.schedule_launcher_animation()
        self.root.after(150, self.process_settings_updates)
        self.root.after(0, self.update_pet)

    # ------------------------------------------------------------------
    # Asset loading and resizing
    # ------------------------------------------------------------------
    def load_frames(self, paths: list[str]) -> list[tk.PhotoImage]:
        return [tk.PhotoImage(file=path) for path in paths]

    def load_assets(self) -> None:
        self.raw_frames = {
            'idle': self.load_frames([
                os.path.join(BASE, 'assets', 'idle', f'idle{i}.png')
                for i in range(1, 4)
            ]),
            'walk_left': self.load_frames([
                os.path.join(BASE, 'assets', 'walk', 'left', f'walk2left{i}.png')
                for i in range(1, 4)
            ]),
            'walk_right': self.load_frames([
                os.path.join(BASE, 'assets', 'walk', 'right', f'walk2right{i}.png')
                for i in range(1, 4)
            ]),
            'walk_up': self.load_frames([
                os.path.join(BASE, 'assets', 'up-down', f'Screenshot (351){suffix}.png')
                for suffix in ('', '2', '3')
            ]),
            'walk_down': self.load_frames([
                os.path.join(BASE, 'assets', 'up-down', f'Screenshot (351){suffix}.png')
                for suffix in ('', '2', '3')
            ]),
        }

        self.launcher_raw_frames_open = self.load_frames([
            os.path.join(BASE, 'assets', 'settings', 'open', 'Screenshot (353).png'),
            os.path.join(BASE, 'assets', 'settings', 'open', 'Screenshot (354).png'),
        ])
        self.launcher_raw_frames_closed = self.load_frames([
            os.path.join(BASE, 'assets', 'settings', 'closed', 'Screenshot (355).png'),
            os.path.join(BASE, 'assets', 'settings', 'closed', 'Screenshot (356).png'),
        ])

    def rebuild_sprite_frames(self) -> None:
        if self.sprite_size_mode.get() == 'uniform':
            target_w = self._safe_int(self.uniform_width_var, UNIFORM_SPRITE_SIZE[0], minimum=1)
            target_h = self._safe_int(self.uniform_height_var, UNIFORM_SPRITE_SIZE[1], minimum=1)
            self.frames = {
                action: [scale_frame_to_size(frame, target_w, target_h) for frame in frames]
                for action, frames in self.raw_frames.items()
            }
        else:
            self.frames = {action: frames[:] for action, frames in self.raw_frames.items()}

        self.pet_w = self.frames['idle'][0].width()
        self.pet_h = self.frames['idle'][0].height()

    def rebuild_launcher_frames(self) -> None:
        if self.launcher_size_mode.get() == 'uniform':
            target_w = self._safe_int(self.launcher_width_var, LAUNCHER_ICON_SIZE[0], minimum=1)
            target_h = self._safe_int(self.launcher_height_var, LAUNCHER_ICON_SIZE[1], minimum=1)
            self.launcher_frames_open = [
                scale_frame_to_size(frame, target_w, target_h)
                for frame in self.launcher_raw_frames_open
            ]
            self.launcher_frames_closed = [
                scale_frame_to_size(frame, target_w, target_h)
                for frame in self.launcher_raw_frames_closed
            ]
        else:
            self.launcher_frames_open = self.launcher_raw_frames_open[:]
            self.launcher_frames_closed = self.launcher_raw_frames_closed[:]

        self.launcher_w = self.launcher_frames_open[0].width()
        self.launcher_h = self.launcher_frames_open[0].height()
        self.launcher_x = 0
        self.launcher_y = 0

    # ------------------------------------------------------------------
    # Bounds and state
    # ------------------------------------------------------------------
    def rebuild_play_bounds(self) -> None:
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        if self.play_area_mode.get() == 'custom':
            left = int(self.screen_w * self._safe_float(self.margin_left_var, PLAY_MARGIN_LEFT_PCT, minimum=0.0))
            right = int(self.screen_w * self._safe_float(self.margin_right_var, PLAY_MARGIN_RIGHT_PCT, minimum=0.0))
            top = int(self.screen_h * self._safe_float(self.margin_top_var, PLAY_MARGIN_TOP_PCT, minimum=0.0))
            bottom = int(self.screen_h * self._safe_float(self.margin_bottom_var, PLAY_MARGIN_BOTTOM_PCT, minimum=0.0))
            self.min_x = max(0, left)
            self.min_y = max(0, top)
            self.max_x = max(self.min_x, self.screen_w - self.pet_w - max(0, right))
            self.max_y = max(self.min_y, self.screen_h - self.pet_h - max(0, bottom))
        else:
            self.min_x = 0
            self.min_y = 0
            self.max_x = max(0, self.screen_w - self.pet_w)
            self.max_y = max(0, self.screen_h - self.pet_h)

    def reset_position(self) -> None:
        self.pet_x = (self.min_x + self.max_x) // 2
        self.pet_y = (self.min_y + self.max_y) // 2
        self.apply_geometry()

    def clamp_position(self) -> None:
        self.pet_x = max(self.min_x, min(self.max_x, self.pet_x))
        self.pet_y = max(self.min_y, min(self.max_y, self.pet_y))

    def apply_geometry(self) -> None:
        self.root.geometry(f'{self.pet_w}x{self.pet_h}+{self.pet_x}+{self.pet_y}')

    def avoid_launcher_overlap(self, previous_x: int | None = None, previous_y: int | None = None) -> None:
        if self.pet_x >= self.launcher_w or self.pet_y >= self.launcher_h:
            return

        if previous_x is not None and previous_x >= self.launcher_w:
            self.pet_x = self.launcher_w
            return

        if previous_y is not None and previous_y >= self.launcher_h:
            self.pet_y = self.launcher_h
            return

        push_x = self.launcher_w - self.pet_x
        push_y = self.launcher_h - self.pet_y
        if push_x <= push_y:
            self.pet_x = self.launcher_w
        else:
            self.pet_y = self.launcher_h

    # ------------------------------------------------------------------
    # Action helpers
    # ------------------------------------------------------------------
    def choose_loops(self, action_name: str) -> int:
        cfg = self.action_settings[action_name]
        return random.randint(cfg['loops_min'], cfg['loops_max'])

    def choose_action(self, exclude: str | None = None) -> str:
        names = list(self.action_settings.keys())
        if exclude in names and len(names) > 1:
            names.remove(exclude)
        weights = [self.action_settings[name]['weight'] for name in names]
        return random.choices(names, weights=weights, k=1)[0]

    def start_action(self, next_action: str) -> None:
        self.action = next_action
        self.cycle = 0
        self.loops_done = 0
        self.loops_target = self.choose_loops(next_action)

    def refresh_motion_from_settings(self) -> None:
        horizontal = self._safe_int(self.horizontal_speed_var, HORIZONTAL_SPEED, minimum=0)
        vertical = self._safe_int(self.vertical_speed_var, VERTICAL_SPEED, minimum=0)

        self.action_settings['walk_left']['dx'] = -horizontal
        self.action_settings['walk_left']['dy'] = 0
        self.action_settings['walk_right']['dx'] = horizontal
        self.action_settings['walk_right']['dy'] = 0
        self.action_settings['walk_up']['dx'] = 0
        self.action_settings['walk_up']['dy'] = -vertical
        self.action_settings['walk_down']['dx'] = 0
        self.action_settings['walk_down']['dy'] = vertical

    def refresh_action_settings_from_vars(self) -> None:
        for action_name, fields in self.action_vars.items():
            cfg = self.action_settings[action_name]
            cfg['delay_ms'] = self._safe_int(fields['delay_ms'], cfg['delay_ms'], minimum=1)
            cfg['loops_min'] = self._safe_int(fields['loops_min'], cfg['loops_min'], minimum=1)
            cfg['loops_max'] = self._safe_int(fields['loops_max'], cfg['loops_max'], minimum=1)
            cfg['weight'] = self._safe_int(fields['weight'], cfg['weight'], minimum=1)
            if cfg['loops_max'] < cfg['loops_min']:
                cfg['loops_max'] = cfg['loops_min']
                fields['loops_max'].set(str(cfg['loops_max']))

    def apply_live_settings(self) -> None:
        old_w = self.pet_w
        old_h = self.pet_h

        self.rebuild_sprite_frames()
        self.rebuild_launcher_frames()
        self.refresh_motion_from_settings()
        self.refresh_action_settings_from_vars()
        self.rebuild_play_bounds()

        if self.launcher_window is not None and self.launcher_window.winfo_exists():
            self.launcher_window.geometry(f'{self.launcher_w}x{self.launcher_h}+{self.launcher_x}+{self.launcher_y}')

        if old_w != self.pet_w or old_h != self.pet_h:
            self.clamp_position()
            self.apply_geometry()

        self.clamp_position()
        self.apply_geometry()

    def mark_settings_dirty(self, *args) -> None:
        self.settings_dirty = True

    def process_settings_updates(self) -> None:
        if self.settings_dirty:
            self.settings_dirty = False
            self.apply_live_settings()

        if self.root.winfo_exists():
            self.root.after(150, self.process_settings_updates)

    # ------------------------------------------------------------------
    # Settings window launcher
    # ------------------------------------------------------------------
    def build_launcher_window(self) -> None:
        self.launcher_window = tk.Toplevel(self.root)
        self.launcher_window.overrideredirect(True)
        self.launcher_window.wm_attributes('-topmost', True)
        self.launcher_window.geometry(f'{self.launcher_w}x{self.launcher_h}+{self.launcher_x}+{self.launcher_y}')
        self.launcher_label = tk.Label(self.launcher_window, bd=0)
        self.launcher_label.pack()
        self.launcher_label.bind('<Button-1>', self.open_settings_window)
        self.launcher_window.bind('<Button-1>', self.open_settings_window)

    def open_settings_window(self, event=None) -> None:
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.deiconify()
            self.settings_window.lift()
            self.settings_window.focus_force()
            self.launcher_state = 'closed'
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title('Rat Settings')
        self.settings_window.wm_attributes('-topmost', True)
        self.settings_window.protocol('WM_DELETE_WINDOW', self.close_settings_window)
        self.settings_window.resizable(False, False)

        container = tk.Frame(self.settings_window, padx=12, pady=12)
        container.pack(fill='both', expand=True)

        self._build_settings_panel(container)
        self.settings_window.lift()
        self.settings_window.focus_force()
        self.launcher_state = 'closed'
        self.launcher_cycle = 0

    def close_settings_window(self) -> None:
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.destroy()
        self.settings_window = None
        self.launcher_state = 'open'
        self.launcher_cycle = 0

    def _build_settings_panel(self, parent: tk.Widget) -> None:
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)

        motion_tab = ttk.Frame(notebook, padding=10)
        size_tab = ttk.Frame(notebook, padding=10)
        play_tab = ttk.Frame(notebook, padding=10)
        launcher_icon_tab = ttk.Frame(notebook, padding=10)
        launcher_tab = ttk.Frame(notebook, padding=10)
        behavior_tab = ttk.Frame(notebook, padding=10)

        notebook.add(motion_tab, text='Motion')
        notebook.add(size_tab, text='Size')
        notebook.add(play_tab, text='Play Area')
        notebook.add(launcher_icon_tab, text='Launcher Icon')
        notebook.add(launcher_tab, text='Launcher')
        notebook.add(behavior_tab, text='Behavior')

        def add_tab_note(tab: ttk.Frame, text: str) -> None:
            ttk.Label(tab, text=text, wraplength=460, justify='left').pack(anchor='w', pady=(0, 10))

        def add_labeled_row(tab: ttk.Frame, row_label: str, widget: tk.Widget) -> None:
            container = ttk.Frame(tab)
            container.pack(fill='x', pady=2)
            ttk.Label(container, text=row_label, width=18).pack(side='left')
            widget.pack(side='left', fill='x', expand=True)

        def make_entry(tab: ttk.Frame, variable: tk.Variable, width: int = 10) -> tk.Entry:
            return tk.Entry(tab, textvariable=variable, width=width)

        def make_choice(tab: ttk.Frame, variable: tk.StringVar, options: list[str]) -> ttk.Combobox:
            widget = ttk.Combobox(tab, textvariable=variable, values=options, state='readonly', width=12)
            return widget

        add_tab_note(motion_tab, 'Adjust movement speed here. Higher values make the rat travel farther each tick.')
        add_labeled_row(motion_tab, 'Horizontal speed', make_entry(motion_tab, self.horizontal_speed_var))
        add_labeled_row(motion_tab, 'Vertical speed', make_entry(motion_tab, self.vertical_speed_var))

        add_tab_note(size_tab, 'Use this page to keep the sprite as-is or force a single uniform size.')
        add_labeled_row(size_tab, 'Sprite size mode', make_choice(size_tab, self.sprite_size_mode, ['as_is', 'uniform']))
        add_labeled_row(size_tab, 'Uniform width', make_entry(size_tab, self.uniform_width_var))
        add_labeled_row(size_tab, 'Uniform height', make_entry(size_tab, self.uniform_height_var))

        add_tab_note(play_tab, 'These margins shrink the usable area so the rat stays away from the screen edges.')
        add_labeled_row(play_tab, 'Play mode', make_choice(play_tab, self.play_area_mode, ['full', 'custom']))
        add_labeled_row(play_tab, 'Left margin %', make_entry(play_tab, self.margin_left_var))
        add_labeled_row(play_tab, 'Right margin %', make_entry(play_tab, self.margin_right_var))
        add_labeled_row(play_tab, 'Top margin %', make_entry(play_tab, self.margin_top_var))
        add_labeled_row(play_tab, 'Bottom margin %', make_entry(play_tab, self.margin_bottom_var))

        add_tab_note(launcher_icon_tab, 'This section controls the top-left settings icon size. Make it smaller if it feels too large on your screen.')
        add_labeled_row(launcher_icon_tab, 'Launcher size mode', make_choice(launcher_icon_tab, self.launcher_size_mode, ['as_is', 'uniform']))
        add_labeled_row(launcher_icon_tab, 'Icon width', make_entry(launcher_icon_tab, self.launcher_width_var))
        add_labeled_row(launcher_icon_tab, 'Icon height', make_entry(launcher_icon_tab, self.launcher_height_var))

        add_tab_note(launcher_tab, 'The launcher sits in the top-left corner and opens or closes the settings panel. When the panel is open, the launcher shows the closed animation.')

        add_tab_note(behavior_tab, 'Each row below controls how long that animation lasts and how often it is chosen.')
        header = ttk.Frame(behavior_tab)
        header.pack(fill='x', pady=(0, 4))
        for text, width in [('Action', 12), ('Delay', 10), ('Loop min', 10), ('Loop max', 10), ('Weight', 10)]:
            ttk.Label(header, text=text, width=width, anchor='center').pack(side='left', padx=2)

        for action_name in ['idle', 'walk_left', 'walk_right', 'walk_up', 'walk_down']:
            row = ttk.Frame(behavior_tab)
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=action_name, width=12).pack(side='left')
            ttk.Entry(row, textvariable=self.action_vars[action_name]['delay_ms'], width=10).pack(side='left', padx=2)
            ttk.Entry(row, textvariable=self.action_vars[action_name]['loops_min'], width=10).pack(side='left', padx=2)
            ttk.Entry(row, textvariable=self.action_vars[action_name]['loops_max'], width=10).pack(side='left', padx=2)
            ttk.Entry(row, textvariable=self.action_vars[action_name]['weight'], width=10).pack(side='left', padx=2)

        footer = ttk.Frame(parent)
        footer.pack(fill='x', pady=(10, 0))
        ttk.Button(footer, text='Close', command=self.close_settings_window).pack(side='right')

        widgets_to_watch = [
            self.sprite_size_mode,
            self.uniform_width_var,
            self.uniform_height_var,
            self.play_area_mode,
            self.margin_left_var,
            self.margin_right_var,
            self.margin_top_var,
            self.margin_bottom_var,
            self.horizontal_speed_var,
            self.vertical_speed_var,
            self.launcher_size_mode,
            self.launcher_width_var,
            self.launcher_height_var,
        ]

        for variable in widgets_to_watch:
            variable.trace_add('write', self.mark_settings_dirty)

        for fields in self.action_vars.values():
            for variable in fields.values():
                variable.trace_add('write', self.mark_settings_dirty)

        self.mark_settings_dirty()

    def schedule_launcher_animation(self) -> None:
        if self.launcher_window is None or not self.launcher_window.winfo_exists():
            return

        frames = self.launcher_frames_closed if self.launcher_state == 'closed' else self.launcher_frames_open
        if not frames:
            return

        if self.launcher_cycle >= len(frames):
            self.launcher_cycle = 0

        self.launcher_label.configure(image=frames[self.launcher_cycle])
        self.launcher_cycle += 1
        self.launcher_window.after(self.launcher_after_delay, self.schedule_launcher_animation)

    # ------------------------------------------------------------------
    # Rat interaction
    # ------------------------------------------------------------------
    def on_press(self, event) -> None:
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def on_drag(self, event) -> None:
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        self.pet_x = max(self.min_x, min(self.max_x, self.root.winfo_x() + dx))
        self.pet_y = max(self.min_y, min(self.max_y, self.root.winfo_y() + dy))
        self.avoid_launcher_overlap()
        self.apply_geometry()

    def update_pet(self) -> None:
        if not self.root.winfo_exists():
            return

        cfg = self.action_settings[self.action]
        frames = self.frames[self.action]
        previous_x = self.pet_x
        previous_y = self.pet_y

        self.main_label.configure(image=frames[self.cycle])

        self.pet_x += cfg.get('dx', 0)
        self.pet_y += cfg.get('dy', 0)

        if self.pet_x <= self.min_x:
            self.pet_x = self.min_x
            if self.action == 'walk_left':
                self.start_action('walk_right')
                cfg = self.action_settings[self.action]
                frames = self.frames[self.action]
        elif self.pet_x >= self.max_x:
            self.pet_x = self.max_x
            if self.action == 'walk_right':
                self.start_action('walk_left')
                cfg = self.action_settings[self.action]
                frames = self.frames[self.action]

        if self.pet_y <= self.min_y:
            self.pet_y = self.min_y
            if self.action == 'walk_up':
                self.start_action('walk_down')
                cfg = self.action_settings[self.action]
                frames = self.frames[self.action]
        elif self.pet_y >= self.max_y:
            self.pet_y = self.max_y
            if self.action == 'walk_down':
                self.start_action('walk_up')
                cfg = self.action_settings[self.action]
                frames = self.frames[self.action]

        self.avoid_launcher_overlap(previous_x, previous_y)

        self.apply_geometry()

        self.cycle += 1
        if self.cycle >= len(frames):
            self.cycle = 0
            self.loops_done += 1
            if self.loops_done >= self.loops_target:
                self.start_action(self.choose_action(exclude=self.action))
                cfg = self.action_settings[self.action]

        self.root.after(cfg['delay_ms'], self.update_pet)

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _safe_int(self, variable: tk.Variable, fallback: int, minimum: int | None = None) -> int:
        try:
            value = int(variable.get())
        except (TypeError, ValueError):
            return fallback
        if minimum is not None:
            value = max(minimum, value)
        return value

    def _safe_float(self, variable: tk.Variable, fallback: float, minimum: float | None = None) -> float:
        try:
            value = float(variable.get())
        except (TypeError, ValueError):
            return fallback
        if minimum is not None:
            value = max(minimum, value)
        return value

    def shutdown(self, event=None) -> None:
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.destroy()
        if self.launcher_window is not None and self.launcher_window.winfo_exists():
            self.launcher_window.destroy()
        if self.root.winfo_exists():
            self.root.destroy()

    def run(self) -> None:
        self.root.geometry(f'{self.pet_w}x{self.pet_h}+{self.pet_x}+{self.pet_y}')
        self.root.after(0, self.update_pet)
        self.root.mainloop()


if __name__ == '__main__':
    RatDesktopApp().run()

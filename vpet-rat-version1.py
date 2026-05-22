import os 
import random
import tkinter as tk
from tkinter import ttk
from fractions import Fraction


# ---------------------------------------------------------------------------
# Base tuning
# ---------------------------------------------------------------------------
x_speed = 9
y_speed = 9 

sprite_size = 'as_is'   # default 'as_is' because I dont care about the sizes but can be changed to 'uniform'
uniform_sprite_size = (180, 180)  # option can be either 'as_is' or 'uniform'

settings_size = 'uniform' # settings icon size is 'as_is' but can be changed to 'uniform'
settings_icon = (60,60)

play_area = 'full'  # default full screen but can be changed to anything

play_area_left = 0.05
play_area_right = 0.05
play_area_up = 0.05
play_area_down = 0.1

default_actions_settings = {
    'idle':{
        'delay_ms': 200,
        'loop_min': 9,      # default 6 since it would loop twice at least
        'loop_max': 12,      # three loops can be changed
        'luck': 2,          # this is fequency of an animation the higher the luck the more likely its gonna do the act         
    },
    'walk_left':{
        'delay_ms': 120,
        'loop_min': 6,      # default 6 since it would loop twice at least
        'loop_max': 9,      # three loops can be changed
        'luck': 2,          # this is fequency of an animation the higher the luck the more likely its gonna do the act         
    },
    'walk_right':{
        'delay_ms': 120,
        'loop_min': 6,      # default 6 since it would loop twice at least
        'loop_max': 9,      # three loops can be changed
        'luck': 2,          # this is fequency of an animation the higher the luck the more likely its gonna do the act         
    },
    'walk_up':{
        'delay_ms': 120,
        'loop_min': 6,      # default 6 since it would loop twice at least
        'loop_max': 9,      # three loops can be changed
        'luck': 2,          # this is fequency of an animation the higher the luck the more likely its gonna do the act         
    },
    'walk_down':{
        'delay_ms': 120,
        'loop_min': 6,      # default 6 since it would loop twice at least
        'loop_max': 9,      # three loops can be changed
        'luck': 2,          # this is fequency of an animation the higher the luck the more likely its gonna do the act         
    },
}

BASE = os.path.dirname(os.path.abspath(__file__))   

# the function scale_frame_to_size controls the sizes of all the assets that exist but it ONLY applys to the 'uniform' option
# meaning that when the 'uniform' option is active the user will be able to input a size and this function figures out the ratios and everything else

def scale_frame_to_size(frame: tk.PhotoImage, target_w: int, target_h:int) -> tk.PhotoImage:
    src_w = frame.width()
    src_h = frame.height()
    if src_w == target_w and src_h == target_h:
        return frame
    
    x_ratio = Fraction (target_w, src_w).limit_denominator(16)
    y_ratio = Fraction (target_h, src_h).limit_denominator(16)
    # the liit_denominator is the ratio of shrinking and growth 
    # imagine it to be something like 180/480 => 3/8 -> since the denominator is 8 it passes
    # obviously 16 > 8 is not bigger than it so yeah its allowed
    
    scaled = frame.zoom(max(1, x_ratio.numerator), max(1, y_ratio.numerator))
    if x_ratio.denominator > 1 or y_ratio.denominator > 1: 
        scaled = scaled.subsample(max(1, x_ratio.denominator), max(1, y_ratio.denominator))
    return scaled


class rat:
    
    # ------------------------------------------------------------------
    # Initializer for everything thats gonne be used in the project
    # ------------------------------------------------------------------
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes('-topmost', True)
        
        # self.root.bind_all('<KeyPress-->', self.shutdown)       # Killswitch the button is '-' 
        # self.root.bind_all('<KeyPress-KP_Subtract>', self.shutdown)
        self.root.bind_all('<KeyPress-p>', self.shutdown)
        
        self.base_action_settings = {name: values.copy() for name, values in default_actions_settings.items()}      # initializer for actions
        self.action_settings = {name: values.copy() for name, values in default_actions_settings.items()}
        
        self.sprite_size_mode = tk.StringVar(value=sprite_size)                         # settings initalizers
        self.uniform_width_var = tk.StringVar(value=str(uniform_sprite_size[0]))
        self.uniform_height_var = tk.StringVar(value=str(uniform_sprite_size[1]))

        self.setting_size_mode = tk.StringVar(value=settings_size)              # settings sizes initalizers
        self.setting_width_var = tk.StringVar(value=str(settings_icon[0]))
        self.setting_height_var = tk.StringVar(value=str(settings_icon[1]))

        self.play_area_mode = tk.StringVar(value=play_area)                     # play area initalizer
        self.margin_left_var = tk.StringVar(value=str(play_area_left))
        self.margin_right_var = tk.StringVar(value=str(play_area_right))
        self.margin_top_var = tk.StringVar(value=str(play_area_up))
        self.margin_bottom_var = tk.StringVar(value=str(play_area_down))

        self.horizontal_speed_var = tk.StringVar(value=str(x_speed))        # sprite speed initalizers
        self.vertical_speed_var = tk.StringVar(value=str(y_speed))  
        
        self.action_vars ={                                                 # moving functions initalizers
            action:{
                'delay_ms': tk.StringVar(value=str(settings['delay_ms'])),
                'loop_min': tk.StringVar(value=str(settings['loop_min'])),
                'loop_max': tk.StringVar(value=str(settings['loop_max'])),
                'luck': tk.StringVar(value=str(settings['luck'])),
            }
            for action, settings in default_actions_settings.items()
        }
        
        # self.root.bind_all('<KeyPress-=>', self.open_settings_window)  # this is the opening button for the setting '='
        # self.root.bind_all('<KeyPress-KP_Equal>', self.open_settings_window)
        self.root.bind_all('<KeyPress-o>', self.open_settings_window)
        
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
        self.refresh_motion_from_settings()
        self.refresh_action_settings_from_vars()
        self.reset_position()
        self.start_action('idle')

        self.build_launcher_window()
        self.open_settings_window()
        self.schedule_launcher_animation()
        self.root.after(150, self.process_settings_updates)


    # ------------------------------------------------------------------
    # Asset loading and resizing
    # ------------------------------------------------------------------
    def load_frames(self, paths: list[str]) -> list[tk.PhotoImage]:
        return [tk.PhotoImage(file=path) for path in paths]
    
    def load_assets(self) -> None:
        self.raw_frames ={
            'idle': self.load_frames([
                os.path.join(BASE, 'assets', 'idle', f'idle{innie}.png')
                for innie in range(1,4)
            ]),
            'walk_left': self.load_frames([
                os.path.join(BASE, 'assets', 'walk', 'left', f'walk2left{innie}.png')
                for innie in range(1,4)
            ]),
            'walk_right': self.load_frames([
                os.path.join(BASE, 'assets', 'walk', 'right', f'walk2right{innie}.png')
                for innie in range(1,4)
            ]),
            'walk_up': self.load_frames([
                os.path.join(BASE, 'assets', 'up-down', f'updown{innie}.png')
                for innie in range(1,4)
            ]),
            'walk_down': self.load_frames([
                os.path.join(BASE, 'assets', 'up-down', f'updown{innie}.png')
                for innie in range(1,4)
            ]),
        }
        
        self.setting_raw_frames_open = self.load_frames([
            os.path.join(BASE, 'assets', 'settings', 'open', 'open1.png'),
            os.path.join(BASE, 'assets', 'settings', 'open', 'open2.png'),
        ])
        self.setting_raw_frames_close = self.load_frames([
            os.path.join(BASE, 'assets', 'settings', 'closed', 'close1.png'),
            os.path.join(BASE, 'assets', 'settings', 'closed', 'close2.png'),
        ])
        
        
    def rebuild_sprite_frames(self) -> None:
        if self.sprite_size_mode.get() == 'uniform':
            target_w = self._safe_int(self.uniform_width_var, uniform_sprite_size[0], minimum=1)
            target_h = self._safe_int(self.uniform_height_var, uniform_sprite_size[1], minimum=1)
            self.frames = {
                action: [scale_frame_to_size(frame, target_w, target_h) for frame in frames]
                for action, frames in self.raw_frames.items()
            }
        else:
            self.frames = {action: frames[:] for action, frames in self.raw_frames.items()}

        self.pet_w = self.frames['idle'][0].width()
        self.pet_h = self.frames['idle'][0].height()

    def rebuild_launcher_frames(self) -> None:
        if self.setting_size_mode.get() == 'uniform':
            target_w = self._safe_int(self.setting_width_var, settings_icon[0], minimum=1)
            target_h = self._safe_int(self.setting_height_var, settings_icon[1], minimum=1)
            self.launcher_frames_open = [
                scale_frame_to_size(frame, target_w, target_h)
                for frame in self.setting_raw_frames_open
            ]
            self.launcher_frames_closed = [
                scale_frame_to_size(frame, target_w, target_h)
                for frame in self.setting_raw_frames_close
            ]
        else:
            self.launcher_frames_open = self.setting_raw_frames_open[:]
            self.launcher_frames_closed = self.setting_raw_frames_close[:]

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
            left = int(self.screen_w * self._safe_float(self.margin_left_var, play_area_left, minimum=0.0))
            right = int(self.screen_w * self._safe_float(self.margin_right_var, play_area_right, minimum=0.0))
            top = int(self.screen_h * self._safe_float(self.margin_top_var, play_area_up, minimum=0.0))
            bottom = int(self.screen_h * self._safe_float(self.margin_bottom_var, play_area_down, minimum=0.0))
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
        return random.randint(cfg['loop_min'], cfg['loop_max'])

    def choose_action(self, exclude: str | None = None) -> str:
        names = list(self.action_settings.keys())
        if exclude in names and len(names) > 1:
            names.remove(exclude)
        luck = [self.action_settings[name]['luck'] for name in names]
        return random.choices(names, weights=luck, k=1)[0]

    def start_action(self, next_action: str) -> None:
        self.action = next_action
        self.cycle = 0
        self.loops_done = 0
        self.loops_target = self.choose_loops(next_action)

    def refresh_motion_from_settings(self) -> None:
        horizontal = self._safe_int(self.horizontal_speed_var, x_speed, minimum=0)
        vertical = self._safe_int(self.vertical_speed_var, y_speed, minimum=0)

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
            cfg['loop_min'] = self._safe_int(fields['loop_min'], cfg['loop_min'], minimum=1)
            cfg['loop_max'] = self._safe_int(fields['loop_max'], cfg['loop_max'], minimum=1)
            cfg['luck'] = self._safe_int(fields['luck'], cfg['luck'], minimum=1)
            if cfg['loop_max'] < cfg['loop_min']:
                cfg['loop_max'] = cfg['loop_min']
                fields['loop_max'].set(str(cfg['loop_max']))

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
            self.close_settings_window()
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
        self.apply_live_settings()
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.destroy()
        self.settings_window = None
        self.launcher_state = 'open'
        self.launcher_cycle = 0

    def _build_settings_panel(self, parent: tk.Widget) -> None:
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)
        
        controls_tab=ttk.Frame(notebook, padding=10)

        motion_tab = ttk.Frame(notebook, padding=10)
        size_tab = ttk.Frame(notebook, padding=10)
        play_tab = ttk.Frame(notebook, padding=10)
        settings_tab = ttk.Frame(notebook, padding=10)
        behavior_tab = ttk.Frame(notebook, padding=10)
        issues_tab = ttk.Frame(notebook, padding = 10)
        
        notebook.add(controls_tab, text='Controls')
        notebook.add(motion_tab, text='Motion')
        notebook.add(size_tab, text='Size')
        notebook.add(play_tab, text='Play Area')
        notebook.add(settings_tab, text='Settings Icon')
        notebook.add(behavior_tab, text='Behavior')
        notebook.add(issues_tab, text = 'Known Bugs')

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
        
        add_tab_note(controls_tab, 'The controls are pretty simple its only two:')
        add_tab_note(controls_tab, 'P - Progam Killswitch')
        add_tab_note(controls_tab, 'O - Open/Close the Settings')
        add_tab_note(controls_tab, 'this game sucks and is made by one person, me. So, there will be bugs, my bad. I will continue to fix this garbage.')
        
        add_tab_note(issues_tab, 'Known Issues: ')
        add_tab_note(issues_tab, '1 - clicking the settings icon doesnt open it... well it does but it also closes it')
        add_tab_note(issues_tab, '2 - another issue (kinda) when you edit the settings it automatically changes while you write it. so if the speed is 9 and you changee it to 100 it will IMMEDIATLY change.')
        add_tab_note(issues_tab, '3 - have you noticed the weird white space that appears sometimes? yeah idk how to fix that but its steams from assets sizes mismatching. If a frame is 20x20px and the other frame is 40x40px there will be whitespace.')

        add_tab_note(motion_tab, 'Change the movement speed for all assets here.')
        add_tab_note(motion_tab, 'Defult is 9 (3 frames an animation so 3 times its speed) but you can go crazy and break it :)')
        add_labeled_row(motion_tab, 'Horizontal speed', make_entry(motion_tab, self.horizontal_speed_var))
        add_labeled_row(motion_tab, 'Vertical speed', make_entry(motion_tab, self.vertical_speed_var))

        add_tab_note(size_tab, 'Change the size of the little cute rat or whatever asset you swapped it with.')
        add_tab_note(size_tab, 'Default "as_is".')
        add_tab_note(size_tab, 'Note "as_is" is for whatever size the original image was, while "uniform" is a controlled size. best if you know what size you want.')
        add_labeled_row(size_tab, 'Rat size type', make_choice(size_tab, self.sprite_size_mode, ['as_is', 'uniform']))
        add_labeled_row(size_tab, 'Uniform width', make_entry(size_tab, self.uniform_width_var))
        add_labeled_row(size_tab, 'Uniform height', make_entry(size_tab, self.uniform_height_var))

        add_tab_note(play_tab, 'The "Play Area" is how much space would the rat have.')
        add_tab_note(play_tab, 'Default is "full" for the entire screen.')
        add_tab_note(play_tab,'"full" is the entire screen. "custom" is a size you control. I recomend to keep it bigger than the rat so it moves but its up to you im not your ma or pop.')
        add_labeled_row(play_tab, 'Play mode', make_choice(play_tab, self.play_area_mode, ['full', 'custom']))
        add_labeled_row(play_tab, 'Left margin %', make_entry(play_tab, self.margin_left_var))
        add_labeled_row(play_tab, 'Right margin %', make_entry(play_tab, self.margin_right_var))
        add_labeled_row(play_tab, 'Top margin %', make_entry(play_tab, self.margin_top_var))
        add_labeled_row(play_tab, 'Bottom margin %', make_entry(play_tab, self.margin_bottom_var))

        add_tab_note(settings_tab, 'Change the settings icon size.')
        add_tab_note(settings_tab, 'Default is "uniform" because the "as_is" images are big as hell.')
        add_tab_note(settings_tab, '"uniform" control the size. "as_is" whatever the asset is.')
        add_labeled_row(settings_tab, 'Setting size mode', make_choice(settings_tab, self.setting_size_mode, ['as_is', 'uniform']))
        add_labeled_row(settings_tab, 'Setting width', make_entry(settings_tab, self.setting_width_var))
        add_labeled_row(settings_tab, 'Setting height', make_entry(settings_tab, self.setting_height_var))

        # add_tab_note(launcher_tab, 'The launcher sits in the top-left corner and opens or closes the settings panel. When the panel is open, the launcher shows the closed animation.')

        add_tab_note(behavior_tab, 'Change the Rat Behavior.')
        add_tab_note(behavior_tab, 'Action: What thing the rat can be doing. In the future there will be more... i hope')
        add_tab_note(behavior_tab, 'Delay: How long the wait will be for each animation')
        add_tab_note(behavior_tab, 'Loop Minimum: Default 6 & 9 because it makes the animation long enough to tell whats happening.')
        add_tab_note(behavior_tab, 'Loop Max: Default 9 and 12 because i felt like it. Point is that you can extend the animation loop')
        add_tab_note(behavior_tab, 'Luck: Control the likelyhood the Action will appear')
        header = ttk.Frame(behavior_tab)
        header.pack(fill='x', pady=(0, 4))
        for text, width in [('Action', 12), ('Delay', 10), ('Loop min', 10), ('Loop max', 10), ('Luck', 10)]:
            ttk.Label(header, text=text, width=width, anchor='center').pack(side='left', padx=2)

        for action_name in ['idle', 'walk_left', 'walk_right', 'walk_up', 'walk_down']:
            row = ttk.Frame(behavior_tab)
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=action_name, width=12).pack(side='left')
            ttk.Entry(row, textvariable=self.action_vars[action_name]['delay_ms'], width=10).pack(side='left', padx=2)
            ttk.Entry(row, textvariable=self.action_vars[action_name]['loop_min'], width=10).pack(side='left', padx=2)
            ttk.Entry(row, textvariable=self.action_vars[action_name]['loop_max'], width=10).pack(side='left', padx=2)
            ttk.Entry(row, textvariable=self.action_vars[action_name]['luck'], width=10).pack(side='left', padx=2)

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
            self.setting_size_mode,
            self.setting_width_var,
            self.setting_height_var,
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
    rat().run()


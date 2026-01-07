import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
import random

# --- DEFINIRE TEME (PALETE DE CULORI) ---
THEMES = {
    "Dark Mode (Spotify)": {
        "bg": "#1e1e1e", "fg": "#ffffff", "btn": "#2d2d2d",
        "accent": "#1db954", "list_bg": "#121212", "list_fg": "#ffffff",
        "fav": "#e91e63", "remove": "#ff5252"
    },
    "Light Mode (Classic)": {
        "bg": "#f0f2f5", "fg": "#000000", "btn": "#ffffff",
        "accent": "#1877f2", "list_bg": "#ffffff", "list_fg": "#000000",
        "fav": "#ff4081", "remove": "#d32f2f"
    },
    "Cyberpunk (Neon)": {
        "bg": "#0b0c15", "fg": "#00f3ff", "btn": "#181a25",
        "accent": "#ff0099", "list_bg": "#000000", "list_fg": "#00f3ff",
        "fav": "#ff0099", "remove": "#ff2a2a"
    },
    "Retro Gold (Elegant)": {
        "bg": "#2c2c2c", "fg": "#f1c40f", "btn": "#3d3d3d",
        "accent": "#d4ac0d", "list_bg": "#222222", "list_fg": "#f39c12",
        "fav": "#e67e22", "remove": "#c0392b"
    }
}

# Configurații fonturi
FONT_MAIN = ("Arial", 10)
FONT_ICONS = ("Arial", 14)


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python MP3 Player - Multi-Theme")
        self.root.geometry("700x550")

        # Inițializare Pygame
        pygame.mixer.init()

        # Variabile de stare
        self.paused = False
        self.current_song_index = 0
        self.is_looping = False
        self.is_shuffling = False

        self.main_playlist = []
        self.fav_playlist = []
        self.active_playlist_data = self.main_playlist

        # --- COLECVȚII DE WIDGET-URI PENTRU THEMING ---
        # Salvăm referințe la toate elementele pentru a le putea schimba culoarea
        self.colored_frames = []
        self.colored_labels = []
        self.colored_buttons = []  # Butoane standard (fără logică specială de culoare)

        # Setăm tema implicită
        self.current_theme = THEMES["Dark Mode (Spotify)"]

        # --- SETUP INTERFAȚĂ ---
        self.setup_ui()

        # Aplicăm culorile inițiale
        self.apply_theme("Dark Mode (Spotify)")

    def setup_ui(self):
        # 1. Header
        self.title_label = tk.Label(self.root, text="My Music Library", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)
        self.colored_labels.append(self.title_label)

        # 2. Tabs Area (TTK Notebook)
        self.style = ttk.Style()
        self.style.theme_use('default')

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        self.tab1 = tk.Frame(self.tabs)
        self.tab2 = tk.Frame(self.tabs)
        self.colored_frames.extend([self.tab1, self.tab2])

        self.tabs.add(self.tab1, text="🎵 Toate Melodiile")
        self.tabs.add(self.tab2, text="❤ Favorite")
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Listboxes
        self.main_listbox = self.create_listbox(self.tab1)
        self.main_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fav_listbox = self.create_listbox(self.tab2)
        self.fav_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.active_listbox_widget = self.main_listbox

        # 3. Control Area
        self.control_area = tk.Frame(self.root)
        self.control_area.pack(pady=15, fill=tk.X)
        self.colored_frames.append(self.control_area)

        # Slider Volum
        self.volume_slider = tk.Scale(
            self.control_area, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL,
            bd=0, highlightthickness=0, showvalue=0, length=100, label="Volum",
            command=self.set_volume
        )
        self.volume_slider.set(0.5)
        self.volume_slider.pack(side=tk.RIGHT, padx=20)

        # Frame Butoane
        self.btns_frame = tk.Frame(self.control_area)
        self.btns_frame.pack(side=tk.TOP)
        self.colored_frames.append(self.btns_frame)

        # Configurație stil butoane
        btn_conf = {"bd": 0, "relief": tk.FLAT, "font": FONT_ICONS, "width": 4, "cursor": "hand2"}

        # -- Creare Butoane --
        # Favorite Group
        self.fav_add_btn = tk.Button(self.btns_frame, text="❤", command=self.add_to_favorites, **btn_conf)
        self.fav_remove_btn = tk.Button(self.btns_frame, text="💔", command=self.remove_from_favorites, **btn_conf)

        # Playback Group
        self.shuffle_btn = tk.Button(self.btns_frame, text="🔀", command=self.toggle_shuffle, **btn_conf)
        self.prev_btn = tk.Button(self.btns_frame, text="⏮", command=self.prev_song, **btn_conf)
        self.play_btn = tk.Button(self.btns_frame, text="▶", command=self.play_music, **btn_conf)
        self.pause_btn = tk.Button(self.btns_frame, text="⏸", command=self.pause_music, **btn_conf)
        self.stop_btn = tk.Button(self.btns_frame, text="⏹", command=self.stop_music, **btn_conf)
        self.next_btn = tk.Button(self.btns_frame, text="⏭", command=self.next_song, **btn_conf)
        self.loop_btn = tk.Button(self.btns_frame, text="🔁", command=self.toggle_loop, **btn_conf)

        # Adăugăm butoanele standard la lista pentru colorare automată
        # (Cele speciale - Shuffle, Loop, Play, Fav - le gestionăm manual în apply_theme)
        self.colored_buttons.extend([self.prev_btn, self.pause_btn, self.stop_btn, self.next_btn])

        # Grid Layout
        self.fav_add_btn.grid(row=0, column=0, padx=(0, 2))
        self.fav_remove_btn.grid(row=0, column=1, padx=(0, 20))
        self.shuffle_btn.grid(row=0, column=2, padx=5)
        self.prev_btn.grid(row=0, column=3, padx=5)
        self.play_btn.grid(row=0, column=4, padx=5)
        self.pause_btn.grid(row=0, column=5, padx=5)
        self.stop_btn.grid(row=0, column=6, padx=5)
        self.next_btn.grid(row=0, column=7, padx=5)
        self.loop_btn.grid(row=0, column=8, padx=5)

        # 4. Status Bar
        self.status_bar = tk.Label(self.root, text="Selectează o temă din meniu!", bd=0, relief=tk.FLAT,
                                   anchor=tk.W, font=("Arial", 9), padx=10)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)
        # Status bar are culori specifice de buton, nu de label standard

        # 5. MENIU
        self.create_menu()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        # Meniu Fișier
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Fișier", menu=file_menu)
        file_menu.add_command(label="Adaugă Melodie", command=self.add_song)
        file_menu.add_command(label="Adaugă Folder", command=self.add_many_songs)
        file_menu.add_separator()
        file_menu.add_command(label="Ieșire", command=self.root.quit)

        # Meniu Teme (NOU)
        theme_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="🎨 Teme", menu=theme_menu)

        # Adăugăm dinamic opțiunile din dicționarul THEMES
        for theme_name in THEMES.keys():
            theme_menu.add_command(label=theme_name, command=lambda t=theme_name: self.apply_theme(t))

    def create_listbox(self, parent):
        return tk.Listbox(parent, width=60, height=10, bd=0, highlightthickness=0,
                          font=FONT_MAIN, activestyle="none")

    # --- LOGICA DE SCHIMBARE A TEMEI ---
    def apply_theme(self, theme_name):
        t = THEMES[theme_name]
        self.current_theme = t  # Salvăm tema curentă

        # 1. Root & Frames
        self.root.configure(bg=t["bg"])
        for frame in self.colored_frames:
            frame.configure(bg=t["bg"])

        # 2. Labels
        for label in self.colored_labels:
            label.configure(bg=t["bg"], fg=t["fg"])

        # 3. Listboxes
        for lb in [self.main_listbox, self.fav_listbox]:
            lb.configure(bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["accent"], selectforeground="white")

        # 4. Tabs Style (TTK)
        self.style.configure("TNotebook", background=t["bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab", background=t["btn"], foreground=t["fg"], padding=[10, 5])
        self.style.map("TNotebook.Tab", background=[("selected", t["accent"])], foreground=[("selected", "white")])

        # 5. Slider
        self.volume_slider.configure(bg=t["bg"], fg=t["fg"], troughcolor=t["btn"])

        # 6. Status Bar
        self.status_bar.configure(bg=t["btn"], fg=t["fg"])

        # 7. Butoane Standard (Prev, Next, Stop, Pause)
        for btn in self.colored_buttons:
            btn.configure(bg=t["btn"], fg=t["fg"], activebackground=t["accent"], activeforeground="white")

        # 8. Butoane Speciale (Trebuie tratate separat pentru că au culori specifice)

        # Play Button
        self.play_btn.configure(bg=t["accent"], fg="white", activebackground=t["fg"], activeforeground=t["bg"])

        # Favorite Buttons
        self.fav_add_btn.configure(bg=t["btn"], fg=t["fav"], activebackground=t["fav"], activeforeground="white")
        self.fav_remove_btn.configure(bg=t["btn"], fg="#aaaaaa", activebackground=t["remove"], activeforeground="white")

        # Shuffle & Loop (Verificăm starea lor activă/inactivă)
        self.update_toggle_buttons_color()

        self.status_bar.config(text=f"Tema schimbată: {theme_name}")

    def update_toggle_buttons_color(self):
        t = self.current_theme
        # Shuffle
        if self.is_shuffling:
            self.shuffle_btn.configure(bg=t["btn"], fg=t["accent"], activebackground=t["btn"])
        else:
            self.shuffle_btn.configure(bg=t["btn"], fg="#777777", activebackground=t["btn"])  # Gri inactiv

        # Loop
        if self.is_looping:
            self.loop_btn.configure(bg=t["btn"], fg=t["accent"], activebackground=t["btn"])
        else:
            self.loop_btn.configure(bg=t["btn"], fg="#777777", activebackground=t["btn"])

    # --- FUNCTIONALITATE (Aceleași funcții, doar mici ajustări la toggle) ---

    def toggle_loop(self):
        self.is_looping = not self.is_looping
        self.update_toggle_buttons_color()  # Actualizăm culoarea conform temei curente
        state = "PORNIT" if self.is_looping else "OPRIT"
        self.status_bar.config(text=f"Loop: {state}")

    def toggle_shuffle(self):
        self.is_shuffling = not self.is_shuffling
        self.update_toggle_buttons_color()
        state = "PORNIT" if self.is_shuffling else "OPRIT"
        self.status_bar.config(text=f"Shuffle: {state}")

    def on_tab_change(self, event):
        selected_tab = self.tabs.index(self.tabs.select())
        if selected_tab == 0:
            self.active_playlist_data = self.main_playlist
            self.active_listbox_widget = self.main_listbox
            self.status_bar.config(text="Listă: Toate")
        else:
            self.active_playlist_data = self.fav_playlist
            self.active_listbox_widget = self.fav_listbox
            self.status_bar.config(text="Listă: Favorite")

    def play_music(self):
        try:
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
                self.status_bar.config(text="Redare...")
                return

            selection = self.active_listbox_widget.curselection()
            if selection:
                index = selection[0]
                self.current_song_index = int(index)
            else:
                index = self.current_song_index

            if index < len(self.active_playlist_data):
                song_path = self.active_playlist_data[index]
                pygame.mixer.music.load(song_path)
                loops_val = -1 if self.is_looping else 0
                pygame.mixer.music.play(loops=loops_val)
                self.status_bar.config(text=f"Acum cântă: {os.path.basename(song_path)}")
                self.play_btn.config(text="▶")
            else:
                self.status_bar.config(text="Selectează o melodie")
        except Exception:
            self.status_bar.config(text="Eroare redare")

    def next_song(self):
        try:
            if self.is_shuffling and len(self.active_playlist_data) > 0:
                next_idx = random.randint(0, len(self.active_playlist_data) - 1)
            else:
                selection = self.active_listbox_widget.curselection()
                next_idx = (selection[0] + 1) if selection else (self.current_song_index + 1)

            if next_idx < len(self.active_playlist_data):
                self.play_song_at_index(next_idx)
            else:
                self.status_bar.config(text="Sfârșitul listei active")
        except Exception:
            pass

    def prev_song(self):
        try:
            selection = self.active_listbox_widget.curselection()
            prev_idx = (selection[0] - 1) if selection else (self.current_song_index - 1)
            if prev_idx >= 0:
                self.play_song_at_index(prev_idx)
            else:
                self.status_bar.config(text="Începutul listei")
        except Exception:
            pass

    def play_song_at_index(self, index):
        song_path = self.active_playlist_data[index]
        pygame.mixer.music.load(song_path)
        loops_val = -1 if self.is_looping else 0
        pygame.mixer.music.play(loops=loops_val)

        self.active_listbox_widget.selection_clear(0, tk.END)
        self.active_listbox_widget.activate(index)
        self.active_listbox_widget.selection_set(index, last=None)
        self.active_listbox_widget.see(index)
        self.current_song_index = index
        self.status_bar.config(text=f"Acum cântă: {os.path.basename(song_path)}")

    def add_song(self):
        song = filedialog.askopenfilename(initialdir='audio/', title="Alege o melodie",
                                          filetypes=(("mp3 Files", "*.mp3"),))
        if song:
            self.main_playlist.append(song)
            self.main_listbox.insert(tk.END, os.path.basename(song))

    def add_many_songs(self):
        songs = filedialog.askopenfilenames(initialdir='audio/', title="Alege melodii",
                                            filetypes=(("mp3 Files", "*.mp3"),))
        for song in songs:
            self.main_playlist.append(song)
            self.main_listbox.insert(tk.END, os.path.basename(song))

    def add_to_favorites(self):
        selection = self.main_listbox.curselection()
        if selection:
            song_path = self.main_playlist[selection[0]]
            if song_path not in self.fav_playlist:
                self.fav_playlist.append(song_path)
                self.fav_listbox.insert(tk.END, os.path.basename(song_path))
                self.status_bar.config(text="Adăugat la Favorite ❤")

    def remove_from_favorites(self):
        if self.tabs.index(self.tabs.select()) != 1: return
        selection = self.fav_listbox.curselection()
        if selection:
            idx = selection[0]
            del self.fav_playlist[idx]
            self.fav_listbox.delete(idx)
            self.status_bar.config(text="Șters din Favorite 💔")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.active_listbox_widget.selection_clear(0, tk.END)
        self.status_bar.config(text="Oprit")

    def pause_music(self):
        pygame.mixer.music.pause()
        self.paused = True
        self.status_bar.config(text="Pauză")

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()

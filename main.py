import tkinter as tk
from tkinter import filedialog
import pygame
import os

# --- CULORI ȘI STILURI (CONFIG) ---
COLOR_BG = "#1e1e1e"  # Background general
COLOR_FG = "#ffffff"  # Text principal
COLOR_BTN = "#2d2d2d"  # Background butoane
COLOR_BTN_HOVER = "#3e3e3e"  # Hover (simulat prin activebackground)
COLOR_ACCENT = "#1db954"  # Verde tip "Spotify" pentru Play/Listbox
COLOR_LISTBOX = "#121212"  # Background playlist
FONT_MAIN = ("Arial", 10)
FONT_BOLD = ("Arial", 10, "bold")
FONT_ICONS = ("Arial", 14)  # Font mai mare pentru simboluri


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python MP3 Player - Modern UI")
        self.root.geometry("600x450")
        self.root.configure(bg=COLOR_BG)  # Setare culoare fundal fereastră

        # --- STUDENT 1: Audio Setup ---
        pygame.mixer.init()
        self.paused = False
        self.current_song_index = 0
        self.playlist = []

        # --- HEADER (Titlu) ---
        title_label = tk.Label(root, text="My Music Library", bg=COLOR_BG, fg=COLOR_FG,
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=15)

        # --- STUDENT 2: GUI - Song List ---
        # Frame container pentru playlist ca să adăugăm un border subtil
        list_frame = tk.Frame(root, bg=COLOR_BG)
        list_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        self.playlist_box = tk.Listbox(
            list_frame,
            bg=COLOR_LISTBOX,
            fg=COLOR_FG,
            width=60,
            height=12,
            selectbackground=COLOR_ACCENT,
            selectforeground="white",
            bd=0,  # Fără border clasic
            highlightthickness=0,  # Fără highlight border la focus
            font=FONT_MAIN,
            activestyle="none"  # Elimină sublinierea elementului activ
        )
        self.playlist_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- CONTROL AREA ---
        # Un frame dedicat pentru controale jos
        control_area = tk.Frame(root, bg=COLOR_BG)
        control_area.pack(pady=20, fill=tk.X)

        # 1. Slider Volum (Mutat deasupra butoanelor pentru simetrie)
        self.volume_slider = tk.Scale(
            control_area,
            from_=0, to=1,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            bg=COLOR_BG,
            fg=COLOR_FG,
            troughcolor=COLOR_BTN,
            highlightthickness=0,
            bd=0,
            showvalue=0,  # Ascundem numerele, lăsăm doar slider-ul
            command=self.set_volume,
            length=150,
            label="Volume"
        )
        self.volume_slider.set(0.5)
        self.volume_slider.pack(side=tk.RIGHT, padx=20)

        # 2. Butoane (Centrate)
        # Folosim un frame interior pentru a centra butoanele
        btns_frame = tk.Frame(control_area, bg=COLOR_BG)
        btns_frame.pack(side=tk.TOP)

        # Dicționar pentru stilul comun al butoanelor
        btn_style = {
            "bg": COLOR_BTN,
            "fg": COLOR_FG,
            "activebackground": COLOR_ACCENT,
            "activeforeground": "white",
            "bd": 0,
            "relief": tk.FLAT,
            "font": FONT_ICONS,
            "width": 4,
            "cursor": "hand2"
        }

        # Definiție butoane cu simboluri Unicode
        # STUDENT 3 (Prev/Next) & STUDENT 2 (Play/Pause/Stop)
        self.prev_btn = tk.Button(btns_frame, text="⏮", command=self.prev_song, **btn_style)
        self.play_btn = tk.Button(btns_frame, text="▶", command=self.play_music, **btn_style)
        self.pause_btn = tk.Button(btns_frame, text="⏸", command=self.pause_music, **btn_style)
        self.stop_btn = tk.Button(btns_frame, text="⏹", command=self.stop_music, **btn_style)
        self.next_btn = tk.Button(btns_frame, text="⏭", command=self.next_song, **btn_style)

        # Butonul PLAY îl facem puțin diferit (accentuat)
        self.play_btn.config(bg=COLOR_ACCENT, fg="white", activebackground="#1ed760")

        # Grid Layout pentru butoane
        self.prev_btn.grid(row=0, column=0, padx=5)
        self.play_btn.grid(row=0, column=1, padx=5)
        self.pause_btn.grid(row=0, column=2, padx=5)
        self.stop_btn.grid(row=0, column=3, padx=5)
        self.next_btn.grid(row=0, column=4, padx=5)

        # --- MENIU (Student 3) ---
        # Modificăm meniul să arate standard, dar funcționalitatea rămâne
        menu = tk.Menu(root)
        root.config(menu=menu)
        add_song_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=add_song_menu)
        add_song_menu.add_command(label="Add One Song", command=self.add_song)
        add_song_menu.add_command(label="Add Many Songs", command=self.add_many_songs)
        add_song_menu.add_separator()
        add_song_menu.add_command(label="Exit", command=root.quit)

        # --- STUDENT 4: Status Bar ---
        self.status_bar = tk.Label(
            root,
            text="Welcome to Music Player",
            bd=0,
            relief=tk.FLAT,
            anchor=tk.W,
            bg=COLOR_BTN,
            fg="#aaaaaa",
            font=("Arial", 8),
            padx=10
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)

    # --- FUNCTIONS (Neschimbate ca logică, doar mici update-uri UI) ---

    def add_song(self):
        song = filedialog.askopenfilename(initialdir='audio/', title="Choose A Song",
                                          filetypes=(("mp3 Files", "*.mp3"),))
        if song:
            song_name = os.path.basename(song)
            self.playlist.append(song)
            self.playlist_box.insert(tk.END, song_name)

    def add_many_songs(self):
        songs = filedialog.askopenfilenames(initialdir='audio/', title="Choose Songs",
                                            filetypes=(("mp3 Files", "*.mp3"),))
        for song in songs:
            song_name = os.path.basename(song)
            self.playlist.append(song)
            self.playlist_box.insert(tk.END, song_name)

    def play_music(self):
        try:
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
                self.status_bar.config(text="Status: Playing...")
                return

            selection = self.playlist_box.curselection()
            if selection:
                index = selection[0]
                self.current_song_index = int(index)
            else:
                index = self.current_song_index

            if index < len(self.playlist):
                song_path = self.playlist[index]
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play(loops=0)

                # Actualizare sumară a UI
                song_name = os.path.basename(song_path)
                self.status_bar.config(text=f"Now Playing: {song_name}")
                self.play_btn.config(text="▶")  # Reset icon just in case
            else:
                self.status_bar.config(text="Playlist empty or no song selected")

        except Exception as e:
            print(e)
            self.status_bar.config(text="Error: Select a song first!")

    def pause_music(self):
        pygame.mixer.music.pause()
        self.paused = True
        self.status_bar.config(text="Status: Paused")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.playlist_box.selection_clear(0, tk.END)
        self.status_bar.config(text="Status: Stopped")

    def set_volume(self, val):
        volume = float(val)
        pygame.mixer.music.set_volume(volume)

    def next_song(self):
        try:
            current_selection = self.playlist_box.curselection()
            if current_selection:
                next_one = current_selection[0] + 1
            else:
                next_one = self.current_song_index + 1

            if next_one < len(self.playlist):
                song_path = self.playlist[next_one]
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play(loops=0)

                self.playlist_box.selection_clear(0, tk.END)
                self.playlist_box.activate(next_one)
                self.playlist_box.selection_set(next_one, last=None)
                self.current_song_index = next_one

                self.status_bar.config(text=f"Now Playing: {os.path.basename(song_path)}")
            else:
                self.status_bar.config(text="End of Playlist")
        except Exception:
            self.status_bar.config(text="Error playing next song")

    def prev_song(self):
        try:
            current_selection = self.playlist_box.curselection()
            if current_selection:
                prev_one = current_selection[0] - 1
            else:
                prev_one = self.current_song_index - 1

            if prev_one >= 0:
                song_path = self.playlist[prev_one]
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play(loops=0)

                self.playlist_box.selection_clear(0, tk.END)
                self.playlist_box.activate(prev_one)
                self.playlist_box.selection_set(prev_one, last=None)
                self.current_song_index = prev_one

                self.status_bar.config(text=f"Now Playing: {os.path.basename(song_path)}")
            else:
                self.status_bar.config(text="Start of Playlist")
        except Exception:
            self.status_bar.config(text="Error playing previous song")


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
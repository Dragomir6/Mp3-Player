import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
import random  # Avem nevoie de asta pentru Shuffle

# --- CULORI ȘI STILURI (CONFIG) ---
COLOR_BG = "#1e1e1e"
COLOR_FG = "#ffffff"
COLOR_BTN = "#2d2d2d"
COLOR_ACCENT = "#1db954"  # Verde (Activ)
COLOR_FAV = "#e91e63"
COLOR_REMOVE = "#ff5252"
COLOR_LISTBOX = "#121212"
COLOR_DISABLED = "#555555"  # Culoare pentru starea inactivă a butoanelor Loop/Shuffle

FONT_MAIN = ("Arial", 10)
FONT_ICONS = ("Arial", 14)


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python MP3 Player - Complete")
        self.root.geometry("700x500")
        self.root.configure(bg=COLOR_BG)

        # --- AUDIO SETUP ---
        pygame.mixer.init()
        self.paused = False
        self.current_song_index = 0

        # State Variables (Noi)
        self.is_looping = False
        self.is_shuffling = False

        # Liste de date
        self.main_playlist = []
        self.fav_playlist = []

        self.active_playlist_data = self.main_playlist
        self.active_listbox_widget = None

        # --- STYLE TABS ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_BTN, foreground="white", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", COLOR_ACCENT)], foreground=[("selected", "white")])

        # --- HEADER ---
        title_label = tk.Label(root, text="My Music Library", bg=COLOR_BG, fg=COLOR_FG,
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # --- TABS AREA ---
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        self.tab1 = tk.Frame(self.tabs, bg=COLOR_BG)
        self.tab2 = tk.Frame(self.tabs, bg=COLOR_BG)
        self.tabs.add(self.tab1, text="🎵 Toate Melodiile")
        self.tabs.add(self.tab2, text="❤ Favorite")

        self.main_listbox = self.create_listbox(self.tab1)
        self.main_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fav_listbox = self.create_listbox(self.tab2)
        self.fav_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.active_listbox_widget = self.main_listbox
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # --- CONTROL AREA ---
        control_area = tk.Frame(root, bg=COLOR_BG)
        control_area.pack(pady=15, fill=tk.X)

        # Slider Volum
        self.volume_slider = tk.Scale(
            control_area, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL,
            bg=COLOR_BG, fg=COLOR_FG, troughcolor=COLOR_BTN, highlightthickness=0, bd=0,
            showvalue=0, command=self.set_volume, length=100, label="Volum"
        )
        self.volume_slider.set(0.5)
        self.volume_slider.pack(side=tk.RIGHT, padx=20)

        # Frame Butoane
        btns_frame = tk.Frame(control_area, bg=COLOR_BG)
        btns_frame.pack(side=tk.TOP)

        btn_style = {
            "bg": COLOR_BTN, "fg": COLOR_FG, "activebackground": COLOR_ACCENT,
            "activeforeground": "white", "bd": 0, "relief": tk.FLAT,
            "font": FONT_ICONS, "width": 4, "cursor": "hand2"
        }

        # --- DEFINIRE BUTOANE ---
        # 1. Favorite
        self.fav_add_btn = tk.Button(btns_frame, text="❤", command=self.add_to_favorites, **btn_style)
        self.fav_add_btn.config(activebackground=COLOR_FAV, fg=COLOR_FAV)

        self.fav_remove_btn = tk.Button(btns_frame, text="💔", command=self.remove_from_favorites, **btn_style)
        self.fav_remove_btn.config(activebackground=COLOR_REMOVE, fg="#aaaaaa")

        # 2. Control Playback & Moduri (Shuffle/Loop)
        self.shuffle_btn = tk.Button(btns_frame, text="🔀", command=self.toggle_shuffle, **btn_style)
        self.shuffle_btn.config(fg=COLOR_DISABLED)  # Default inactiv

        self.prev_btn = tk.Button(btns_frame, text="⏮", command=self.prev_song, **btn_style)
        self.play_btn = tk.Button(btns_frame, text="▶", command=self.play_music, **btn_style)
        self.pause_btn = tk.Button(btns_frame, text="⏸", command=self.pause_music, **btn_style)
        self.stop_btn = tk.Button(btns_frame, text="⏹", command=self.stop_music, **btn_style)
        self.next_btn = tk.Button(btns_frame, text="⏭", command=self.next_song, **btn_style)

        self.loop_btn = tk.Button(btns_frame, text="🔁", command=self.toggle_loop, **btn_style)
        self.loop_btn.config(fg=COLOR_DISABLED)  # Default inactiv

        self.play_btn.config(bg=COLOR_ACCENT, fg="white")

        # --- GRID LAYOUT ---
        # Favorite Group
        self.fav_add_btn.grid(row=0, column=0, padx=(0, 2))
        self.fav_remove_btn.grid(row=0, column=1, padx=(0, 20))

        # Playback Group
        self.shuffle_btn.grid(row=0, column=2, padx=5)  # Shuffle la stânga controalelor
        self.prev_btn.grid(row=0, column=3, padx=5)
        self.play_btn.grid(row=0, column=4, padx=5)
        self.pause_btn.grid(row=0, column=5, padx=5)
        self.stop_btn.grid(row=0, column=6, padx=5)
        self.next_btn.grid(row=0, column=7, padx=5)
        self.loop_btn.grid(row=0, column=8, padx=5)  # Loop la dreapta controalelor

        # --- MENIU ---
        menu = tk.Menu(root)
        root.config(menu=menu)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Fișier", menu=file_menu)
        file_menu.add_command(label="Adaugă Melodie", command=self.add_song)
        file_menu.add_command(label="Adaugă Folder", command=self.add_many_songs)
        file_menu.add_separator()
        file_menu.add_command(label="Ieșire", command=root.quit)

        # --- STATUS BAR ---
        self.status_bar = tk.Label(root, text="Așteptare...", bd=0, relief=tk.FLAT, anchor=tk.W,
                                   bg=COLOR_BTN, fg="#aaaaaa", font=("Arial", 9), padx=10)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)

    # --- UI HELPERS ---
    def create_listbox(self, parent):
        return tk.Listbox(parent, bg=COLOR_LISTBOX, fg=COLOR_FG, width=60, height=10,
                          selectbackground=COLOR_ACCENT, selectforeground="white",
                          bd=0, highlightthickness=0, font=FONT_MAIN, activestyle="none")

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

    # --- NOILE FUNCȚII PENTRU LOOP ȘI SHUFFLE ---

    def toggle_loop(self):
        self.is_looping = not self.is_looping
        if self.is_looping:
            self.loop_btn.config(fg=COLOR_ACCENT)  # Se face verde
            self.status_bar.config(text="Loop: PORNIT (Melodia se va repeta)")
            # Dacă muzica deja cântă, trebuie să îi spunem lui pygame să o pună pe repeat
            if pygame.mixer.music.get_busy():
                # Din păcate pygame nu permite schimbarea loop-ului on-the-fly fără restart,
                # dar va avea efect la următoarea apăsare de Play.
                pass
        else:
            self.loop_btn.config(fg=COLOR_DISABLED)  # Se face gri
            self.status_bar.config(text="Loop: OPRIT")

    def toggle_shuffle(self):
        self.is_shuffling = not self.is_shuffling
        if self.is_shuffling:
            self.shuffle_btn.config(fg=COLOR_ACCENT)  # Se face verde
            self.status_bar.config(text="Shuffle: PORNIT")
        else:
            self.shuffle_btn.config(fg=COLOR_DISABLED)  # Se face gri
            self.status_bar.config(text="Shuffle: OPRIT")

    # --- FUNCTIONALITATE AUDIO ---

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

                # AICI ESTE MODIFICAREA PENTRU LOOP
                # loops = -1 înseamnă infinit, loops = 0 înseamnă o singură dată
                loops_val = -1 if self.is_looping else 0
                pygame.mixer.music.play(loops=loops_val)

                song_name = os.path.basename(song_path)
                self.status_bar.config(text=f"Acum cântă: {song_name}")
                self.play_btn.config(text="▶")
            else:
                self.status_bar.config(text="Selectează o melodie")

        except Exception as e:
            self.status_bar.config(text="Eroare redare")

    def next_song(self):
        try:
            # LOGICA PENTRU SHUFFLE
            if self.is_shuffling and len(self.active_playlist_data) > 0:
                # Alegem un index complet aleatoriu
                next_idx = random.randint(0, len(self.active_playlist_data) - 1)
            else:
                # Comportament normal (următoarea)
                selection = self.active_listbox_widget.curselection()
                if selection:
                    next_idx = selection[0] + 1
                else:
                    next_idx = self.current_song_index + 1

            if next_idx < len(self.active_playlist_data):
                song_path = self.active_playlist_data[next_idx]
                pygame.mixer.music.load(song_path)

                # Verificăm din nou loop-ul la schimbarea melodiei
                loops_val = -1 if self.is_looping else 0
                pygame.mixer.music.play(loops=loops_val)

                # Update UI Selection
                self.active_listbox_widget.selection_clear(0, tk.END)
                self.active_listbox_widget.activate(next_idx)
                self.active_listbox_widget.selection_set(next_idx, last=None)
                self.active_listbox_widget.see(next_idx)  # Asigură că lista face scroll la melodie

                self.current_song_index = next_idx
                self.status_bar.config(text=f"Acum cântă: {os.path.basename(song_path)}")
            else:
                # Dacă am ajuns la final și shuffle nu e activ
                self.status_bar.config(text="Sfârșitul listei active")
                # Opțional: Poți reseta la început
                # self.current_song_index = 0
        except Exception:
            pass

    def prev_song(self):
        # La prev, de obicei shuffle nu se aplică (te duce la piesa anterioară logică sau istorică)
        # Pentru simplitate, păstrăm ordinea listei aici.
        try:
            selection = self.active_listbox_widget.curselection()
            if selection:
                prev_idx = selection[0] - 1
            else:
                prev_idx = self.current_song_index - 1

            if prev_idx >= 0:
                song_path = self.active_playlist_data[prev_idx]
                pygame.mixer.music.load(song_path)

                loops_val = -1 if self.is_looping else 0
                pygame.mixer.music.play(loops=loops_val)

                self.active_listbox_widget.selection_clear(0, tk.END)
                self.active_listbox_widget.activate(prev_idx)
                self.active_listbox_widget.selection_set(prev_idx, last=None)
                self.active_listbox_widget.see(prev_idx)

                self.current_song_index = prev_idx
                self.status_bar.config(text=f"Acum cântă: {os.path.basename(song_path)}")
            else:
                self.status_bar.config(text="Începutul listei")
        except Exception:
            pass

    # --- RESTUL FUNCTIILOR (ADD/REMOVE) ---
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
            index = selection[0]
            song_path = self.main_playlist[index]
            if song_path not in self.fav_playlist:
                self.fav_playlist.append(song_path)
                self.fav_listbox.insert(tk.END, os.path.basename(song_path))
                self.status_bar.config(text="Adăugat la Favorite ❤")

    def remove_from_favorites(self):
        if self.tabs.index(self.tabs.select()) != 1:
            self.status_bar.config(text="Mergi în tab-ul 'Favorite' pentru a șterge!")
            return
        selection = self.fav_listbox.curselection()
        if selection:
            index = selection[0]
            del self.fav_playlist[index]
            self.fav_listbox.delete(index)
            self.status_bar.config(text="Șters din Favorite 💔")

    def pause_music(self):
        pygame.mixer.music.pause()
        self.paused = True
        self.status_bar.config(text="Pauză")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.active_listbox_widget.selection_clear(0, tk.END)
        self.status_bar.config(text="Oprit")

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
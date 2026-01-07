import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
import pygame
import os
import random
import pickle
import time

# Încercăm să importăm mutagen pentru durată.
try:
    from mutagen.mp3 import MP3

    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

# --- CONFIGURARE TEME ---
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

FONT_MAIN = ("Arial", 10)
FONT_ICONS = ("Segoe UI Symbol", 14)


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python MP3 Player - Final v4")
        self.root.geometry("800x650")

        # --- SETUP AUDIO ---
        try:
            pygame.mixer.quit()
        except:
            pass
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # Variabile
        self.paused = False
        self.current_song_index = 0
        self.is_looping = False
        self.is_shuffling = False
        self.song_length = 0
        self.is_dragging = False
        self.sleep_timer_id = None

        self.main_playlist = []
        self.fav_playlist = []
        self.active_playlist_data = self.main_playlist

        if not os.path.exists("saved_playlists"):
            os.makedirs("saved_playlists")

        # UI Lists
        self.colored_frames = []
        self.colored_labels = []
        self.colored_buttons = []

        self.current_theme = THEMES["Dark Mode (Spotify)"]

        self.setup_ui()
        self.apply_theme("Dark Mode (Spotify)")
        self.refresh_saved_playlists()

        # Start Timer
        self.update_song_timer()

    def setup_ui(self):
        # Header
        self.title_label = tk.Label(self.root, text="Music Player", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=(15, 0))
        self.colored_labels.append(self.title_label)

        # Timer
        self.time_label = tk.Label(self.root, text="00:00 / 00:00", font=("Arial", 12, "bold"))
        self.time_label.pack(pady=(5, 10))
        self.colored_labels.append(self.time_label)

        # Tabs
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        self.tab1 = tk.Frame(self.tabs)
        self.tab2 = tk.Frame(self.tabs)
        self.tab3 = tk.Frame(self.tabs)
        self.colored_frames.extend([self.tab1, self.tab2, self.tab3])

        self.tabs.add(self.tab1, text="🎵 Melodii")
        self.tabs.add(self.tab2, text="❤ Favorite")
        self.tabs.add(self.tab3, text="💾 Playlist-uri")
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Listboxes
        self.main_listbox = self.create_listbox(self.tab1)
        self.main_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.fav_listbox = self.create_listbox(self.tab2)
        self.fav_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.playlists_listbox = self.create_listbox(self.tab3)
        self.playlists_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Butoane Playlist (Tab 3)
        pl_btn_frame = tk.Frame(self.tab3)
        pl_btn_frame.pack(fill=tk.X, pady=5)
        self.colored_frames.append(pl_btn_frame)

        load_btn = tk.Button(pl_btn_frame, text="Încarcă", command=self.load_selected_playlist_from_tab)
        load_btn.pack(side=tk.LEFT, padx=20)
        self.colored_buttons.append(load_btn)

        del_btn = tk.Button(pl_btn_frame, text="Șterge Playlist-ul", command=self.delete_saved_playlist, fg="red",
                            bg="#222")
        del_btn.pack(side=tk.RIGHT, padx=20)

        self.active_listbox_widget = self.main_listbox

        # Control Area
        self.control_area = tk.Frame(self.root)
        self.control_area.pack(pady=5, fill=tk.X, padx=20)
        self.colored_frames.append(self.control_area)

        # Slider Progres
        self.progress_scale = tk.Scale(self.control_area, from_=0, to=100, orient=tk.HORIZONTAL, showvalue=0,
                                       length=600, bd=0, highlightthickness=0, relief=tk.FLAT)
        self.progress_scale.pack(fill=tk.X, pady=(0, 10))
        self.progress_scale.bind("<ButtonPress-1>", self.start_slide)
        self.progress_scale.bind("<ButtonRelease-1>", self.stop_slide)

        # Slider Volum
        self.volume_slider = tk.Scale(self.control_area, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL, bd=0,
                                      highlightthickness=0, showvalue=0, length=100, label="Volum",
                                      command=self.set_volume)
        self.volume_slider.set(0.5)
        self.volume_slider.pack(side=tk.RIGHT, padx=10)

        # Butoane Player
        self.btns_frame = tk.Frame(self.control_area)
        self.btns_frame.pack(side=tk.TOP)
        self.colored_frames.append(self.btns_frame)

        btn_conf = {"bd": 0, "relief": tk.FLAT, "font": FONT_ICONS, "width": 4, "cursor": "hand2"}

        self.fav_add_btn = tk.Button(self.btns_frame, text="❤", command=self.add_to_favorites, **btn_conf)
        self.fav_remove_btn = tk.Button(self.btns_frame, text="💔", command=self.remove_from_favorites, **btn_conf)

        self.del_song_btn = tk.Button(self.btns_frame, text="🗑", command=self.remove_selected_song, **btn_conf)

        self.shuffle_btn = tk.Button(self.btns_frame, text="🔀", command=self.toggle_shuffle, **btn_conf)
        self.prev_btn = tk.Button(self.btns_frame, text="⏮", command=self.prev_song, **btn_conf)
        self.play_btn = tk.Button(self.btns_frame, text="▶", command=self.play_music, **btn_conf)
        self.stop_btn = tk.Button(self.btns_frame, text="⏹", command=self.stop_music, **btn_conf)
        self.next_btn = tk.Button(self.btns_frame, text="⏭", command=self.next_song, **btn_conf)
        self.loop_btn = tk.Button(self.btns_frame, text="🔁", command=self.toggle_loop, **btn_conf)

        # Lista butoane colorate
        self.colored_buttons.extend([
            self.prev_btn, self.stop_btn, self.next_btn,
            self.fav_add_btn, self.fav_remove_btn, self.del_song_btn,
            self.shuffle_btn, self.loop_btn
        ])

        # Grid Layout
        self.fav_add_btn.grid(row=0, column=0, padx=2)
        self.fav_remove_btn.grid(row=0, column=1, padx=2)
        self.del_song_btn.grid(row=0, column=2, padx=10)

        self.shuffle_btn.grid(row=0, column=3, padx=5)
        self.prev_btn.grid(row=0, column=4, padx=5)
        self.play_btn.grid(row=0, column=5, padx=5)
        self.stop_btn.grid(row=0, column=6, padx=5)
        self.next_btn.grid(row=0, column=7, padx=5)
        self.loop_btn.grid(row=0, column=8, padx=5)

        # Status Bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=0, relief=tk.FLAT, anchor=tk.W, font=("Arial", 9),
                                   padx=10)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)

        self.create_menu()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Fișier", menu=file_menu)
        file_menu.add_command(label="Adaugă Melodii", command=self.add_many_songs)
        file_menu.add_separator()
        file_menu.add_command(label="Salvează Playlist", command=self.save_playlist_dialog)
        file_menu.add_command(label="Ieșire", command=self.root.quit)

        theme_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="🎨 Teme", menu=theme_menu)
        for t in THEMES.keys():
            theme_menu.add_command(label=t, command=lambda x=t: self.apply_theme(x))

        sleep_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="⏰ Ceas", menu=sleep_menu)
        sleep_menu.add_command(label="5 min", command=lambda: self.set_sleep_timer(5))
        sleep_menu.add_command(label="10 min", command=lambda: self.set_sleep_timer(10))
        sleep_menu.add_command(label="30 min", command=lambda: self.set_sleep_timer(30))
        sleep_menu.add_command(label="60 min", command=lambda: self.set_sleep_timer(60))
        sleep_menu.add_separator()
        sleep_menu.add_command(label="Anulează", command=lambda: self.set_sleep_timer(0))

    def create_listbox(self, parent):
        return tk.Listbox(parent, width=60, height=10, bd=0, highlightthickness=0, font=FONT_MAIN, activestyle="none")

    def remove_selected_song(self):
        try:
            current_tab = self.tabs.index(self.tabs.select())

            if current_tab == 0:
                target_list = self.main_playlist
                target_box = self.main_listbox
            elif current_tab == 1:
                target_list = self.fav_playlist
                target_box = self.fav_listbox
            else:
                messagebox.showwarning("Info", "Selectează o melodie din tab-ul Melodii sau Favorite.")
                return

            selection = target_box.curselection()
            if not selection:
                messagebox.showwarning("Info", "Selectează o melodie de șters!")
                return

            index = selection[0]
            is_active_list = (self.active_playlist_data == target_list)

            if is_active_list and index == self.current_song_index:
                self.stop_music()

            del target_list[index]
            target_box.delete(index)

            if is_active_list and index < self.current_song_index:
                self.current_song_index -= 1

            self.status_bar.config(text="Melodie ștearsă.")

        except Exception as e:
            print(f"Eroare ștergere: {e}")

    def play_music(self):
        try:
            selection = self.active_listbox_widget.curselection()
            if selection:
                selected_index = int(selection[0])
                if selected_index != self.current_song_index:
                    self.play_song_at_index(selected_index)
                    return

            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
                self.play_btn.config(text="⏸")
                self.status_bar.config(text="Redare...")
                return

            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.paused = True
                self.play_btn.config(text="▶")
                self.status_bar.config(text="Pauză")
                return

            if not selection and len(self.active_playlist_data) > 0:
                self.play_song_at_index(0)
            elif selection:
                self.play_song_at_index(int(selection[0]))
            else:
                messagebox.showinfo("Info", "Adaugă melodii în listă!")
        except Exception as e:
            self.status_bar.config(text=f"Eroare: {e}")

    def play_song_at_index(self, index):
        try:
            song_path = self.active_playlist_data[index]
            pygame.mixer.music.load(song_path)

            self.song_length = 0
            if HAS_MUTAGEN:
                try:
                    audio = MP3(song_path)
                    self.song_length = audio.info.length
                except:
                    pass

            self.progress_scale.config(to=self.song_length)
            self.progress_scale.set(0)

            pygame.mixer.music.play(loops=0)

            self.current_song_index = index
            self.paused = False
            self.play_btn.config(text="⏸")
            self.status_bar.config(text=f"Playing: {os.path.basename(song_path)}")

            self.active_listbox_widget.selection_clear(0, tk.END)
            self.active_listbox_widget.activate(index)
            self.active_listbox_widget.selection_set(index, last=None)
            self.active_listbox_widget.see(index)
        except Exception as e:
            messagebox.showerror("Eroare Fișier", f"Nu pot reda fișierul:\n{e}")

    def start_slide(self, event):
        self.is_dragging = True

    def stop_slide(self, event):
        self.is_dragging = False
        val = self.progress_scale.get()
        if self.active_playlist_data:
            try:
                path = self.active_playlist_data[self.current_song_index]
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(loops=0, start=val)
                self.paused = False
                self.play_btn.config(text="⏸")
            except:
                pass

    def update_song_timer(self):
        if pygame.mixer.music.get_busy() and not self.paused and not self.is_dragging:
            current_val = self.progress_scale.get()
            new_val = current_val + 1
            if new_val <= self.song_length:
                self.progress_scale.set(new_val)
                cur_min = int(new_val // 60)
                cur_sec = int(new_val % 60)
                tot_min = int(self.song_length // 60)
                tot_sec = int(self.song_length % 60)
                self.time_label.config(text=f"{cur_min:02}:{cur_sec:02} / {tot_min:02}:{tot_sec:02}")

        elif not self.paused and self.active_playlist_data and self.song_length > 0:
            if self.progress_scale.get() >= self.song_length - 1:
                if self.is_looping:
                    self.play_song_at_index(self.current_song_index)
                else:
                    self.next_song()

        self.root.after(1000, self.update_song_timer)

    def stop_music(self):
        pygame.mixer.music.stop()
        self.paused = False
        self.play_btn.config(text="▶")
        self.progress_scale.set(0)
        self.time_label.config(text="00:00 / 00:00")
        self.status_bar.config(text="Oprit")

    def next_song(self):
        try:
            if self.is_shuffling:
                idx = random.randint(0, len(self.active_playlist_data) - 1)
            else:
                idx = self.current_song_index + 1

            # --- MODIFICARE AICI: Resetăm indexul la 0 dacă depășește lungimea ---
            if idx >= len(self.active_playlist_data):
                idx = 0
            # ---------------------------------------------------------------------

            self.play_song_at_index(idx)
        except:
            pass

    def prev_song(self):
        try:
            idx = self.current_song_index - 1
            if idx >= 0:
                self.play_song_at_index(idx)
        except:
            pass

    def toggle_shuffle(self):
        self.is_shuffling = not self.is_shuffling
        self.update_toggle_color()

    def toggle_loop(self):
        self.is_looping = not self.is_looping
        self.update_toggle_color()

    def update_toggle_color(self):
        t = self.current_theme
        self.shuffle_btn.config(fg=t["accent"] if self.is_shuffling else t["fg"])
        self.loop_btn.config(fg=t["accent"] if self.is_looping else t["fg"])

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))

    def add_song(self):
        f = filedialog.askopenfilename(filetypes=(("mp3", "*.mp3"),))
        if f:
            self.main_playlist.append(f)
            self.main_listbox.insert(tk.END, os.path.basename(f))

    def add_many_songs(self):
        fs = filedialog.askopenfilenames(filetypes=(("mp3", "*.mp3"),))
        for f in fs:
            self.main_playlist.append(f)
            self.main_listbox.insert(tk.END, os.path.basename(f))

    def add_to_favorites(self):
        sel = self.main_listbox.curselection()
        if sel:
            path = self.main_playlist[sel[0]]
            if path not in self.fav_playlist:
                self.fav_playlist.append(path)
                self.fav_listbox.insert(tk.END, os.path.basename(path))

    def remove_from_favorites(self):
        if self.tabs.index(self.tabs.select()) == 1:
            sel = self.fav_listbox.curselection()
            if sel:
                del self.fav_playlist[sel[0]]
                self.fav_listbox.delete(sel[0])

    def save_playlist_dialog(self):
        if not self.main_playlist: return
        name = simpledialog.askstring("Nume", "Nume Playlist:")
        if name:
            with open(f"saved_playlists/{name}.dat", "wb") as f:
                pickle.dump(self.main_playlist, f)
            self.refresh_saved_playlists()

    def refresh_saved_playlists(self):
        self.playlists_listbox.delete(0, tk.END)
        for f in os.listdir("saved_playlists"):
            if f.endswith(".dat"):
                self.playlists_listbox.insert(tk.END, f.replace(".dat", ""))

    def load_selected_playlist_from_tab(self):
        sel = self.playlists_listbox.curselection()
        if sel:
            name = self.playlists_listbox.get(sel[0])
            with open(f"saved_playlists/{name}.dat", "rb") as f:
                self.main_playlist = pickle.load(f)
            self.main_listbox.delete(0, tk.END)
            for s in self.main_playlist:
                self.main_listbox.insert(tk.END, os.path.basename(s))
            self.tabs.select(self.tab1)
            self.active_playlist_data = self.main_playlist

    def delete_saved_playlist(self):
        sel = self.playlists_listbox.curselection()
        if sel:
            name = self.playlists_listbox.get(sel[0])
            if messagebox.askyesno("Confirm", "Stergi?"):
                os.remove(f"saved_playlists/{name}.dat")
                self.refresh_saved_playlists()

    def set_sleep_timer(self, minutes):
        if self.sleep_timer_id:
            self.root.after_cancel(self.sleep_timer_id)
        if minutes > 0:
            self.sleep_timer_id = self.root.after(minutes * 60 * 1000, self.stop_music)
            self.status_bar.config(text=f"Sleep timer setat: {minutes} min")
            messagebox.showinfo("Sleep Timer", f"Muzica se va opri în {minutes} minute.")
        else:
            self.status_bar.config(text="Sleep timer anulat")
            messagebox.showinfo("Sleep Timer", "Timer anulat.")

    def on_tab_change(self, event):
        idx = self.tabs.index(self.tabs.select())
        if idx == 0:
            self.active_playlist_data = self.main_playlist
            self.active_listbox_widget = self.main_listbox
        elif idx == 1:
            self.active_playlist_data = self.fav_playlist
            self.active_listbox_widget = self.fav_listbox

    def apply_theme(self, name):
        t = THEMES[name]
        self.current_theme = t
        self.root.config(bg=t["bg"])
        for f in self.colored_frames: f.config(bg=t["bg"])
        for l in self.colored_labels: l.config(bg=t["bg"], fg=t["fg"])
        for lb in [self.main_listbox, self.fav_listbox, self.playlists_listbox]:
            lb.config(bg=t["list_bg"], fg=t["list_fg"], selectbackground=t["accent"])

        self.style.configure("TNotebook", background=t["bg"])
        self.style.configure("TNotebook.Tab", background=t["bg"], foreground=t["fg"])
        self.style.map("TNotebook.Tab", background=[("selected", t["accent"])], foreground=[("selected", "white")])

        self.progress_scale.config(bg=t["bg"], fg=t["accent"], troughcolor=t["list_bg"], activebackground=t["accent"])
        self.volume_slider.config(bg=t["bg"], fg=t["fg"], troughcolor=t["list_bg"])
        self.status_bar.config(bg=t["list_bg"], fg=t["fg"])

        for btn in self.colored_buttons:
            btn.config(bg=t["bg"], fg=t["fg"], activebackground=t["bg"], activeforeground=t["accent"])

        self.play_btn.config(bg=t["accent"], fg="white")
        self.update_toggle_color()


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
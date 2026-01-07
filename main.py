import tkinter as tk
from tkinter import filedialog
import pygame
import os


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python MP3 Player - Group Project")
        self.root.geometry("500x400")

        # --- STUDENT 1: Audio Setup ---
        # Initialize Pygame Mixer
        pygame.mixer.init()
        # State variables
        self.paused = False
        self.current_song_index = 0
        self.playlist = []

        # --- STUDENT 2: GUI - Song List ---
        # Frame for the playlist
        self.playlist_box = tk.Listbox(root, bg="black", fg="white", width=60, selectbackground="gray",
                                       selectforeground="black")
        self.playlist_box.pack(pady=20)

        # --- STUDENT 2: GUI - Buttons & Slider ---
        # Control Frame
        controls_frame = tk.Frame(root)
        controls_frame.pack()

        # Button Images (using text for simplicity, but images can be added here)
        play_btn = tk.Button(controls_frame, text="PLAY", command=self.play_music, width=10)
        pause_btn = tk.Button(controls_frame, text="PAUSE", command=self.pause_music, width=10)
        stop_btn = tk.Button(controls_frame, text="STOP", command=self.stop_music, width=10)

        # Grid layout for buttons
        play_btn.grid(row=0, column=1, padx=10)
        pause_btn.grid(row=0, column=2, padx=10)
        stop_btn.grid(row=0, column=3, padx=10)

        # Volume Slider (Student 2)
        self.volume_slider = tk.Scale(root, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL, label="Volume",
                                      command=self.set_volume)
        self.volume_slider.set(0.5)  # Default 50%
        self.volume_slider.pack(pady=10)

        # --- STUDENT 3: Playlist Management ---
        # Navigation Buttons
        prev_btn = tk.Button(controls_frame, text="<< PREV", command=self.prev_song, width=10)
        next_btn = tk.Button(controls_frame, text="NEXT >>", command=self.next_song, width=10)

        prev_btn.grid(row=0, column=0, padx=10)
        next_btn.grid(row=0, column=4, padx=10)

        # Menu to add songs
        menu = tk.Menu(root)
        root.config(menu=menu)
        add_song_menu = tk.Menu(menu)
        menu.add_cascade(label="Add Songs", menu=add_song_menu)
        add_song_menu.add_command(label="Add One Song", command=self.add_song)
        add_song_menu.add_command(label="Add Many Songs", command=self.add_many_songs)

        # --- STUDENT 4: Status/Extras ---
        # Status Bar
        self.status_bar = tk.Label(root, text="Welcome to Music Player", bd=1, relief=tk.SUNKEN, anchor=tk.E)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)

    # --- FUNCTIONS ---

    # Student 3 Functionality
    def add_song(self):
        song = filedialog.askopenfilename(initialdir='audio/', title="Choose A Song",
                                          filetypes=(("mp3 Files", "*.mp3"),))
        if song:
            # Strip out the directory info to show just the name
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

    # Student 1 Functionality
    def play_music(self):
        try:
            # If paused, unpause
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
                self.status_bar.config(text="Playing...")
                return

            # Get selected song index
            selection = self.playlist_box.curselection()
            if selection:
                index = selection[0]
                self.current_song_index = int(index)
            else:
                index = self.current_song_index

            song_path = self.playlist[index]

            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play(loops=0)
            self.status_bar.config(text=f"Playing: {os.path.basename(song_path)}")
        except Exception as e:
            print("Select a song first!")

    def pause_music(self):
        pygame.mixer.music.pause()
        self.paused = True
        self.status_bar.config(text="Paused")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.playlist_box.selection_clear(tk.ACTIVE)
        self.status_bar.config(text="Stopped")

    def set_volume(self, val):
        volume = float(val)
        pygame.mixer.music.set_volume(volume)

    # Student 3 Functionality (Navigation)
    def next_song(self):
        try:
            next_one = self.playlist_box.curselection()[0] + 1
            song_path = self.playlist[next_one]

            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play(loops=0)

            # Move selection bar
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.activate(next_one)
            self.playlist_box.selection_set(next_one, last=None)
            self.current_song_index = next_one
        except:
            self.status_bar.config(text="End of Playlist")

    def prev_song(self):
        try:
            prev_one = self.playlist_box.curselection()[0] - 1
            song_path = self.playlist[prev_one]

            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play(loops=0)

            # Move selection bar
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.activate(prev_one)
            self.playlist_box.selection_set(prev_one, last=None)
            self.current_song_index = prev_one
        except:
            self.status_bar.config(text="Start of Playlist")


# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
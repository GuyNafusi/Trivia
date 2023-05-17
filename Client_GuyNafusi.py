import tkinter as tk
from tkinter import font
import socket
import threading
import os

try:
    import pygame
except ImportError:
    os.system('python -m pip install requests')
import pygame

CLIENT_IP = '127.0.0.1'
PORT = 5555
X = 800
Y = 600
MAX_LEN = 1024
HELP_IMG_LOC = r"instruct.png"
START_IMG_LOC = r"button_start.png"
REPLAY_IMG_LOC = r"replay_button.png"
EXIT_IMG_LOC = r"button_exit.png"
FIRST_SCREEN_IMG_LOC = r"first_s.png"
QA_IMG_LOC = r"qabg.png"
SEND_IMG_LOC = r"send_ans.png"
MUSIC_LOC = r"backmusic.mp3"
HELP_BUTTON_IMG_LOC = r"button_help.png"


def send_to_server():
    """ send an answer to the server and disables the answer button"""
    if len(entry.get()) == 0:
        client_socket.send("None".encode())
    else:
        client_socket.send(entry.get().encode())
    entry.delete(0, tk.END)
    entry['state'] = tk.DISABLED
    answer_button.config(state=tk.DISABLED)


def replay_game():
    global again_game_thread
    """closes a clients game root and socket and open a new game"""
    try:
        client_socket.close()
        my_game.destroy()
    except Exception as e:
        print(e)
    again_game_thread = threading.Thread(target=open_game)
    again_game_thread.start()


def open_help_menu():
    """configures the instructions page"""
    global help_img

    help_menu = tk.Toplevel()
    help_menu.title("Help menu")
    help_menu.resizable(width=tk.FALSE, height=tk.FALSE)
    help_menu.geometry("%dx%d" % (X, Y))
    help_menu.protocol("WM_DELETE_WINDOW", help_menu.destroy)

    help_img = tk.PhotoImage(file=HELP_IMG_LOC)
    # root has no image argument, so use a label as a panel
    panel = tk.Label(help_menu, image=help_img)
    panel.pack(fill='both', expand='yes')
    return_button = tk.Button(help_menu, image=button_exit_img, command=help_menu.destroy)
    return_button.place(x=740, y=540, anchor="center")


def exit_game():
    """exits the game properly when used"""
    try:
        client_socket.close()
        py_music.stop()
        my_game.destroy()
        root.destroy()
    except NameError:
        print("server wasnt up error/name error")
    print("Exists")
    os.abort()


def game_settings():
    """defines the game page"""
    global my_game
    global bg_image
    global answer_button
    global entry
    global txt
    global send_ans_img
    global replay_img
    my_game = tk.Toplevel()
    my_game.title("The Game")
    my_game.resizable(width=tk.FALSE, height=tk.FALSE)
    my_game.geometry("%dx%d" % (X, Y))
    my_game.protocol("WM_DELETE_WINDOW", exit_game)
    bg_image = tk.PhotoImage(file=QA_IMG_LOC)
    send_ans_img = tk.PhotoImage(file=SEND_IMG_LOC)
    replay_img = tk.PhotoImage(file=REPLAY_IMG_LOC)
    # root has no image argument, so use a label as a panel
    img_label = tk.Label(my_game, image=bg_image)
    img_label.pack(fill='both', expand='yes')
    music_scale = tk.Scale(my_game, orient=tk.HORIZONTAL, from_=0, to=100, variable=intVr, command=bg_volume,
                           length=100)
    music_scale.place(x=5, y=5)
    exit_button = tk.Button(my_game, image=button_exit_img, command=exit_game)
    exit_button.place(x=400, y=490, anchor="center")
    fnt = font.Font(family="Helvetica", size=10, weight=font.BOLD)
    txt = tk.Text(my_game, bd=8, font=fnt, width=60, height=5)
    txt.place(x=400, y=120, anchor="center")
    txt.focus_set()
    txt.insert("1.1", "Waiting For players")
    txt.config(state=tk.DISABLED)
    entry = tk.Entry(my_game, width=50)
    entry.place(x=400, y=220, anchor="center")
    answer_button = tk.Button(my_game, image=send_ans_img, command=send_to_server)
    answer_button.place(x=400, y=280, anchor="center")
    answer_button.config(state=tk.DISABLED)
    entry['state'] = tk.DISABLED
    help_button = tk.Button(my_game, image=button_help_img, command=open_help_menu)
    help_button.place(x=400, y=350, anchor="center")
    player_label = tk.Label(my_game, text="You are player number " + player_num, fg="white", bg="black")
    player_label.place(x=400, y=30, anchor="center")


def get_data():
    """gets data from server and check for possible crashes"""
    try:
        data = client_socket.recv(MAX_LEN).decode()
        print(data)
        if data == "ServerCrash":
            print("server crash")
            exit_game()
        elif data == "ClientCrash":
            print("client crash")
            data = client_socket.recv(MAX_LEN).decode()
            print(data)
        return data
    except ConnectionAbortedError:
        quit()


def text_box_config(text_data):
    """configures the txt object according to given data"""
    txt.config(state=tk.NORMAL)
    txt.delete(1.0, tk.END)
    txt.insert("1.1", text_data)
    txt.config(state=tk.DISABLED)


def open_game():
    """used to start playing the game with the game's logic and style"""
    global client_socket, player_num
    button1.config(state=tk.NORMAL, command=replay_game)
    try:
        client_socket = socket.socket()
        client_socket.connect((CLIENT_IP, PORT))
        client_socket.settimeout(1.0)
        player_num = client_socket.recv(MAX_LEN).decode()
        client_socket.settimeout(None)
        print(player_num)
    except ConnectionRefusedError:
        quit()
    except ConnectionAbortedError:
        quit()
    except OSError:
        quit()
    button1.config(state=tk.NORMAL, command=replay_game)
    game_settings()
    my_data = get_data()
    while my_data != "Exit":
        text_box_config(my_data)
        answer_button.config(state=tk.NORMAL)
        entry['state'] = tk.NORMAL
        my_data = get_data()
    try:
        stat_data = client_socket.recv(MAX_LEN).decode()
        winner_data = client_socket.recv(MAX_LEN).decode()
        answer_button.config(state=tk.DISABLED)
        replay_button = tk.Button(my_game, image=replay_img, command=replay_game)
        replay_button.place(x=400, y=420, anchor="center")
        stat_label = tk.Label(my_game, text="You answered " + stat_data + " correct ", fg="white", bg="black")
        stat_label.place(x=400, y=190, anchor="center")
        text_box_config(winner_data)
        client_socket.close()
    except ConnectionAbortedError:
        quit()


def bg_volume(value):
    """volume for music"""
    n_value = int(value) / 100
    pygame.mixer.music.set_volume(n_value)


def root_settings():
    """configures the root settings"""
    global root
    global button1
    global game_thread
    global intVr
    global back_img
    global button_start_img
    global button_help_img
    global button_exit_img
    root = tk.Tk()
    root.title('Start Menu')
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    # make the root window the size of the image
    root.geometry("%dx%d" % (X, Y))
    root.protocol("WM_DELETE_WINDOW", exit_game)
    back_img = tk.PhotoImage(file=FIRST_SCREEN_IMG_LOC)
    button_start_img = tk.PhotoImage(file=START_IMG_LOC)
    button_help_img = tk.PhotoImage(file=HELP_BUTTON_IMG_LOC)
    button_exit_img = tk.PhotoImage(file=EXIT_IMG_LOC)
    # root has no image argument, so use a label as a panel
    lbl = tk.Label(root, image=back_img)
    lbl.pack(fill='both', expand='yes')
    intVr = tk.IntVar()
    scl = tk.Scale(root, orient=tk.HORIZONTAL, from_=0, to=100, variable=intVr, command=bg_volume, length=100)
    scl.place(x=5, y=5)
    game_thread = threading.Thread(target=open_game)
    button1 = tk.Button(root, image=button_start_img, command=game_thread.start)
    button1.place(x=400, y=250, anchor="center")
    button2 = tk.Button(root, image=button_help_img, command=open_help_menu)
    button2.place(x=400, y=350, anchor="center")
    exit_button = tk.Button(root, image=button_exit_img, command=exit_game)
    exit_button.place(x=400, y=450, anchor="center")


def play_music():
    """plays given music """
    global py_music
    pygame.mixer.init()
    py_music = pygame.mixer.music
    py_music.load(MUSIC_LOC)
    py_music.play(loops=-1)
    py_music.set_volume(0)


def main():
    root_settings()
    play_music()
    root.mainloop()


if __name__ == "__main__":
    main()

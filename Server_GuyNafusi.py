import socket
import select
import random
import sys
import time

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = "0.0.0.0"
QUESTIONS = 5
question_answer_list = [("A father's child, a mother's child, yet no one's son. Who am I?", "The daughter"),
                        ("I love spinach. Who am I?", "Popeye"),
                        ("I travel the world and I am drunk constantly. Who am I?", "Water"),
                        ("I make billions of dollars selling Windows. Who am I?", "Microsoft"),
                        ("The more you have of me, the less you see. Who am I?", "Darkness"),
                        ("I have no life, but I can die. What am I?", "A battery"),
                        ("People make me, save me, change me, raise me. What am I?", "Money"),
                        ("I’m where yesterday follows today. What am I?", "A Dictionary")]


def exceptions_keyboard(cl_sk):
    """for keyboard interrupt error, server crashed"""
    for current_sock in cl_sk:
        try:
            current_sock.send("ServerCrash".encode())
        except ConnectionResetError:
            pass


def send_to_client(sock, msg):
    """sends a given message to a client's socket"""
    sock.send(msg.encode())
    time.sleep(0.1)


def exceptions_any(cl_sk, e):
    """handles exception in case of a client crash"""
    count = 1
    for current_sock in cl_sk:
        try:
            send_to_client(current_sock, "ClientCrash")
            send_to_client(current_sock, "Exit")
            if count == 1:
                send_to_client(current_sock, str(count_correct_1))
            else:
                send_to_client(current_sock, str(count_correct_2))
            send_to_client(current_sock, "You Won By Forfiet")
        except ConnectionResetError:
            count += 1
        except ConnectionAbortedError:
            pass
    print(e)


def WaitingForPlayers(server_socket):
    """waits for 2 players to connect in order to return a list of them"""
    global client_sockets
    client_sockets = []
    count = 0
    while count < 2:
        r1list, w1list, x1list = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in r1list:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                count += 1
                client_sockets.append(connection)
                send_to_client(connection, str(count))
            else:
                data = current_socket.recv(MAX_MSG_LENGTH).decode()
                if data == "":
                    print("Connection closed", )
                    client_sockets.remove(current_socket)
                    current_socket.close()
    return client_sockets


def QuestionAndAnswers(client_sockets_l, server_socket, q_a):
    """works every round to send and check a question and a given answer"""
    count_A = 0
    player_1 = client_sockets_l[0]
    player_2 = client_sockets_l[1]
    count_A_1 = False
    count_A_2 = False
    for current_st in client_sockets_l:
        msg = q_a[0]
        current_st.send(msg.encode())
    while count_A < 2:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets_l, client_sockets_l, [])
        for current_socket in rlist:
            if current_socket is not server_socket:
                count_A += 1
                data = current_socket.recv(MAX_MSG_LENGTH).decode()
                print(data)
                if data == "":
                    print("Connection closed")
                    client_sockets.remove(current_socket)
                    current_socket.close()
                elif data == q_a[1]:
                    if current_socket == player_1:
                        count_A_1 = True
                    elif current_socket == player_2:
                        count_A_2 = True

    return count_A_1, count_A_2


def set_server():
    """set up the server"""
    try:
        server_st = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_st.bind((SERVER_IP, SERVER_PORT))
        server_st.listen()
        return server_st
    except OSError:
        sys.exit()


def correct_answers(server_st, q_a_list):
    """check the amount of correct answers by each client"""
    global count_correct_1
    global count_correct_2
    count_correct_1 = 0
    count_correct_2 = 0
    for i in range(QUESTIONS):
        correct_1, correct_2 = QuestionAndAnswers(client_sockets_list, server_st, q_a_list[i])
        if correct_1:
            count_correct_1 += 1
        if correct_2:
            count_correct_2 += 1


def exit_clients():
    """ends a game by sending end messages to the client """
    for cr_st in client_sockets_list:
        cr_st.send("Exit".encode())
    client_sockets_list[0].send(str(count_correct_1).encode())
    client_sockets_list[1].send(str(count_correct_2).encode())
    time.sleep(0.1)


def send_won():
    """determines who won in the game and sends a matching messgae"""
    if count_correct_1 > count_correct_2:
        for cs in client_sockets_list:
            cs.send("The winner is Player Number 1!".encode())

    elif count_correct_2 > count_correct_1:
        for cs in client_sockets_list:
            cs.send("The winner is Player Number 2!".encode())

    else:
        for cs in client_sockets_list:
            cs.send("This is a tie!".encode())

    print("Correct for number 1 is: " + str(count_correct_1))
    print("Correct for number 2 is: " + str(count_correct_2))


def main():
    global client_sockets_list
    print("Setting up server...")
    server_st = set_server()
    client_sockets_list = []
    while True:
        try:
            print("Listening for clients...")
            client_sockets_list = []
            client_sockets_list = WaitingForPlayers(server_st)
            q_a_list = random.sample(question_answer_list, QUESTIONS)
            correct_answers(server_st, q_a_list)
            exit_clients()
            send_won()
        except KeyboardInterrupt:
            exceptions_keyboard(client_sockets)
        except Exception as e:
            exceptions_any(client_sockets, e)


if __name__ == "__main__":
    main()

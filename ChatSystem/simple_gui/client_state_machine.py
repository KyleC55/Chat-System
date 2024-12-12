from chat_utils import *
import json

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action": "connect", "target": peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        status = response.get("status", "")
        if status == "success":
            self.peer = peer
            self.out_msg += 'You are connected with ' + self.peer + '\n'
            return True
        elif status == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif status == "self":
            self.out_msg += 'Cannot talk to yourself\n'
        elif status == "not_online":
            self.out_msg += 'User is not online, try again later\n'
        else:
            self.out_msg += 'Unknown status received from server.\n'
        return False

    def disconnect(self):
        msg = json.dumps({"action": "disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def send_move(self, position): 
        move_msg = f"press_button_{position + 1}"
        msg = json.dumps({"action": "exchange", "from": self.me, "message": move_msg})
        mysend(self.s, msg)

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''

        if self.state == S_LOGGEDIN:
            # Handling commands while logged in but not chatting
            if len(my_msg) > 0:
                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    # Request time from server
                    mysend(self.s, json.dumps({"action": "time"}))
                    server_response = json.loads(myrecv(self.s))
                    if server_response.get("action") == "time":
                        current_time = server_response.get("results", "Unknown time")
                        self.out_msg += "Time is: " + current_time + "\n"
                    else:
                        self.out_msg += "Failed to get the time.\n"

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action": "list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in + "\n"

                elif my_msg == 'game':
                    # Send a start_game request to the server
                    mysend(self.s, json.dumps({"action": "start_game"}))
                    # Inform the user that the request has been sent
                    self.out_msg += "Game request sent. Waiting for the server to start the game...\n"

                elif my_msg.startswith('c'):
                    peer = my_msg[1:].strip()
                    if self.connect_to(peer):
                        self.state = S_CHATTING
                        self.out_msg += 'Connected to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg.startswith('?'):
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action": "search", "target": term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if len(search_rslt) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg.startswith('p') and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action": "poem", "target": poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    if len(poem) > 0:
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                else:
                    self.out_msg += menu

            # Process incoming peer/server messages while logged in
            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err:
                    self.out_msg += "json.loads failed: " + str(err) + "\n"
                    return self.out_msg

                action = peer_msg.get("action", "")
                status = peer_msg.get("status", "")

                if action == "connect":
                    if status == "success":
                        peer = peer_msg.get("target", "")
                        self.peer = peer
                        self.state = S_CHATTING
                        self.out_msg += 'You are connected with ' + self.peer + '\n'
                        self.out_msg += 'Chat away!\n\n-----------------------------------\n'
                    elif status == "request":
                        from_user = peer_msg.get("from", "")
                        accept = True  # Automatically accept the game request
                        if accept:
                            self.peer = from_user
                            self.state = S_CHATTING
                            # Optionally, send an acknowledgment to the server
                            self.out_msg += f"{from_user} has connected with you for a game.\nEnjoy the game!\n\n-----------------------------------\n"
                        else:
                            # Optionally handle rejection
                            self.out_msg += f"{from_user} tried to connect with you, but you rejected the game.\n"
                elif action == "start_game":
                    # Server initiating start of the game
                    self.out_msg += "[Server]: Enjoy Evans Tic Tac Toe!\n\n"

                elif action == "update_board":
                    board = peer_msg.get("board", [])
                    current_player = peer_msg.get("current_player", "")
                    board_str = ",".join([mark if mark else " " for mark in board])
                    self.out_msg += f"update_board:{board_str}:{current_player}\n"

                elif action == "game_result":
                    winner = peer_msg.get("winner", "")
                    self.out_msg += f"game_result:{winner}\n"

            return self.out_msg

        elif self.state == S_CHATTING:
            # Sending chat messages to the server
            if len(my_msg) > 0:
                if my_msg.startswith("press_button_"): 
                    try: 
                        position = int(my_msg.split("_")[-1]) - 1
                        if 0 <= position < 9:
                            self.send_move(position)
                        else:
                            self.out_msg += "Invalid move position.\n"
                    except ValueError:
                        self.out_msg += "Invalid move format.\n"
                else:
                    msg = json.dumps({"action": "exchange",
                                      "from": "[" + self.me + "]",
                                      "message": my_msg}) 
                    mysend(self.s, msg)
                
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''

            # Receiving messages from peer/server while chatting
            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err:
                    self.out_msg += "json.loads failed: " + str(err) + "\n"
                    return self.out_msg

                action = peer_msg.get("action", "")
                if action == "exchange":
                    # Display the incoming chat message
                    self.out_msg += peer_msg["from"] + " " + peer_msg["message"] + "\n"
                elif action == "disconnect":
                    self.out_msg += "Your peer has disconnected.\n"
                    self.state = S_LOGGEDIN
                elif action == "connect":
                    from_user = peer_msg.get("from", "")
                    self.out_msg += f"{from_user} has connected with you.\n"
                elif action == "update_board":
                    board = peer_msg.get("board", [])
                    current_player = peer_msg.get("current_player", "")
                    board_str = ",".join([mark if mark else " " for mark in board])
                    self.out_msg += f"update_board:{board_str}:{current_player}\n"
                elif action == "game_result":
                    winner = peer_msg.get("winner", "")
                    self.out_msg += f"game_result:{winner}\n"

            # If we returned to LOGGEDIN after finishing chat
            if self.state == S_LOGGEDIN:
                self.out_msg += menu

            return self.out_msg

        else:
            # Invalid state or error
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg

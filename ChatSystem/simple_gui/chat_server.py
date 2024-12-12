import time
import socket
import select
import sys
import json
import indexer
import pickle as pkl
from chat_utils import *
import chat_group as grp

class Game:
    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.sockets = [player1['socket'], player2['socket']]
        self.board = [""] * 9  # 0-8 indices
        self.current_player = player1['name']  # Player1 starts
        self.winner = None
        self.is_draw = False

    def make_move(self, player_name, position):
        if self.winner or self.is_draw:
            return {"status": "game_over"}

        if player_name != self.current_player:
            return {"status": "not_your_turn"}

        if position < 0 or position > 8 or self.board[position] != "":
            return {"status": "invalid_move"}

        mark = "X" if player_name == self.players[0]['name'] else "O"
        self.board[position] = mark

        if self.check_winner(mark):
            self.winner = player_name
        elif "" not in self.board:
            self.is_draw = True
        else:
            # Switch turns
            self.current_player = self.players[1]['name'] if self.current_player == self.players[0]['name'] else self.players[0]['name']

        return {"status": "move_made"}

    def check_winner(self, mark):
        # Winning combinations
        win_combinations = [
            [0,1,2], [3,4,5], [6,7,8],  # Rows
            [0,3,6], [1,4,7], [2,5,8],  # Columns
            [0,4,8], [2,4,6]            # Diagonals
        ]
        for combo in win_combinations:
            if all(self.board[pos] == mark for pos in combo):
                return True
        return False

    def get_board(self):
        return self.board

class Server:
    def __init__(self):
        self.new_clients = []  # List of new sockets whose user id is not known
        self.logged_name2sock = {}  # Mapping username to socket
        self.logged_sock2name = {}  # Mapping socket to username
        self.all_sockets = []
        self.group = grp.Group()
        self.games = {}  # Mapping frozenset of players to Game instances

        # Start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)  # Use SERVER from chat_utils.py
        self.server.listen(5)
        self.all_sockets.append(self.server)
        print(f"Server started on {SERVER[0]}:{SERVER[1]}")

        # Initialize past chat indices
        self.indices = {}
        self.sonnet = indexer.PIndex("ChatSystem/simple_gui/AllSonnets.txt")

    def new_client(self, sock):
        print('New client connected.')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        try:
            msg = json.loads(myrecv(sock))
            print("Login attempt:", msg)
            if len(msg) > 0 and msg["action"] == "login":
                name = msg["name"]

                if not self.group.is_member(name):
                    # Move socket from new_clients to logged clients
                    self.new_clients.remove(sock)
                    self.logged_name2sock[name] = sock
                    self.logged_sock2name[sock] = name

                    # Load chat history
                    if name not in self.indices:
                        try:
                            self.indices[name] = pkl.load(open(name + '.idx', 'rb'))
                        except IOError:
                            self.indices[name] = indexer.Index(name)

                    print(f"{name} logged in.")
                    self.group.join(name)

                    mysend(sock, json.dumps({"action": "login", "status": "ok"}))
                else:
                    # Duplicate login attempt
                    mysend(sock, json.dumps({"action": "login", "status": "duplicate"}))
                    print(f"{name} attempted duplicate login.")
            else:
                print('Wrong login format received.')
        except Exception as e:
            print(f"Error during login: {e}")
            if sock in self.all_sockets:
                self.all_sockets.remove(sock)

    def logout(self, sock):
        if sock in self.logged_sock2name:
            name = self.logged_sock2name[sock]
            pkl.dump(self.indices[name], open(name + '.idx','wb'))
            del self.indices[name]
            del self.logged_name2sock[name]
            del self.logged_sock2name[sock]
            self.group.leave(name)
            print(f"{name} logged out.")

        if sock in self.all_sockets:
            self.all_sockets.remove(sock)
        sock.close()

    def handle_connect(self, from_sock, msg):
        to_name = msg["target"]
        from_name = self.logged_sock2name[from_sock]

        if to_name == from_name:
            response = {"action": "connect", "status": "self"}
        elif self.group.is_member(to_name):
            to_sock = self.logged_name2sock[to_name]
            # Create a game between from_name and to_name
            players = [
                {"name": from_name, "socket": from_sock},
                {"name": to_name, "socket": to_sock}
            ]
            game = Game(players[0], players[1])
            self.games[frozenset([from_name, to_name])] = game

            response = {"action": "connect", "status": "success"}

            # Notify the other user about the game
            mysend(to_sock, json.dumps({
                "action": "connect",
                "status": "request",
                "from": from_name
            }))
        else:
            response = {"action": "connect", "status": "not_online"}

        mysend(from_sock, json.dumps(response))

    def handle_exchange(self, from_sock, msg):
        from_name = self.logged_sock2name[from_sock]
        game = self.find_game(from_name)

        if not game:
            print(f"No active game found for {from_name}.")
            return

        # Parse the move
        move_msg = msg.get("message", "")  # e.g., "press_button_1"
        if not move_msg.startswith("press_button_"):
            # Handle as a regular chat message
            print(f"Chat message from {from_name}: {move_msg}")
            # Relay the chat message to the peer
            peer_sock = [p['socket'] for p in game.players if p['name'] != from_name][0]
            chat_msg = {
                "action": "exchange",
                "from": from_name,
                "message": move_msg
            }
            mysend(peer_sock, json.dumps(chat_msg))
            return

        try:
            button_number = int(move_msg.split("_")[-1])
            position = button_number - 1  # Assuming buttons 1-9 map to 0-8
        except ValueError:
            print(f"Invalid button number from {from_name}: {move_msg}")
            return

        move_result = game.make_move(from_name, position)

        if move_result["status"] == "game_over":
            # Determine game result
            if game.winner:
                result = {"action": "game_result", "winner": game.winner}
            elif game.is_draw:
                result = {"action": "game_result", "winner": "Draw"}
            else:
                result = {"action": "game_result", "winner": "Unknown"}

            # Notify both players
            for player in game.players:
                mysend(player['socket'], json.dumps(result))

            # Remove game from active games
            del self.games[frozenset([game.players[0]['name'], game.players[1]['name']])]
        elif move_result["status"] == "move_made":
            # Send updated board to both players
            board_update = {
                "action": "update_board",
                "board": game.get_board(),
                "current_player": game.current_player
            }
            for player in game.players:
                mysend(player['socket'], json.dumps(board_update))
        elif move_result["status"] == "not_your_turn":
            # Inform player it's not their turn
            mysend(from_sock, json.dumps({"action": "error", "message": "Not your turn."}))
        elif move_result["status"] == "invalid_move":
            # Inform player the move is invalid
            mysend(from_sock, json.dumps({"action": "error", "message": "Invalid move."}))

    def find_game(self, player_name):
        for game in self.games.values():
            if player_name in [p['name'] for p in game.players]:
                return game
        return None

    def handle_msg(self, from_sock):
        try:
            msg = myrecv(from_sock)
            if len(msg) > 0:
                msg = json.loads(msg)
                action = msg.get("action", "")

                if action == "connect":
                    self.handle_connect(from_sock, msg)

                elif action == "exchange":
                    self.handle_exchange(from_sock, msg)

                elif action == "list":
                    msg_out = self.group.list_all()
                    mysend(from_sock, json.dumps({"action": "list", "results": msg_out}))

                elif action == "poem":
                    poem_indx = int(msg["target"])
                    poem = self.sonnet.get_poem(poem_indx)
                    poem = '\n'.join(poem).strip()
                    mysend(from_sock, json.dumps({"action": "poem", "results": poem}))

                elif action == "time":
                    ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                    mysend(from_sock, json.dumps({"action": "time", "results": ctime}))

                elif action == "search":
                    term = msg["target"]
                    from_name = self.logged_sock2name[from_sock]
                    search_rslt = '\n'.join([x[-1] for x in self.indices[from_name].search(term)])
                    mysend(from_sock, json.dumps({"action": "search", "results": search_rslt}))

                elif action == "disconnect":
                    from_name = self.logged_sock2name[from_sock]
                    game = self.find_game(from_name)
                    if game:
                        # Inform the other player
                        other_player = [p for p in game.players if p['name'] != from_name][0]
                        mysend(other_player['socket'], json.dumps({"action": "disconnect", "from": from_name}))
                        del self.games[frozenset([game.players[0]['name'], game.players[1]['name']])]

                    # Handle normal disconnect
                    self.group.disconnect(from_name)
                    mysend(from_sock, json.dumps({"action": "disconnect", "status": "ok"}))

                elif action == "start_game":
                    # Additional logic if needed
                    mysend(from_sock, json.dumps({"action": "start_game"}))

                else:
                    print(f"Unknown action received: {action}")
            else:
                # Client disconnected
                self.logout(from_sock)
        except Exception as e:
            print(f"Error handling message: {e}")
            self.logout(from_sock)

    def run(self):
        print('Starting server...')
        while True:
            try:
                read, _, _ = select.select(self.all_sockets, [], [])
                for sock in read:
                    if sock == self.server:
                        # New connection
                        client_sock, address = self.server.accept()
                        self.new_client(client_sock)
                    elif sock in self.logged_name2sock.values():
                        # Existing client message
                        self.handle_msg(sock)
                    elif sock in self.new_clients:
                        # New client attempting to login
                        self.login(sock)
            except KeyboardInterrupt:
                print("Server shutting down.")
                for sock in self.all_sockets:
                    sock.close()
                break

def main():
    server = Server()
    server.run()

if __name__ == "__main__":
    main()

import socket
from _thread import *
import sys
import random

address = ("localhost", 20000)

# Create sockets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect sockets
server_socket.bind(address)
server_socket.listen(10)

clientNumber = 0  # Total number of clients
words = [
    'paralelepipedo', 'retrovisor','geladeira'
]

word2 = [
    'quadrado','volante' ,'panela'
]

word3 = [
    'triangulo','amortecedor', 'armario'
]

topic = [
    'Figura Geometrica', 'Carro', 'Cozinha'
]

games = []

class Game:
    word = ""
    gameString = ""
    incorrectGuesses = 0
    incorrectLetters = 0
    turn = 1
    lock = 0
    full = False

    def __init__(self, word, num_players_requested):
        self.incorrectLetters = []
        self.lock = allocate_lock()
        self.word = word
        for i in range(len(word)):
            self.gameString += "_"

    def getStatus(self):
        if self.incorrectGuesses >= 6:
            return 'You Lose :('
        elif not '_' in self.gameString:
            return 'You Win!'
        else:
            return ''

    def guess(self, letter):
        if letter not in self.word or letter in self.gameString:
            self.incorrectGuesses += 1
            self.incorrectLetters.append(letter)
            return 'Incorrect!'
        else:
            gameString = list(self.gameString)
            for i in range(len(self.word)):
                if self.word[i] == letter:
                    gameString[i] = letter
            self.gameString = ''.join(gameString)
            return 'Correct!'

    def changeTurn(self):
        if self.turn == 1:
            self.turn = 2
        elif self.turn == 2:
            self.turn = 3
        else:
            self.turn = 1


def Main():
    global clientNumber
    global words
    print('servidor runing...')
    while 1:
        conn,addr = server_socket.accept()
        print("nova conexao recebida de: " + addr[0]+ ": " + str(addr[1]))
        clientNumber += 1
        start_new_thread(clientThread, (conn,))
    server_socket.close()

def getGame(num_players_requested):
    if num_players_requested >= 2 and num_players_requested <= 3:
        for game in games:
            print('cheguei no not game.full')
            if num_players_requested == 3:
                game.full = True
                print('entrei no if num_plays aqui ver se tem 2 players')
            return (game, clientNumber)
    if len(games) < 2:
        print('entrei aqui no if len')
        word = words[random.randint(0, 3)]
        game = Game(word, num_players_requested)
        games.append(game)
        return (game, clientNumber)
    else:
        return -1

def clientThread(c):  # Threaded client handler
    global clientNumber

    x = getGame(clientNumber)
    if x == -1:
        send(c, 'server cheio capacidade maxima 3')
    else:
        game, player = x
        print (player)
        send(c, 'Esperando o jogador se conectar')

        while not game.full:
            continue
        send(c, 'Jogo comecou!! Boa Sorte!!')
        playerGame(c, player, game)

def send(c, msg):
    packet = bytes([len(msg)]) + bytes(msg, 'utf8')
    c.send(packet)

def send_game_control_packet(c, game):
    msgFlag = bytes([0])
    data = bytes(game.gameString + ''.join(game.incorrectLetters), 'utf8')
    gamePacket = msgFlag + bytes([len(game.word)]) + bytes([game.incorrectGuesses]) + data
    c.send(gamePacket)

def playerGame(c, player, game):
    global clientNumber

    while True:
        while game.turn != player:
            continue
        game.lock.acquire()

        status = game.getStatus()
        if status != '':
            send_game_control_packet(c, game)
            send(c, status)
            send(c, "Game Over!")
            game.changeTurn()
            game.lock.release()
            break

        send(c, 'Your Turn!')

        send_game_control_packet(c, game)

        rcvd = c.recv(1024)
        letterGuessed = bytes([rcvd[1]]).decode('utf-8')

        send(c, game.guess(letterGuessed))

        status = game.getStatus()
        if len(status) > 0:
            send_game_control_packet(c, game)
            send(c, status)
            send(c, "Game Over!")
            game.changeTurn()
            game.lock.release()
            break

        send(c, "Waiting on other player...")
        game.changeTurn()
        game.lock.release()

    if game in games:
        games.remove(game)
    c.close()

if __name__ == '__main__':
    Main()
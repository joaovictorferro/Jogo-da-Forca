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

topic = [
    'figura geometrica', 'carro', 'cozinha'
]

games = []

class Game:
    word = ""
    topic = ""
    gameString = ""
    incorrectGuesses = 0
    incorrectLetters = 0
    turn = 1
    lock = 0
    full = False

    def __init__(self, word, topic):
        self.incorrectLetters = []
        self.lock = allocate_lock()
        self.word = word
        self.topic = topic
        for i in range(len(word)):
            self.gameString += "_"

    def getStatus(self):
        if self.incorrectGuesses >= 7:
            return 'Voces Perderam, mais de 7 tentativa :('
        elif not '_' in self.gameString:
            return 'Voce Ganhou!'
        else:
            return ''

    def guess(self, letter):
        if letter not in self.word or letter in self.gameString:
            self.incorrectGuesses += 1
            self.incorrectLetters.append(letter)
            return 'Letra incorreta!'
        else:
            gameString = list(self.gameString)
            for i in range(len(self.word)):
                if self.word[i] == letter:
                    gameString[i] = letter
            self.gameString = ''.join(gameString)
            return 'Letra correta!'

    def changeTurn(self):
        self.turn += 1
        if self.turn == 4:
            self.turn = 1

def Main():
    global clientNumber
    global words
    global topic

    print('servidor funcionando...')
    while 1:
        conn,addr = server_socket.accept()
        print("nova conexao recebida de: " + addr[0]+ ": " + str(addr[1]))
        clientNumber += 1
        print ("cliente" , clientNumber)
        start_new_thread(clientThread, (conn,))
    server_socket.close()

def getGame(n):

    if n >= 2 and n <= 3:
        for game in games:
            if n == 3:
                game.full = True
            return (game, n)

    if len(games) < 2:
        m = random.randint(0, 2)
        topics = topic[m]
        word = words[m]
        game = Game(word,topics)
        games.append(game)
        return (game, n)
    else:
        return -1

def clientThread(c):
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
    data = bytes(game.gameString + ''.join(game.incorrectLetters) + ''.join(game.topic), 'utf8')
    gamePacket = msgFlag + bytes([len(game.word)]) + bytes([game.incorrectGuesses]) + bytes([len(game.topic)]) + data
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
            send(c, "Fim de jogo!")
            game.changeTurn()
            game.lock.release()
            break

        send(c, 'Seu turno!')

        send_game_control_packet(c, game)

        rcvd = c.recv(1024)
        letterGuessed = bytes([rcvd[1]]).decode('utf-8')

        send(c, game.guess(letterGuessed))

        status = game.getStatus()
        if len(status) > 0:
            send_game_control_packet(c, game)
            send(c, status)
            send(c, "Fim de jogo!")
            game.changeTurn()
            game.lock.release()
            break

        send(c, "Aguardando o outro jogador...")
        game.changeTurn()
        game.lock.release()

    if game in games:
        games.remove(game)
    c.close()

if __name__ == '__main__':
    Main()
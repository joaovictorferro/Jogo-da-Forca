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

jogos = []

class Game:
    word = ""
    topic = ""
    gameString = ""
    tentativas = 0
    letrasErradas = 0
    turno = 1
    lock = 0
    full = False

    def __init__(self, word, topic):
        self.letrasErradas= []
        self.lock = allocate_lock()
        self.word = word
        self.topic = topic
        for i in range(len(word)):
            self.gameString += "_"

    def getStatus(self):
        if self.tentativas == 7:
            return 'Voces Perderam, mais de 7 tentativa :('
        elif not '_' in self.gameString:
            return 'Voce Ganhou!'
        else:
            return ''

    def letras(self, letra):
        if letra not in self.word or letra in self.gameString:
            self.tentativas += 1
            self.letrasErradas.append(letra)
            return 'Letra incorreta!'
        else:
            gameString = list(self.gameString)
            for i in range(len(self.word)):
                if self.word[i] == letra:
                    gameString[i] = letra
            self.gameString = ''.join(gameString)
            return 'Letra correta!'

    def turnos(self):
        self.turno += 1
        if self.turno == 4:
            self.turno = 1

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
        start_new_thread(client, (conn,))
    server_socket.close()

def startGame(n):
    for game in jogos:
        if game.full != True and n == 2:
            return (game, n)
        if n == 3 and game.full != True:
            game.full = True
            return (game, n)

    if n == 1:
        m = random.randint(0, 2)
        topics = topic[m]
        word = words[m]
        game = Game(word,topics)
        jogos.append(game)
        return (game, n)

def client(c):
    global clientNumber

    x = startGame(clientNumber)

    game, player = x
    print (player)
    send(c, 'Esperando o jogador se conectar')

    while not game.full:
        continue
    
    clientNumber = 0
    send(c, 'Jogo comecou!! Boa Sorte!!')
    playerGame(c, player, game)

def send(c, msg):
    packet = bytes([len(msg)]) + bytes(msg, 'utf8')
    c.send(packet)

def send_packet(c, game):
    msgFlag = bytes([0])
    data = bytes(game.gameString + ''.join(game.letrasErradas) + ''.join(game.topic), 'utf8')
    gamePacket = msgFlag + bytes([len(game.word)]) + bytes([game.tentativas]) + bytes([len(game.topic)]) + data
    c.send(gamePacket)

def verificacao(status,game,c):
    if status != '' or len(status) > 0:
            send_packet(c, game)
            send(c, status)
            send(c, "Fim de jogo!")
            game.turnos()
            game.lock.release()
            return 1
    return 0

def playerGame(c, player, game):
    global clientNumber

    while True:
        while game.turno != player:
            continue
        game.lock.acquire()

        status = game.getStatus()

        if verificacao(status,game,c) == 1:
            break

        send(c, 'Seu turno!')
        send_packet(c, game)
        rcvd = c.recv(1024)
        letra= bytes([rcvd[1]]).decode('utf-8')
        send(c, game.letras(letra))
        status = game.getStatus()

        if verificacao(status,game,c) == 1:
            break

        send(c, "Aguardando o outro jogador...")
        game.turnos()
        game.lock.release()

    if game in jogos:
        jogos.remove(game)
    c.close()

if __name__ == '__main__':
    Main()
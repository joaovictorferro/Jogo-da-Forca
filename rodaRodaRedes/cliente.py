import socket
import sys

address = ("localhost",20000)

def Main():
	s = socket.socket()
	s.connect(address)
	playGame(s)

def recv_helper(socket):
    first_byte_value = int(socket.recv(1)[0])
    if first_byte_value == 0:
        x, y = socket.recv(2)
        return 0, socket.recv(int(x)), socket.recv(int(y))
    else:
        return 1, socket.recv(first_byte_value)

def playGame(s):
    while True:
        pkt = recv_helper(s)
        msgFlag = pkt[0]
        if msgFlag != 0:
            msg = pkt[1].decode('utf8')
            print(msg)
            if msg == 'server cheio capacidade maxima 3' or 'Game Over!' in msg:
                break
        else:
            gameString = pkt[1].decode('utf8')
            incorrectGuesses = pkt[2].decode('utf8')
            print(" ".join(list(gameString)))
            print("Incorrect Guesses: " + " ".join(incorrectGuesses) + "\n")
            if "_" not in gameString or len(incorrectGuesses) >= 6:
                continue
            else:
                letterGuessed = ''
                valid = False
                while not valid:
                    letterGuessed = input('Letter to guess: ').lower()
                    if letterGuessed in incorrectGuesses or letterGuessed in gameString:
                        print("Error! Letter " + letterGuessed.upper() + " has been guessed before, please guess another letter.")
                    elif len(letterGuessed) > 1 or not letterGuessed.isalpha():
                        print("Error! Please guess one letter")
                    else:
                        valid = True
                msg = bytes([len(letterGuessed)]) + bytes(letterGuessed, 'utf8')
                s.send(msg)

    s.shutdown(socket.SHUT_RDWR)
    s.close()


if __name__ == '__main__':
    Main()
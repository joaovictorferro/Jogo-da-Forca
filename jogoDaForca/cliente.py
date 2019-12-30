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
        x, y,z = socket.recv(3)
        return 0, socket.recv(int(x)), socket.recv(int(y)), socket.recv(int(z))
    else:
        return 1, socket.recv(first_byte_value)

def playGame(s):
    while True:
        pkt = recv_helper(s)
        msgFlag = pkt[0]
        if msgFlag != 0:
            msg = pkt[1].decode('utf8')
            print(msg)
            if msg == 'server cheio capacidade maxima 3' or 'Fim de jogo!' in msg:
                break
        else:
            gameString = pkt[1].decode('utf8')
            incorrectGuesses = pkt[2].decode('utf8')
            topic  = pkt[3].decode('utf8')
            print(" ".join(list(gameString)))
            print("Letras erradas: " + " ".join(incorrectGuesses) + "\n")

            if len(incorrectGuesses) > 3:
                print('Dica:' + " ".join(topic) + "\n")     
            
            if "_" not in gameString or len(incorrectGuesses) >= 7:
                continue
            else:
                letterGuessed = ''
                valid = False
                while not valid:
                    letterGuessed = input('Digite uma Lestra (a-z): ').lower()
                    if letterGuessed in incorrectGuesses or letterGuessed in gameString:
                        print("Letra: " + letterGuessed.upper() + " ja foi digitida essa letra, por favor digite outra letra")
                    elif len(letterGuessed) > 1 or not letterGuessed.isalpha():
                        print("Digite apenas uma letra!!")
                    else:
                        valid = True
                msg = bytes([len(letterGuessed)]) + bytes(letterGuessed, 'utf8')
                s.send(msg)

    s.shutdown(socket.SHUT_RDWR)
    s.close()

if __name__ == '__main__':
    Main()
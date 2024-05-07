from DYPlayer import DYPlayer
import board
import busio
PLAYER_VOL   = 70

uart = busio.UART(board.GP4,board.GP5,baudrate=9600)
dyplayer = DYPlayer(uart, volume=PLAYER_VOL)
print("AA")
dyplayer.play()


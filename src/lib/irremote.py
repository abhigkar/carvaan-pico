import pulseio
import board
import adafruit_irremote

class irRemote:
    
    ARTISTS = [0, 255, 128, 127]
    MOODS = [0, 255, 64, 191]
    GEETMALA = [0, 255, 192, 63]
    PREV_STATION = [0, 255, 32, 223]
    NEXT_STATION = [0, 255, 160, 95]
    PLAY_PREV = [0, 255, 96, 159]
    PLAYPAUSE = [0, 255, 224, 31]
    PLAY_NEXT = [0, 255, 16, 239]
    VOL_NEG = [0, 255, 144, 111]
    VOL_POS = [0, 255, 80, 175]
    SAREGAMA_MODE = [0, 255, 208, 47]
    FM = [0, 255, 48, 207]
    USB = [0, 255, 176, 79]
    BT = [0, 255, 112, 143]
    
    def __init__(self):
        self._pulsein = pulseio.PulseIn(board.GP15, maxlen=120, idle_state=True)
        self._decoder = adafruit_irremote.GenericDecode()
        
    def getCommand(self):
        pulses = self._decoder.read_pulses(self._pulsein,blocking=False)
        if pulses is None :
            return None
        code = self._decoder.decode_bits(pulses)
        if code[2] == irRemote.VOL_NEG[2]:
            return "VOL_DOWN"
        elif code[2] == irRemote.VOL_POS[2]:
            return "VOL_UP"
        elif code[2] == irRemote.ARTISTS[2]:
            return "ARTISTS"
        elif code[2] == irRemote.MOODS[2]:
            return "MOODS"
        elif code[2] == irRemote.GEETMALA[2]:
            return "GEETMALA"
        elif code[2] == irRemote.PLAYPAUSE[2]:
            return "PLAYPAUSE"
        elif code[2] == irRemote.PLAY_PREV[2]:
            return "PREVIOUS"
        elif code[2] == irRemote.PLAY_NEXT[2]:
            return "NEXT"
        elif code[2] == irRemote.PREV_STATION[2]:
            return "PREVIOUSALBUM"
        elif code[2] == irRemote.NEXT_STATION[2]:
            return "NEXTALBUM"
        else:
            return None

         

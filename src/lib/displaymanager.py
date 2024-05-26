import busio
import board
import terminalio
import displayio
import i2cdisplaybus
from adafruit_display_text import label, scrolling_label
import adafruit_displayio_sh1106

class oledScreen:
    def __init__(self):
        displayio.release_displays()
        i2c = busio.I2C(board.GP17, board.GP16)
        display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3c)
        self.display = adafruit_displayio_sh1106.SH1106(display_bus, width=132, height=64)
        self._setup()
        
    def _setup(self):
        self.display.sleep()
        #self.display.root_group.hidden = True
        self.splash = displayio.Group()
        self.display.root_group = self.splash
        
        self.heading1 = label.Label(
            terminalio.FONT, text="",scale = 2 ,color=0xFFFFFF, x=5, y=10
        )
        self.heading2 = label.Label(
            terminalio.FONT, text="",scale = 1 ,color=0xFFFFFF, x=5, y=30
        )
        self.heading3 = label.Label(
            terminalio.FONT, text="",scale = 1 ,color=0xFFFFFF, x=5, y=50
        )
        self.icon = label.Label(
            terminalio.FONT, text="",scale = 1 ,color=0xFFFFFF, x=105 , y=5
        )
        self.splash.append(self.heading1)
        self.splash.append(self.heading2)
        self.splash.append(self.heading3)
        self.splash.append(self.icon)
        
    def updateIcon(self,text):
        self.icon.text = text
        
    def displayOn(self):
        self.display.wake()
        
    def updateScreen(self, song, album, mode):
        if mode != None:
            self.heading1.text=mode
        if album != None:
            self.heading2.text=album
        if song != None:
            self.heading3.text=song

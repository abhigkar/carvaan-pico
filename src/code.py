import asyncio
import board
import keypad
import time
import rotaryio
import digitalio

from displaymanager import oledScreen
from musicplayer import player
from adafruit_ticks import ticks_ms, ticks_add, ticks_less
from playerState import PlayerState
import gc


pState = PlayerState()

oled = oledScreen()
mp3player = player(pState.volume)

timeout_interval = 0

enc = rotaryio.IncrementalEncoder(board.GP0, board.GP1)
rotary_button = digitalio.DigitalInOut(board.GP2)
rotary_button.direction = digitalio.Direction.INPUT
rotary_button.pull = digitalio.Pull.UP

pState.rotary_button_mode = "VOLUME_OFF"

rotary_flag = False

async def monitor_player_state():
    global pState
    while True:
        try:
            if (not mp3player.IsPlaying()):
                pState = mp3player.playNextTrack(pState)
                #print("Playing from here")
                
                pState.play_history.append(pState.current_track)
                oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
           
            oled.updateIcon(str(pState.current_track))
        except Exception as e:
             print(e)
        finally:
             await asyncio.sleep(0)

async def rotary_control_hndlr():
    global timeout_interval
    global rotary_flag
    global pState
    while True:
        try:
            if(timeout_interval != 0):
                if(ticks_less(timeout_interval,ticks_ms())):
                    pState.rotary_button_mode = "SELECT_" + pState.current_mode
                    oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
                    timeout_interval = 0
            position = enc.position
            if pState.rotary_last_position == None or position != pState.rotary_last_position:
                if(rotary_flag == True):
                    if(pState.rotary_button_mode == "SELECT_ARTISTS"):
                        #ARTISCS
                        if(position > pState.rotary_last_position):
                            #
                            #print("Select next album")
                            pState.current_artists_playlist_index = pState.current_artists_playlist_index + 1
                            if(pState.current_artists_playlist_index >= pState.max_artists):
                                pState.current_artists_playlist_index = 0
                        else:
                            #
                            #print("Select previous album")
                            pState.current_artists_playlist_index = pState.current_artists_playlist_index -1
                            if(pState.current_artists_playlist_index < 0):
                                pState.current_artists_playlist_index = pState.max_artists-1
                        
                        pState = mp3player.loadPlaylist(pState)
                        pState = mp3player.playNextTrack(pState)
                        oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
                    elif(pState.rotary_button_mode == "SELECT_MOODS"):
                        #MOODS
                         if(position > pState.rotary_last_position):
                            #
                            #print("Select next mood")
                            pState.current_moods_playlist_index = pState.current_moods_playlist_index + 1
                            if(pState.current_moods_playlist_index >= pState.max_moods):
                                pState.current_moods_playlist_index = 0
                         else:
                            #
                            #print("Select previous mood")
                            pState.current_moods_playlist_index = pState.current_moods_playlist_index -1
                            if(pState.current_moods_playlist_index < 0):
                                pState.current_moods_playlist_index = pState.max_moods-1
                        
                         pState = mp3player.loadPlaylist(pState)
                         pState = mp3player.playNextTrack(pState)
                         oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
                    elif(pState.rotary_button_mode == "SELECT_GEETMALA"):
                        #GEETMALA
                         if(position > pState.rotary_last_position):
                            #
                            #print("Select next geetmala")
                            pState.current_geetmala_playlist_index = pState.current_geetmala_playlist_index + 1
                            if(pState.current_geetmala_playlist_index >= pState.max_geetmala):
                                pState.current_geetmala_playlist_index = 0
                         else:
                            #
                            #print("Select previous geetmala")
                            pState.current_geetmala_playlist_index = pState.current_geetmala_playlist_index -1
                            if(pState.current_geetmala_playlist_index <  0):
                                pState.current_geetmala_playlist_index = pState.max_geetmala-1
                        
                         pState = mp3player.loadPlaylist(pState)
                         pState = mp3player.playNextTrack(pState)
                         oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
                    elif(pState.rotary_button_mode == "VOLUME_ON"):
                        if(position > pState.rotary_last_position):
                            #print("VOL UP")
                            pState.volume = pState.volume + 1
                            if(pState.volume <=100):
                                mp3player.setVolume(pState.volume)
                            else:
                                pState.volume=100
                        else:
                            #print("VOL DOWN")
                            pState.volume = pState.volume - 1
                            if(pState.volume >= 0):
                                mp3player.setVolume(pState.volume)
                            else:
                                pState.volume = 0
                           
                        oled.updateScreen(str(pState.volume) , "", "VOLUME")
                        timeout_interval = ticks_ms() + 1000*5
                else:
                    rotary_flag = True
            
            pState.rotary_last_position = position
            
            if not rotary_button.value and pState.rotary_button_state is None:
                pState.rotary_button_state = "pressed"
            if rotary_button.value and pState.rotary_button_state == "pressed":
                #print("rotary_button pressed.")
                #print(pState.rotary_button_mode)
                if (pState.rotary_button_mode != "VOLUME_ON"):
                    #Enter in volume on mode
                    pState.rotary_button_mode = "VOLUME_ON"
                    #print(pState.volume)
                    oled.updateScreen(str(pState.volume) , "", "VOLUME")
                    #print("in volume mode")
                    timeout_interval = ticks_ms() + 1000*5
                else:
                    #exit volume mode
                    pState.rotary_button_mode = "SELECT_" + pState.current_mode
                    pState.volume = mp3player.getVolume()
                    #print("exit volume mode")
                    oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
                pState.rotary_button_state = None
        except Exception as e:
            print(e)
        finally:
            await asyncio.sleep(0)


async def next_previous_hndlr():
    button_pins = (board.GP7, board.GP6)
    global timeout_interval
    global pState
    with keypad.Keys(button_pins, value_when_pressed=False,pull=True) as keys:
        while True:
            try:
                if(timeout_interval != 0):
                    if(ticks_less(timeout_interval,ticks_ms())):
                        oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
                        timeout_interval = 0
                key_event  = keys.events.get()
                if key_event and key_event.pressed:
                    key_number = key_event.key_number
                    if key_number == 0:
                        if(len(pState.play_history) == 0):
                            mp3player.stopPlayer()
                            timeout_interval = ticks_ms() + 1000*5
                            oled.updateScreen("No Previous Song", "", "")
                        else:
                            pState = mp3player.playPreviousTrack(pState)
                            oled.updateScreen(pState.current_playing_song,None,None)
                        
                    elif key_number == 1:
                        pState.play_history.append(pState.current_track)
                        pState = mp3player.playNextTrack(pState)
                        oled.updateScreen(pState.current_playing_song,None,None)
            except Exception as e:
                print(e)
            finally:
                await asyncio.sleep(0)
            
 
async def mode_handler():
    global pState
    button_pins = (board.GP10, board.GP9, board.GP8)
    with keypad.Keys(button_pins, value_when_pressed=False,pull=True) as keys:
        while True:
            try:
                key_event  = keys.events.get()
                if key_event and key_event.pressed:
                    key_number = key_event.key_number
                    flag = False
                    if key_number == 0:
                        if(pState.current_mode != "ARTISTS"):
                            pState.current_mode="ARTISTS"
                            pState.current_selected_album="Lata Mangeshkar"
                            pState.rotary_button_mode = "SELECT_ARTISTS"
                            flag=True
                    elif key_number == 1:
                        if(pState.current_mode != "MOODS"):
                            pState.current_selected_album="Happy"
                            pState.current_mode="MOODS"
                            pState.rotary_button_mode = "SELECT_MOODS"
                            flag=True
                    elif key_number == 2:
                        if(pState.current_mode != "GEETMALA"):
                            pState.current_selected_album="GEETMALA 1952-1955 VOL. 1"
                            pState.current_mode = "GEETMALA"
                            pState.rotary_button_mode = "SELECT_GEETMALA"
                            flag=True
                            
                    if(flag):
                       pState = mp3player.resetPlaylist(pState)
                       pState = mp3player.loadPlaylist(pState)
                       pState = mp3player.playNextTrack(pState)
                       
                       oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
            except Exception as e:
                print(e)
            finally:
                await asyncio.sleep(0)

   
async def main():
    global pState
    oled.updateScreen(None, "Loading...", "CARVAAN")
    mp3player.stopPlayer()
    oled.displayOn()
    track_task  = asyncio.create_task(next_previous_hndlr())
    mode_task  = asyncio.create_task(mode_handler())
    rotary_task  = asyncio.create_task(rotary_control_hndlr())
    busy_pin = asyncio.create_task(monitor_player_state())


    pState.current_mode="ARTISTS"
    pState.current_selected_album="Lata Mangeshkar"
    pState.rotary_button_mode = "SELECT_ARTISTS"


    pState = mp3player.loadPlaylist(pState)
    pState = mp3player.playNextTrack(pState)
    oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
    await asyncio.gather(track_task,mode_task,rotary_task,busy_pin)

def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        print("Here")
        asyncio.new_event_loop()

run()
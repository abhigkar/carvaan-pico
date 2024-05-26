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
from irremote import irRemote

pState = PlayerState()
oled = oledScreen()
mp3player = player(pState.volume)
ir_remote = irRemote()


timeout_interval = 0

album_knob = rotaryio.IncrementalEncoder(board.GP0, board.GP1)
album_knob_button = digitalio.DigitalInOut(board.GP2)
album_knob_button.direction = digitalio.Direction.INPUT
album_knob_button.pull = digitalio.Pull.UP


volume_knob = rotaryio.IncrementalEncoder(board.GP19, board.GP20)
volume_knob_button = digitalio.DigitalInOut(board.GP21)
volume_knob_button.direction = digitalio.Direction.INPUT
volume_knob_button.pull = digitalio.Pull.UP

def checkScreenTimeout():
    global timeout_interval
    if(timeout_interval != 0):
        if(ticks_less(timeout_interval,ticks_ms())):
            oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
            timeout_interval = 0

def setPlayerVolume(direction, step = 1):
    global pState
    if direction == "VOL_UP":
        pState.volume = pState.volume + step
        if(pState.volume <= 30):
            mp3player.setVolume(pState.volume)
        else:
            pState.volume = 30
    elif direction == "VOL_DOWN":
        pState.volume = pState.volume - step
        if(pState.volume >= 0):
            mp3player.setVolume(pState.volume)
        else:
            pState.volume = 0
    oled.updateScreen(str(pState.volume) , "", "VOLUME")

def togglePlayPause():
    global pState
    if (pState.volume_knob_action == "PLAY"):
        #pause the player
        mp3player.pauseTrack()
        pState.volume_knob_action = "PAUSE"
    else:
        # resume the player
        mp3player.resumeTrack()
        pState.volume_knob_action = "PLAY"

def setPlayerMode(playerMode):
    global pState
    flag = False
    if playerMode == "ARTISTS":
        if(pState.current_mode != "ARTISTS"):
            pState.current_mode="ARTISTS"
            pState.current_selected_album="Lata Mangeshkar"
            flag=True
    elif playerMode == "MOODS":
        if(pState.current_mode != "MOODS"):
            pState.current_selected_album="Happy"
            pState.current_mode="MOODS"
            flag=True
    elif playerMode == "GEETMALA":
        if(pState.current_mode != "GEETMALA"):
            pState.current_selected_album="GEETMALA 1952-1955 VOL. 1"
            pState.current_mode = "GEETMALA"
            flag=True
    if(flag):
        pState = mp3player.resetPlaylist(pState)
        pState = mp3player.loadPlaylist(pState)
        pState = mp3player.playNextTrack(pState)
        oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)

def navigateTracks(direction):
    global pState
    global timeout_interval
    if direction == "PREVIOUS":
        if(len(pState.play_history) == 0):
            mp3player.stopPlayer()
            timeout_interval = ticks_ms() + 1000*5
            oled.updateScreen("No Previous Song", "", "")
        else:
            pState = mp3player.playPreviousTrack(pState)
            oled.updateScreen(pState.current_playing_song,None,None)
        
    elif direction == "NEXT":
        pState.play_history.append(pState.current_track)
        pState = mp3player.playNextTrack(pState)
        oled.updateScreen(pState.current_playing_song,None,None)

def setAlbum(direction):
    global pState
    if(pState.current_mode == "ARTISTS"):
        #ARTISCS
        if(direction == "NEXTALBUM"):
            #
            print("Select next album")
            pState.current_artists_playlist_index = pState.current_artists_playlist_index + 1
            if(pState.current_artists_playlist_index >= pState.max_artists):
                pState.current_artists_playlist_index = 0
        elif (direction == "PREVIOUSALBUM"):
            #
            print("Select previous album")
            pState.current_artists_playlist_index = pState.current_artists_playlist_index -1
            if(pState.current_artists_playlist_index < 0):
                pState.current_artists_playlist_index = pState.max_artists-1
    elif(pState.current_mode == "MOODS"):
        #MOODS
         if(direction == "NEXTALBUM"):
            #
            print("Select next mood")
            pState.current_moods_playlist_index = pState.current_moods_playlist_index + 1
            if(pState.current_moods_playlist_index >= pState.max_moods):
                pState.current_moods_playlist_index = 0
         elif (direction == "PREVIOUSALBUM"):
            #
            print("Select previous mood")
            pState.current_moods_playlist_index = pState.current_moods_playlist_index -1
            if(pState.current_moods_playlist_index < 0):
                pState.current_moods_playlist_index = pState.max_moods-1
    elif(pState.current_mode == "GEETMALA"):
        #GEETMALA
         if(direction == "NEXTALBUM"):
            #
            print("Select next geetmala")
            pState.current_geetmala_playlist_index = pState.current_geetmala_playlist_index + 1
            if(pState.current_geetmala_playlist_index >= pState.max_geetmala):
                pState.current_geetmala_playlist_index = 0
         elif (direction == "PREVIOUSALBUM"):
            #
            print("Select previous geetmala")
            pState.current_geetmala_playlist_index = pState.current_geetmala_playlist_index -1
            if(pState.current_geetmala_playlist_index <  0):
                pState.current_geetmala_playlist_index = pState.max_geetmala-1
        
    pState = mp3player.loadPlaylist(pState)
    pState = mp3player.playNextTrack(pState)
    oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
    
    
    
async def ir_hndlr():
    global pState
    global timeout_interval
    while True:
        try:
            checkScreenTimeout()
            cmd = ir_remote.getCommand()
            if cmd is not None:
                print("IR COMMAND " + cmd)
                if cmd == "VOL_UP" or cmd == "VOL_DOWN":              
                    setPlayerVolume(cmd)
                    timeout_interval = ticks_ms() + 1000*5
                elif cmd == "ARTISTS" or cmd == "MOODS" or cmd == "GEETMALA":
                    setPlayerMode(cmd)
                elif cmd == "PLAYPAUSE":
                    togglePlayPause()
                elif cmd == "PREVIOUS" or cmd == "NEXT":
                    navigateTracks(cmd)
                elif cmd == "NEXTALBUM" or cmd == "PREVIOUSALBUM":
                    setAlbum(cmd)

        except Exception as e:
            print("Error in ir_hndlr")
            print(e)
        finally:
             await asyncio.sleep(0)
    
async def monitor_player_state():
    global pState
    while True:
        try:
            if (not mp3player.IsPlaying() and pState.volume_knob_action != "PAUSE"):
                pState = mp3player.playNextTrack(pState)
                pState.play_history.append(pState.current_track)
                oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
            oled.updateIcon(str(pState.current_track))
        except Exception as e:
            print("Error in monitor_player_state")
            print(e)
        finally:
             await asyncio.sleep(0)

async def volume_knob_hndlr():
    global timeout_interval
    global pState
    while True:
        try:
            #handle timer timeout
            checkScreenTimeout()
            # handle rotary movement
            position = volume_knob.position
            if (position != pState.volume_knob_last_position) :
                if(position > pState.volume_knob_last_position):
                    setPlayerVolume("VOL_UP")
                elif (position < pState.volume_knob_last_position):
                    setPlayerVolume("VOL_DOWN")
                # set timer
                timeout_interval = ticks_ms() + 1000*5

            pState.volume_knob_last_position = position
            
            # handle rotary button
            if not volume_knob_button.value and pState.volume_knob_button_state is None:
                pState.volume_knob_button_state = "pressed"
            if volume_knob_button.value and pState.volume_knob_button_state == "pressed":
                print("volume rotary_button pressed.")
                togglePlayPause()
                pState.volume_knob_button_state = None
        except Exception as e:
            print("Error in volume_knob_hndlr")
            print(e)
        finally:
            await asyncio.sleep(0)

async def album_knob_hndlr():
    global timeout_interval
    global pState
    while True:
        try:
            checkScreenTimeout()
            position = album_knob.position
            if position != pState.album_knob_last_position:
                if(position > pState.volume_knob_last_position):
                    setAlbum("NEXTALBUM")
                elif (position < pState.volume_knob_last_position):
                    setAlbum("PREVIOUSALBUM")
            pState.album_knob_last_position = position
            
            if not album_knob_button.value and pState.album_knob_button_state is None:
                pState.album_knob_button_state = "pressed"
            if album_knob_button.value and pState.album_knob_button_state == "pressed":
                print("album_knob rotary_button pressed.")
                pState.album_knob_button_state = None
        except Exception as e:
            print("Error in album_knob_hndlr")
            print(e)
        finally:
            await asyncio.sleep(0)

async def next_previous_hndlr():
    button_pins = (board.GP9, board.GP10)
    global timeout_interval
    global pState
    with keypad.Keys(button_pins, value_when_pressed=False,pull=True) as keys:
        while True:
            try:
                checkScreenTimeout()
                key_event  = keys.events.get()
                if key_event and key_event.pressed:
                    key_number = key_event.key_number
                    if key_number == 0:
                        navigateTracks("PREVIOUS")
                    elif key_number == 1:
                        navigateTracks("NEXT")
            except Exception as e:
                print("Error in next_previous_hndlr")
                print(e)
            finally:
                await asyncio.sleep(0)
 
async def mode_handler():
    global pState
    button_pins = (board.GP6, board.GP7, board.GP8)
    with keypad.Keys(button_pins, value_when_pressed=False,pull=True) as keys:
        while True:
            try:
                key_event  = keys.events.get()
                if key_event and key_event.pressed:
                    key_number = key_event.key_number
                    if key_number == 0:
                        setPlayerMode("ARTISTS")
                    elif key_number == 1:
                        setPlayerMode("MOODS")
                    elif key_number == 2:
                        setPlayerMode("GEETMALA")
            except Exception as e:
                print("Error in mode_handler")
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
    album_knob_task  = asyncio.create_task(album_knob_hndlr())
    volume_knob_task = asyncio.create_task(volume_knob_hndlr())
    busy_pin_task = asyncio.create_task(monitor_player_state())
    ir_task = asyncio.create_task(ir_hndlr())


    pState.current_mode="ARTISTS"
    pState.current_selected_album="Lata Mangeshkar"
  

    pState = mp3player.loadPlaylist(pState)
    pState = mp3player.playNextTrack(pState)
    oled.updateScreen(pState.current_playing_song, pState.current_selected_album, pState.current_mode)
    await asyncio.gather(track_task, mode_task, album_knob_task, volume_knob_task, busy_pin_task, ir_task)

def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        asyncio.new_event_loop()

run()


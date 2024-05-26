import digitalio
import board
import random
import busio
import time
from DYPlayer import DYPlayer
from playindex import  artistPlayList, moodsPlayList, geetmalaPlayList
import gc 
class player:
    
    def __init__(self,vol):
        self._player_busy = digitalio.DigitalInOut(board.GP18)
        self._player_busy.direction = digitalio.Direction.INPUT
        self._player_busy.pull = digitalio.Pull.DOWN
        
        _uart = busio.UART(board.GP4,board.GP5,baudrate=9600)
        self._dyplayer = DYPlayer(_uart, volume=vol)
        self._mp3s = []
    
    def _setup(self):
        pass
        
    def resetPlaylist(self,pState):
        pState.play_history=[]
        pState.current_track=0;
        return pState
    
    def loadPlaylist(self,pState):
        playfile =""
        if(pState.current_mode == "ARTISTS"):
            r=artistPlayList[pState.current_artists_playlist_index]
            pState.current_selected_album = r[0]
            playfile=r[1]
        elif(pState.current_mode == "MOODS"):
            r=moodsPlayList[pState.current_moods_playlist_index]
            pState.current_selected_album = r[0]
            playfile=r[1]
        else:
            r=geetmalaPlayList[pState.current_geetmala_playlist_index]
            pState.current_selected_album = r[0]
            playfile=r[1]
        if(playfile != ""):
            print(playfile)
            print(pState.current_track)
            self._mp3s=[]
            with open("playlist/"+playfile) as file:
                self._mp3s=file.readlines()
            if(pState.current_mode == "GEETMALA"):
                pState.current_track=int(self._mp3s[0].split(',')[0]) - 1
            self._dyplayer.stop()
        return pState
        
    def _getNextSong(self):
        s=random.choice(self._mp3s).split(',')
        return int(s[0]),s[1]
    
    def _getGeetmalaNextSong(self,pState):
        print(pState.current_track)
        print(len(self._mp3s))
        if(pState.current_track > 5025): pState.current_track = 4381 # geetmala tracks starts from 4382 to 5025
        k=list(filter(lambda s: s.startswith("0"+str(pState.current_track+1)), self._mp3s))[0].split(',')
        return int(k[0]),k[1]
    
    def _getPreviousSong(self,pState):
        if(len(pState.play_history) == 0):
            return None,None
        g=pState.play_history.pop()
        k=list(filter(lambda s: s.startswith('{:05}'.format(g)), self._mp3s))[0].split(',')
        if(len(k) == 0):
            return None, None
        return int(k[0]),k[1]
        
    def playNextTrack(self,pState):
        if(pState.current_mode != "GEETMALA"):
            i,t = self._getNextSong()
        else:
            i,t = self._getGeetmalaNextSong(pState)
        self._dyplayer.stop()
        time.sleep(0.500)
        self._dyplayer.playSpecified(i)
        while (not self.IsPlaying()):
            pass
        pState.current_track=i
        pState.current_playing_song=t
        return pState
        
    def playPreviousTrack(self,pState):
        i,t=self._getPreviousSong(pState)
        self._dyplayer.stop()
        time.sleep(0.500)
        self._dyplayer.playSpecified(i)
        while (not self.IsPlaying()):
            pass
        pState.current_track=i
        pState.current_playing_song=t
        return pState
        
    def pauseTrack(self):
        self._dyplayer.pause()
        
    def resumeTrack(self):
        self._dyplayer.play() #self._dyplayer.resume()
        while (not self.IsPlaying()):
            pass
    
    def stopPlayer(self):
        self._dyplayer.stop()
    
    def IsPlaying(self):
        return self._player_busy.value == False
    
    def IsPlayingUART(self):
        pass
    
    def setVolume(self,volume):
        self._dyplayer.setVolume(volume)
        
    def getVolume(self):
        pass
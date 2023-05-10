class PlayerState:
    
    def __init__(self):
        self.currentArtist = ""
        self.rotary_last_position = None
        self.rotary_button_state = None
        self.volume = 70
        self.rotary_button_mode = None
        self.current_track=1;
        self.current_artists_playlist_index=0
        self.current_moods_playlist_index=0
        self.current_geetmala_playlist_index=0
        self.current_selected_album=""
        self.current_mode=""
        self.current_playing_song=""
        self.play_history=[]
        self.max_artists = 23
        self.max_moods = 9
        self.max_geetmala = 50
        
    def loadPlayerState(self):
        pass
    
    def savePlayerState(self):
        pass
        
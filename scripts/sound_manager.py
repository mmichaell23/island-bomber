import pygame
import os

class SoundManager:
    def __init__(self):
        # Initialize pygame mixer
        try:
            pygame.mixer.init()
            self.mixer_initialized = True
        except Exception as e:
            print(f"Warning: Could not initialize sound mixer: {e}")
            self.mixer_initialized = False
        
        # Sound volume settings
        self.master_volume = 0.7  # 70% volume
        self.sfx_volume = 1.0
        self.is_muted = False
        
        # Sound dictionary
        self.sounds = {}
        
        # Load all sounds
        self.load_sounds()
        
    def load_sounds(self):
        """Load all sound files from the assets directory"""
        if not self.mixer_initialized:
            print("Sound mixer not initialized, skipping sound loading")
            return
            
        try:
            # Define sound files to load
            sound_files = {
                'throw': 'throw.wav',
                'explosion': 'explosion.wav',
                'powerup': 'powerup.wav',
                'hit': 'hit.wav',
                'game_over': 'game_over.wav'
            }
            
            # Load each sound file if it exists
            for sound_name, file_name in sound_files.items():
                file_path = os.path.join('assets', file_name)
                try:
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                        # Set initial volume
                        self.sounds[sound_name].set_volume(self.master_volume * self.sfx_volume)
                    else:
                        print(f"Warning: Sound file '{file_path}' not found or empty.")
                except Exception as e:
                    print(f"Warning: Could not load sound '{file_path}': {e}")
                    
            print(f"Loaded {len(self.sounds)} sound files.")
        except Exception as e:
            print(f"Error loading sounds: {e}")
            
    def play(self, sound_name):
        """Play a sound by name"""
        if not self.mixer_initialized or self.is_muted:
            return
            
        try:
            if sound_name in self.sounds:
                self.sounds[sound_name].play()
            else:
                # Don't print warning for every attempt to play a missing sound
                pass
        except Exception as e:
            print(f"Warning: Could not play sound '{sound_name}': {e}")
        
    def set_master_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        if not self.mixer_initialized:
            return
            
        try:
            self.master_volume = max(0.0, min(1.0, volume))
            self.update_volumes()
        except Exception as e:
            print(f"Warning: Could not set master volume: {e}")
        
    def set_sfx_volume(self, volume):
        """Set SFX volume (0.0 to 1.0)"""
        if not self.mixer_initialized:
            return
            
        try:
            self.sfx_volume = max(0.0, min(1.0, volume))
            self.update_volumes()
        except Exception as e:
            print(f"Warning: Could not set SFX volume: {e}")
        
    def toggle_mute(self):
        """Toggle mute state"""
        self.is_muted = not self.is_muted
        return self.is_muted
        
    def update_volumes(self):
        """Update volume for all sounds"""
        if not self.mixer_initialized:
            return
            
        try:
            for sound in self.sounds.values():
                sound.set_volume(self.master_volume * self.sfx_volume)
        except Exception as e:
            print(f"Warning: Could not update volumes: {e}")

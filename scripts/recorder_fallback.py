import pygame
import os
import time
from datetime import datetime
import threading
import subprocess
import imageio
import numpy as np

class GameRecorder:
    """Fallback recorder that uses imageio for more reliable video encoding"""
    def __init__(self):
        self.recording = False
        self.record_button_rect = pygame.Rect(10, 190, 120, 30)
        self.record_button_color = (200, 0, 0)  # Red when not recording
        self.record_text = "Start Recording"
        self.frame_skip = 3  # Increased frame skip to reduce lag (capture every 3rd frame)
        self.frame_counter = 0
        self.save_thread = None
        self.last_capture_time = 0
        self.frame_rate = 30
        self.capture_interval = 1.0 / (self.frame_rate / self.frame_skip)  # Adjusted interval
        self.frames_captured = 0
        self.recording_start_time = 0
        self.temp_dir = "records/temp"
        self.frame_number = 0
        self.frames = []  # Store frames in memory
        
        # 720p resolution (1280x720)
        self.recording_width = 1280
        self.recording_height = 720
        
        # Create records directory if it doesn't exist
        os.makedirs("records", exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Check if ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.ffmpeg_available = True
            print("ffmpeg detected, using external encoder")
        except FileNotFoundError:
            self.ffmpeg_available = False
            print("ffmpeg not found, using imageio encoder")
        
    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            # Clear temp directory
            for file in os.listdir(self.temp_dir):
                try:
                    os.remove(os.path.join(self.temp_dir, file))
                except:
                    pass
                
            self.frames = []
            self.frames_captured = 0
            self.frame_number = 0
            self.recording_start_time = time.time()
            self.record_button_color = (0, 200, 0)  # Green when recording
            self.record_text = "Stop Recording"
            self.last_capture_time = time.time()
            print("Recording started at 720p...")
        else:
            # Save the recording in a separate thread
            if self.frames_captured > 0:
                if self.save_thread and self.save_thread.is_alive():
                    print("Still saving previous recording, please wait...")
                    return
                
                self.save_thread = threading.Thread(target=self.save_recording)
                self.save_thread.daemon = True
                self.save_thread.start()
            else:
                print("No frames were captured, nothing to save")
                
            self.record_button_color = (200, 0, 0)  # Red when not recording
            self.record_text = "Start Recording"
    
    def capture_frame(self, screen):
        if not self.recording:
            return
            
        # Check if enough time has passed since last capture
        current_time = time.time()
        if current_time - self.last_capture_time < self.capture_interval:
            return
            
        # Skip frames to reduce lag
        self.frame_counter += 1
        if self.frame_counter % self.frame_skip != 0:
            return
            
        self.last_capture_time = current_time
            
        try:
            # Scale the screen to 720p for recording
            screen_width, screen_height = screen.get_size()
            
            # Only scale if needed
            if screen_width != self.recording_width or screen_height != self.recording_height:
                small_screen = pygame.transform.scale(
                    screen, 
                    (self.recording_width, self.recording_height)
                )
            else:
                small_screen = screen
            
            # Save frame as JPG file (more efficient than PNG)
            frame_filename = os.path.join(self.temp_dir, f"frame_{self.frame_number:06d}.jpg")
            pygame.image.save(small_screen, frame_filename)
            self.frame_number += 1
            self.frames_captured += 1
            
            # Clean up old frames if we have too many (to prevent disk space issues)
            if self.frames_captured > 3000:  # Limit to ~100 seconds at 30fps
                print("Warning: Recording length limit reached")
                self.toggle_recording()
                
        except Exception as e:
            print(f"Error capturing frame: {e}")
    
    def save_recording(self):
        """Convert the captured frames to a video using imageio"""
        if self.frames_captured == 0:
            print("No frames to save.")
            return
            
        print(f"Saving {self.frames_captured} frames...")
        
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"records/game_recording_{timestamp}.mp4"
            
            if self.ffmpeg_available:
                # Use ffmpeg to convert frames to video (much more reliable)
                cmd = [
                    "ffmpeg",
                    "-y",  # Overwrite output file if it exists
                    "-framerate", str(self.frame_rate // self.frame_skip),
                    "-i", os.path.join(self.temp_dir, "frame_%06d.jpg"),
                    "-c:v", "libx264",
                    "-preset", "ultrafast",  # Use faster encoding
                    "-pix_fmt", "yuv420p",
                    "-crf", "23",  # Quality setting (lower is better)
                    output_filename
                ]
                
                print("Running ffmpeg to create video...")
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if process.returncode == 0:
                    print(f"Recording saved to {output_filename}")
                else:
                    print(f"Error creating video: {process.stderr.decode()}")
                    self.save_with_imageio(output_filename)
            else:
                # Use imageio to create video
                self.save_with_imageio(output_filename)
                
        except Exception as e:
            print(f"Error saving recording: {e}")
            
        # Reset frame counter
        self.frames_captured = 0
        
    def save_with_imageio(self, output_filename):
        """Save video using imageio"""
        try:
            print("Using imageio to create video...")
            
            # Get list of frame files
            frame_files = sorted([
                os.path.join(self.temp_dir, f) 
                for f in os.listdir(self.temp_dir) 
                if f.startswith("frame_") and f.endswith(".jpg")
            ])
            
            if not frame_files:
                print("No frame files found")
                return
                
            # Create writer with higher quality and faster encoding
            writer = imageio.get_writer(
                output_filename, 
                fps=self.frame_rate//self.frame_skip,
                quality=7,  # Higher quality (0-10)
                macro_block_size=8  # Smaller blocks for better quality
            )
            
            # Add frames in batches to improve performance
            batch_size = 30
            for i in range(0, len(frame_files), batch_size):
                batch = frame_files[i:i+batch_size]
                for frame_file in batch:
                    try:
                        img = imageio.imread(frame_file)
                        writer.append_data(img)
                    except Exception as e:
                        print(f"Error adding frame {frame_file}: {e}")
            
            # Close writer
            writer.close()
            print(f"Recording saved to {output_filename}")
            
        except Exception as e:
            print(f"Error saving with imageio: {e}")
            print("Saving individual frames only")
    
    def draw_button(self, screen):
        # Position button in bottom right corner for fullscreen compatibility
        screen_width, screen_height = screen.get_size()
        button_width, button_height = 150, 40
        margin = 20
        
        # Update button position for current screen size
        self.record_button_rect = pygame.Rect(
            screen_width - button_width - margin,
            screen_height - button_height - margin,
            button_width, 
            button_height
        )
        
        # Draw record button with semi-transparent background
        button_bg = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        button_bg.fill((0, 0, 0, 150))  # Semi-transparent black
        screen.blit(button_bg, self.record_button_rect)
        
        # Draw colored border based on recording state
        pygame.draw.rect(screen, self.record_button_color, self.record_button_rect, 2)
        
        # Draw text
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.record_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.record_button_rect.center)
        screen.blit(text_surface, text_rect)
        
        # Draw recording indicator if recording
        if self.recording:
            # Draw red circle
            pygame.draw.circle(screen, (255, 0, 0), 
                             (self.record_button_rect.left - 15, self.record_button_rect.centery), 
                             8)
            
            # Draw recording time
            if self.recording_start_time > 0:
                recording_time = time.time() - self.recording_start_time
                time_text = f"{recording_time:.1f}s"
                time_surface = font.render(time_text, True, (255, 0, 0))
                screen.blit(time_surface, (self.record_button_rect.left - 60, self.record_button_rect.centery - 10))
            
            # Draw frames captured and resolution
            frames_text = f"{self.frames_captured} frames (720p)"
            frames_surface = font.render(frames_text, True, (255, 200, 200))
            screen.blit(frames_surface, (self.record_button_rect.left - 120, self.record_button_rect.centery + 10))
    
    def check_button_click(self, pos):
        return self.record_button_rect.collidepoint(pos)

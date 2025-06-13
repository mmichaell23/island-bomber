import pygame
import cv2
import numpy as np
import os
import time
from datetime import datetime
import threading
import queue

class GameRecorder:
    def __init__(self):
        self.recording = False
        self.frame_queue = queue.Queue(maxsize=1000)  # Queue to store frames
        self.frame_rate = 30
        self.record_button_rect = pygame.Rect(10, 190, 120, 30)
        self.record_button_color = (200, 0, 0)  # Red when not recording
        self.record_text = "Start Recording"
        self.frame_skip = 2  # Only capture every nth frame to reduce lag
        self.frame_counter = 0
        self.save_thread = None
        self.last_capture_time = 0
        self.capture_interval = 1.0 / self.frame_rate  # Time between frame captures
        self.frames_captured = 0
        self.recording_start_time = 0
        
        # Create records directory if it doesn't exist
        os.makedirs("records", exist_ok=True)
        
    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            # Clear the frame queue
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break
                    
            self.frames_captured = 0
            self.recording_start_time = time.time()
            self.record_button_color = (0, 200, 0)  # Green when recording
            self.record_text = "Stop Recording"
            self.last_capture_time = time.time()
            print("Recording started...")
            
            # Start the recording thread if not already running
            if self.save_thread is None or not self.save_thread.is_alive():
                self.save_thread = threading.Thread(target=self.process_frames)
                self.save_thread.daemon = True
                self.save_thread.start()
        else:
            # Signal the recording thread to save the video
            if self.frames_captured > 0:
                print(f"Stopping recording with {self.frames_captured} frames captured")
                self.frame_queue.put(None)  # Signal to save the video
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
            # Convert pygame surface to numpy array more efficiently
            screen_width, screen_height = screen.get_size()
            scale_factor = 0.5  # Reduce resolution by half for recording
            
            # Scale down the screen for recording
            small_screen = pygame.transform.scale(
                screen, 
                (int(screen_width * scale_factor), int(screen_height * scale_factor))
            )
            
            # Convert to numpy array
            frame = pygame.surfarray.array3d(small_screen)
            
            # Swap the axes because pygame and OpenCV use different coordinate systems
            frame = np.swapaxes(frame, 0, 1)
            
            # Add frame to queue
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
                self.frames_captured += 1
            else:
                print("Warning: Frame queue is full, dropping frame")
        except Exception as e:
            print(f"Error capturing frame: {e}")
    
    def process_frames(self):
        """Process frames from the queue and save video when recording stops"""
        frames = []
        video_writer = None
        
        while True:
            try:
                # Get frame from queue with timeout
                frame = self.frame_queue.get(timeout=1.0)
                
                # None signals end of recording
                if frame is None:
                    break
                    
                # Store frame
                frames.append(frame)
                
                # If we have enough frames, start writing to disk to save memory
                if len(frames) >= 300:  # Start writing after 10 seconds (at 30 fps)
                    if video_writer is None:
                        # Generate filename with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"records/game_recording_{timestamp}.mp4"
                        
                        # Get dimensions from the first frame
                        height, width = frames[0].shape[:2]
                        
                        # Initialize video writer with a more efficient codec
                        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
                        video_writer = cv2.VideoWriter(filename, fourcc, self.frame_rate, (width, height))
                    
                    # Write frames to disk
                    for f in frames:
                        # Convert from RGB to BGR (OpenCV uses BGR)
                        f_bgr = cv2.cvtColor(f, cv2.COLOR_RGB2BGR)
                        video_writer.write(f_bgr)
                    
                    # Clear frames to save memory
                    frames = []
                    
            except queue.Empty:
                # Queue timeout, continue waiting if still recording
                if not self.recording and len(frames) == 0:
                    break
                continue
            except Exception as e:
                print(f"Error processing frames: {e}")
                
        # Save any remaining frames
        try:
            if len(frames) > 0:
                # Generate filename with timestamp if not already created
                if video_writer is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"records/game_recording_{timestamp}.mp4"
                    
                    # Get dimensions from the first frame
                    height, width = frames[0].shape[:2]
                    
                    # Initialize video writer with a more efficient codec
                    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
                    video_writer = cv2.VideoWriter(filename, fourcc, self.frame_rate, (width, height))
                
                # Write remaining frames
                for f in frames:
                    # Convert from RGB to BGR (OpenCV uses BGR)
                    f_bgr = cv2.cvtColor(f, cv2.COLOR_RGB2BGR)
                    video_writer.write(f_bgr)
                    
                print(f"Wrote {len(frames)} remaining frames")
        except Exception as e:
            print(f"Error saving remaining frames: {e}")
            
        # Release video writer
        if video_writer is not None:
            video_writer.release()
            print(f"Recording saved to {filename}")
            
        # Reset frame counter
        self.frames_captured = 0
    
    def save_recording(self):
        """Legacy method - now handled by process_frames"""
        pass
    
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
            
            # Draw frames captured
            frames_text = f"{self.frames_captured} frames"
            frames_surface = font.render(frames_text, True, (255, 200, 200))
            screen.blit(frames_surface, (self.record_button_rect.left - 60, self.record_button_rect.centery + 10))
    
    def check_button_click(self, pos):
        return self.record_button_rect.collidepoint(pos)

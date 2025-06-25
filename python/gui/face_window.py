import pygame
import math
import random
from threading import Thread, Event
import time
import signal

class FaceWindow:
    def __init__(self):
        pygame.init()
        self.width = 640
        self.height = 475
        # Add NOFRAME flag to create borderless window
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)
        pygame.display.set_caption("Max Assistant")
        # Hide cursor
        pygame.mouse.set_visible(False)
        
        # Setup signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (50, 150, 255)
        
        # Eye properties
        self.eye_radius = 30
        self.pupil_radius = 15
        self.left_eye_pos = (self.width // 3, self.height // 2)
        self.right_eye_pos = (2 * self.width // 3, self.height // 2)
        
        # Animation states
        self.blink_progress = 0
        self.is_blinking = False
        self.look_offset = [0, 0]
        self.border_pulse = 0
        self.is_listening = False
        
        # Control
        self.running = True
        self.update_thread = Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def _signal_handler(self, sig, frame):
        print("\nClosing face window...")
        self.close()

    def _update_loop(self):
        clock = pygame.time.Clock()
        last_blink = time.time()
        
        while self.running:
            current_time = time.time()
            
            # Random blinking
            if not self.is_blinking and current_time - last_blink > random.uniform(2.0, 5.0):
                self.is_blinking = True
                last_blink = current_time
            
            # Blink animation
            if self.is_blinking:
                self.blink_progress += 0.15
                if self.blink_progress >= 1.0:
                    self.blink_progress = 0
                    self.is_blinking = False
            
            # Random eye movement
            if random.random() < 0.02:
                self.look_offset = [random.uniform(-10, 10), random.uniform(-10, 10)]
            
            # Border pulse effect
            if self.is_listening:
                self.border_pulse = (self.border_pulse + 0.1) % (2 * math.pi)
            
            self._draw()
            clock.tick(60)

    def _draw(self):
        self.screen.fill(self.BLACK)
        
        # Draw border effect when listening
        if self.is_listening:
            pulse = abs(math.sin(self.border_pulse))
            border_color = (int(self.BLUE[0] * pulse), 
                          int(self.BLUE[1] * pulse), 
                          int(self.BLUE[2] * pulse))
            pygame.draw.rect(self.screen, border_color, 
                           (0, 0, self.width, self.height), 5)
        
        # Draw eyes
        for eye_pos in [self.left_eye_pos, self.right_eye_pos]:
            # Eye white
            blink_squish = 1.0 - (math.sin(self.blink_progress * math.pi) * 1.9 if self.is_blinking else 0)  # Changed from 0.95 to 1.9
            pygame.draw.ellipse(self.screen, self.WHITE,
                              (eye_pos[0] - self.eye_radius,
                               eye_pos[1] - self.eye_radius * blink_squish,
                               self.eye_radius * 2,
                               self.eye_radius * 2 * blink_squish))
            
            # Pupil
            if not self.is_blinking:
                pupil_pos = (eye_pos[0] + self.look_offset[0],
                           eye_pos[1] + self.look_offset[1])
                pygame.draw.circle(self.screen, self.BLACK, 
                                 (int(pupil_pos[0]), int(pupil_pos[1])),
                                 self.pupil_radius)
        
        pygame.display.flip()

    def set_listening(self, is_listening):
        self.is_listening = is_listening

    def close(self):
        self.running = False
        pygame.mouse.set_visible(True)  # Restore cursor visibility
        pygame.quit()

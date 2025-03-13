import pygame
import math
import time
from dataclasses import dataclass
from typing import Tuple, List

# Aircraft data structure
@dataclass
class Aircraft:
    callsign: str
    x: float
    y: float
    altitude: float  # in feet
    heading: float  # in degrees
    speed: float    # in knots
    status: str  # 'landing', 'takeoff', 'cruising'
    color: Tuple[int, int, int]
    landing_sequence: int = 0  # Order in landing sequence, 0 = not landing
    target_heading: float = 0  # Target heading for smooth turns
    initial_target_heading: float = 0  # Initial target heading for landing aircraft
    
    def move(self, dt):
        # Handle smooth turning with proper rate
        if abs(self.heading - self.target_heading) > 1:
            # Calculate turn direction
            diff = (self.target_heading - self.heading + 360) % 360
            if diff > 180:
                self.heading = (self.heading - TURN_RATE * dt + 360) % 360
            else:
                self.heading = (self.heading + TURN_RATE * dt) % 360
        
        # Move aircraft forward in current heading direction
        rad = math.radians((90 - self.heading) % 360)
        self.x += math.cos(rad) * self.speed * dt * SPEED_MULTIPLIER
        self.y -= math.sin(rad) * self.speed * dt * SPEED_MULTIPLIER

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1600, 1000  # More reasonable window size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air Traffic Control Simulation")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)

# Flight parameters
LANDING_SPEED = 140  # Target landing speed in knots
APPROACH_ALTITUDE = 3000  # Initial approach altitude in feet
DESCENT_RATE = 20 * 5  # Increased for faster simulation
DECELERATION = 0.5 * 5  # Increased for faster simulation
TURN_RATE = 2.0 * 5  # Increased for faster simulation
SPEED_MULTIPLIER = 0.005 * 5  # Increased for faster simulation

# Airport position (moved left)
AIRPORT_X = WIDTH // 2 - 200
AIRPORT_Y = HEIGHT // 2

# Runway dimensions
RUNWAY_LENGTH = 300
RUNWAY_WIDTH = 40
RUNWAY_X = AIRPORT_X - RUNWAY_LENGTH // 2
RUNWAY_Y = AIRPORT_Y - RUNWAY_WIDTH // 2

# Pattern dimensions - adjusted for proper L-shaped pattern
PATTERN_LENGTH = 300  # Distance from runway centerline to downwind leg
PATTERN_WIDTH = 200   # Distance from runway end to base leg
DOWNWIND_Y = AIRPORT_Y - PATTERN_WIDTH  # Y coordinate for downwind leg

# Turn points
RUNWAY_END_X = RUNWAY_X + RUNWAY_LENGTH  # Right end of runway
BASE_TURN_X = RUNWAY_END_X + 200  # Turn point 200 units to the right of runway end

# Initialize aircraft with proper positions for the landing pattern
aircraft = [
    # Aircraft cruising over at high altitude
    Aircraft("AC1", WIDTH * 0.3, HEIGHT * 0.3, 30000, 90, 250, "cruising", WHITE, 0, 90),
    
    # Aircraft taking off
    Aircraft("AC2", AIRPORT_X, AIRPORT_Y, 1000, 0, 150, "takeoff", WHITE, 0, 0),
    
    # Three aircraft approaching in sequence - all starting with heading 90 (east)
    # Positioned at different distances and y positions for proper sequencing
    Aircraft("AC3", AIRPORT_X - 300, DOWNWIND_Y - 50, 3000, 90, 180, "landing", WHITE, 1, 90),
    Aircraft("AC4", AIRPORT_X - 500, DOWNWIND_Y, 4000, 90, 170, "landing", WHITE, 2, 90),
    Aircraft("AC5", AIRPORT_X - 700, DOWNWIND_Y + 50, 5000, 90, 160, "landing", WHITE, 3, 90)
]

def draw_airport():
    # Runway dimensions - scaled for new window size
    runway_x = RUNWAY_X
    runway_y = RUNWAY_Y
    
    # Draw main runway rectangle
    GRAY = (128, 128, 128)
    pygame.draw.rect(screen, GRAY, (runway_x, runway_y, RUNWAY_LENGTH, RUNWAY_WIDTH))
    
    # Draw threshold piano keys (shortened)
    num_keys = 8
    key_width = RUNWAY_WIDTH // num_keys
    key_length = 30  # Shortened from 80
    
    # Left threshold
    start_y = runway_y
    for i in range(num_keys):
        if i % 2 == 0:
            y = start_y + (i * key_width)
            pygame.draw.rect(screen, WHITE, (runway_x, y, key_length, key_width))
    
    # Right threshold
    start_y = runway_y
    for i in range(num_keys):
        if i % 2 == 0:
            y = start_y + (i * key_width)
            pygame.draw.rect(screen, WHITE, (runway_x + RUNWAY_LENGTH - key_length, y, key_length, key_width))
    
    # Draw centerline (dashed) - only within runway
    dash_length = 20
    gap_length = 20
    current_x = runway_x  # Start at runway beginning
    end_x = runway_x + RUNWAY_LENGTH  # End at runway end
    
    while current_x < end_x:
        pygame.draw.line(screen, WHITE, 
                        (current_x, AIRPORT_Y),
                        (min(current_x + dash_length, end_x), AIRPORT_Y), 2)
        current_x += dash_length + gap_length
    
    # Draw runway number (smaller size) - moved left
    font = pygame.font.Font(None, 36)
    number_text = font.render("27", True, WHITE)
    rotated_text = pygame.transform.rotate(number_text, 90)
    number_rect = rotated_text.get_rect()
    number_rect.center = (runway_x + RUNWAY_LENGTH - 50, AIRPORT_Y)  # Moved left from -20 to -50
    screen.blit(rotated_text, number_rect)
    
    # Draw marker at runway end
    pygame.draw.circle(screen, RED, (int(RUNWAY_END_X), int(AIRPORT_Y)), 10)
    
    # Draw marker at turn point
    pygame.draw.circle(screen, YELLOW, (int(BASE_TURN_X), int(AIRPORT_Y)), 10)
    
    # Removed blue downwind leg line

def get_landing_pattern_position(ac, phase):
    """Calculate positions for each phase of landing pattern"""
    pattern_altitude = APPROACH_ALTITUDE + (ac.landing_sequence - 1) * 1000
    
    if phase == "downwind":
        return {
            "heading": 90,  # Flying east, parallel to runway
            "altitude": pattern_altitude,
            "speed": LANDING_SPEED + 20
        }
    elif phase == "base_turn":
        return {
            "heading": 180,  # Turn right to south
            "altitude": pattern_altitude - 500,  # Start descent
            "speed": LANDING_SPEED + 10
        }
    elif phase == "base":
        return {
            "heading": 180,  # Flying straight south
            "altitude": max(700, pattern_altitude - 1000),  # Descend to at least 700 ft
            "speed": max(70, LANDING_SPEED)  # Slow to at least 70 knots
        }
    elif phase == "final_turn":
        return {
            "heading": 270,  # Turn right to west (runway heading)
            "altitude": max(500, pattern_altitude - 1500),  # Continue descent
            "speed": max(65, LANDING_SPEED - 5)  # Continue slowing
        }
    elif phase == "final":
        # Calculate descent based on distance to runway middle
        dist_to_middle = ac.x - (AIRPORT_X)
        if dist_to_middle > 0:
            # Start at 350 ft and descend to 0 at runway middle
            target_alt = min(350, (dist_to_middle / (RUNWAY_LENGTH/2)) * 350)
        else:
            target_alt = 0
            
        return {
            "heading": 270,  # Aligned with runway
            "altitude": target_alt,
            "speed": max(60, LANDING_SPEED - 10)  # Final approach speed
        }

def redirect_aircraft(dt):
    for ac in aircraft:
        if ac.landing_sequence > 0:
            # Determine aircraft phase based on position and heading
            if abs(ac.heading - 90) < 10:  # Flying east (downwind)
                if ac.x > BASE_TURN_X:  # Using the new turn point
                    # Aircraft has passed the turn point, turn to base
                    phase = "base_turn"
                else:
                    phase = "downwind"
            elif abs(ac.heading - 180) < 10:  # Flying south (base)
                if ac.y > AIRPORT_Y:
                    # Aircraft has passed the centerline, turn to final
                    phase = "final_turn"
                else:
                    phase = "base"
            elif abs(ac.heading - 270) < 10:  # Flying west (final)
                phase = "final"
            else:
                # In the middle of a turn, maintain current phase
                if abs(ac.target_heading - 180) < 10:
                    phase = "base_turn"
                elif abs(ac.target_heading - 270) < 10:
                    phase = "final_turn"
                else:
                    phase = "downwind"
            
            # Get target parameters for current phase
            target = get_landing_pattern_position(ac, phase)
            
            # Set target heading
            ac.target_heading = target["heading"]
            
            # Debug information - comment out to reduce console spam
            # print(f"{ac.callsign}: Phase={phase}, Heading={ac.heading:.1f}, Target={ac.target_heading}, Pos=({ac.x:.1f}, {ac.y:.1f})")
            
            # Set speed and altitude targets
            desired_speed = target["speed"]
            target_altitude = target["altitude"]
            
            # Gradual speed adjustment
            if ac.speed > desired_speed:
                ac.speed = max(desired_speed, ac.speed - DECELERATION * dt)
            elif ac.speed < desired_speed - 10:
                ac.speed = min(desired_speed, ac.speed + DECELERATION * dt)
            
            # Gradual altitude adjustment
            if ac.altitude > target_altitude:
                ac.altitude = max(target_altitude, ac.altitude - DESCENT_RATE * dt)
            elif ac.altitude < target_altitude:
                ac.altitude = min(target_altitude, ac.altitude + DESCENT_RATE * dt / 2)  # Climb slower than descent

def draw_aircraft(ac: Aircraft):
    # Draw aircraft position - larger circle
    pygame.draw.circle(screen, ac.color, (int(ac.x), int(ac.y)), 8)
    
    # Draw heading line - longer
    heading_length = 40
    rad = math.radians((90 - ac.heading) % 360)
    end_x = ac.x + heading_length * math.cos(rad)
    end_y = ac.y - heading_length * math.sin(rad)
    pygame.draw.line(screen, ac.color, (ac.x, ac.y), (end_x, end_y), 3)
    
    # Draw target heading line (for debugging) - longer
    if ac.landing_sequence > 0:
        target_rad = math.radians((90 - ac.target_heading) % 360)
        target_end_x = ac.x + heading_length * 1.5 * math.cos(target_rad)
        target_end_y = ac.y - heading_length * 1.5 * math.sin(target_rad)
        pygame.draw.line(screen, GREEN, (ac.x, ac.y), (target_end_x, target_end_y), 2)
    
    # Draw detailed aircraft information - larger font
    font = pygame.font.Font(None, 36)
    info_text = f"{ac.callsign}: {int(ac.altitude)}ft | {int(ac.heading)}° | {int(ac.speed)}kts"
    if ac.landing_sequence > 0:
        info_text += f" | #{ac.landing_sequence}"
    text = font.render(info_text, True, GREEN)
    text_pos = (int(ac.x) + 15, int(ac.y) - 15)
    screen.blit(text, text_pos)

def main():
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        dt = 0.1  # Base time delta remains the same, but parameters are scaled
        screen.fill(BLACK)
        draw_airport()
        
        # Update and draw aircraft
        redirect_aircraft(dt)
        
        for ac in aircraft:
            ac.move(dt)
            draw_aircraft(ac)
        
        pygame.display.flip()
        clock.tick(60)  # Keep the frame rate the same

    pygame.quit()

if __name__ == "__main__":
    main() 
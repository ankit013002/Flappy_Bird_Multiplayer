import pygame
import random

class AdversaryBird:
    def __init__(self, x, y, bird_image, difficulty='Medium'):
        self.image = bird_image.copy()
        self.image.set_alpha(150)
        self.rect = self.image.get_rect(center=(x, y))
        self.movement = 0
        self.alive = True
        self.difficulty = difficulty
        self.flap_cooldown = 0

    def update(self, pipes, gravity):
        if self.alive:
            # Reduce flap cooldown
            if self.flap_cooldown > 0:
                self.flap_cooldown -= 1

            self.movement += gravity

            # Cap the movement speed
            max_downward_speed = 10
            max_upward_speed = -10  # Negative because upward movement is negative
            self.movement = max(min(self.movement, max_downward_speed), max_upward_speed)

            self.rect.centery += self.movement

            # Debug: Print the bird's current position and movement
            print(f"Update - Y Position: {self.rect.centery:.2f}, Movement: {self.movement:.2f}")

            self.make_decision(pipes, gravity)

            # Check for collisions
            if self.rect.top <= 0 or self.rect.bottom >= 800:
                self.alive = False
                print("Adversary died by hitting the boundary.")
            for pipe in pipes:
                if self.rect.colliderect(pipe):
                    self.alive = False
                    print("Adversary died by hitting a pipe.")

    def make_decision(self, pipes, gravity):
        if self.difficulty == 'Easy':
            self.predictive_ai(pipes, gravity, buffer=70, reaction_chance=0.5)
        elif self.difficulty == 'Medium':
            self.predictive_ai(pipes, gravity, buffer=50)
        elif self.difficulty == 'Hard':
            self.predictive_ai(pipes, gravity, buffer=30)
        elif self.difficulty == 'Godsend':
            self.predictive_ai(pipes, gravity, buffer=10)

    def predictive_ai(self, pipes, gravity, buffer, reaction_chance=1.0):
        if pipes:
            closest_pipe = self.get_closest_pipe(pipes)
            if closest_pipe and random.random() <= reaction_chance:
                gap_size = 150
                if closest_pipe.top == 0:
                    gap_top = closest_pipe.bottom
                    gap_bottom = gap_top + gap_size
                else:
                    gap_bottom = closest_pipe.top
                    gap_top = gap_bottom - gap_size

                distance_to_pipe = closest_pipe.centerx - self.rect.centerx
                pipe_speed = 5
                time_to_pipe = distance_to_pipe / pipe_speed

                # Limit the time_to_pipe to prevent looking too far ahead
                max_time_to_pipe = 60  # Adjust as needed
                time_to_pipe = max(min(time_to_pipe, max_time_to_pipe), 0)

                # Predict position without flapping
                predicted_y_no_flap = self.rect.centery + self.movement * time_to_pipe + 0.5 * gravity * time_to_pipe ** 2

                # Debug: Print decision variables
                print(f"Decision - Time to Pipe: {time_to_pipe:.2f}, Predicted Y: {predicted_y_no_flap:.2f}, Gap Bottom: {gap_bottom - buffer:.2f}")

                # Decide whether to flap
                if 0 < time_to_pipe <= max_time_to_pipe and predicted_y_no_flap > gap_bottom - buffer:
                    print("Flapping to reach the gap.")
                    self.flap()
                else:
                    print("Not flapping.")
            else:
                # Optional: Implement random flapping or maintain altitude
                pass  # Do nothing
        else:
            # No pipes ahead; do not flap unnecessarily
            pass  # Do nothing

    def get_closest_pipe(self, pipes):
        pipes_ahead = [pipe for pipe in pipes if pipe.centerx > self.rect.centerx]
        return min(pipes_ahead, key=lambda p: p.centerx) if pipes_ahead else None

    def flap(self):
        if self.flap_cooldown == 0:
            self.movement = -6
            self.flap_cooldown = 5
            # Debug: Print when the bird flaps
            print("Flap executed. Movement reset to -6.")

    def draw(self, screen):
        if self.alive:
            screen.blit(self.image, self.rect)

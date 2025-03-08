from datetime import datetime
from Config import *
import csv

def leaderboard_screen():
    move_background()
    # Display the leaderboard entries
    title_surface = font.render('Leaderboard', True, WHITE)
    title_rect = title_surface.get_rect(center=(WIDTH / 2, 50))
    SCREEN.blit(title_surface, title_rect)

    # Column headers
    name_header = font.render('Name', True, WHITE)
    time_header = font.render('Time', True, WHITE)
    score_header = font.render('Score', True, WHITE)
    
    draw_leaderboard_text(name_header, time_header, score_header, 100)

    # Display entries
    y_offset = 150
    for entry in leaderboard:
        name_text = font.render(entry['Name'], True, WHITE)
        time_text = font.render(entry['Time'], True, WHITE)
        score_text = font.render(entry['Score'], True, WHITE)
        draw_leaderboard_text(name_text, time_text, score_text, y_offset)
        y_offset += 40  # Move down for next entry
        
def draw_leaderboard_text(name, time, score, y_pos):
    SCREEN.blit(name, (200, y_pos))
    SCREEN.blit(time, (500, y_pos))
    SCREEN.blit(score, (900, y_pos))
    
def update_leader_board(name, score):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    leaderboard_entry = {'Name': name, 'Time': current_time, 'Score': str(int(score))}
    leaderboard.append(leaderboard_entry)
    leaderboard.sort(key=lambda x: int(x['Score']), reverse=True)
    save_leaderboard(leaderboard)

    
def save_leaderboard(leaderboard):
    """Save the leaderboard to the CSV file."""
    with open(leaderboard_file, mode='w', newline='') as csvfile:
        fieldnames = ['Name', 'Time', 'Score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in leaderboard:
            writer.writerow(entry)

def load_leaderboard():
    """Load the leaderboard from the CSV file."""
    try:
        with open(leaderboard_file, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    except FileNotFoundError:
        return []

leaderboard = load_leaderboard()
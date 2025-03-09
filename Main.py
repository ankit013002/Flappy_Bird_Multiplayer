from Network import Multiplayer
from Button import *
from MainScreen import *
from InputBox import *
from LeaderBoard import *
from Settings import *
from Utilities import *
from Multiplayer import *
from GameLogic import *
from GameOver import *
from PlayMultiplayer import *


def main_game_loop():
    global input_box

    # Input box
    score = 0
    pipe_list = []
    host_code = 0
    game_state = 'start'
    connection_code = 0

    connection_code_input_box = InputBox(
        WIDTH / 2 - 150, HEIGHT / 2 - 120, 300, 40, font, str(connection_code))
    input_box = InputBox(x=((WIDTH - 300) / 2), y=80, w=300, h=40, font=font)
    confirm_button = Button('Confirm', (WIDTH / 2 - 125, HEIGHT / 2 + 100),
                            (250, 60), pygame.font.Font(None, 48), WHITE, BLACK)
    connection_button = Button('Connect', (WIDTH / 2 - 125, HEIGHT / 2 + 100),
                               (250, 60), pygame.font.Font(None, 48), WHITE, BLACK)

    while True:
        if game_state == 'start':
            score = 0
            game_state, game_active, player_name = start_screen(
                input_box, pipe_list)

        elif game_state == 'play':
            game_state, score = play_state(pipe_list, score)
            if game_state == 'game_over':
                update_leader_board(player_name, score)

        elif game_state == 'game_over':
            game_state = game_over_screen_logic(score)

        elif game_state == 'leaderboard':
            game_state = leader_board_screen_logic()

        elif game_state == 'multiplayer menu':
            game_state = multiplayer_menu_logic()

        elif game_state == 'host':
            game_state, host_code = host_logic(host_code)

        elif game_state == 'join':
            game_state = join_logic(connection_code_input_box, host_code)

        elif game_state == 'play_multiplayer':
            game_state = play_multiplayer_logic()
            if game_state == 'game_over':
                update_leader_board(player_name, score)

            display_score(score)
        elif game_state == 'settings':
            game_state = settings_logic(confirm_button)

        pygame.display.update()
        clock.tick(60)


def main():
    global multiplayer

    pygame.init()
    create_main_screen()
    create_multiplayer_menu()
    create_host_screen()
    create_join_screen()

    is_host = input(
        "Do you want to host a game? (y/n): ").strip().lower() == "y"
    host_ip = None

    if not is_host:
        host_ip = input("Enter the host's IP: ").strip()

    multiplayer = Multiplayer(is_host, host_ip)

    main_game_loop()


if __name__ == "__main__":
    main()

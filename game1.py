import random
import cv2
import mediapipe as mp
import pgzrun
import sys


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

background = Actor("background")
player = Actor("ironman")
player.x = 200
player.y = 200

enemy = Actor("alien")
coin = Actor("coin", pos=(300,300))
score = 0
time = 60

hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)

WIDTH = 640
HEIGHT = 480




game_state = 0

def reset_game():
    global score, time, game_state
    game_state = 1
    score = 0
    time = 60
    player.x = 200
    player.y = 200
    enemy.x = 400
    enemy.y = 400

def gesture_control():
    if cap.isOpened():
        success, image = cap.read()
        cv2.flip(image, 1)
        if not success:
            print("Ignoring empty camera frame.")
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                data = hand_landmarks.landmark[8]
                coords = mp_drawing._normalized_to_pixel_coordinates(data.x, data.y, width, height)
                cv2.circle(image, coords, 10, (0, 255, 255), -1)
                print(coords)
                try:
                    # box.center = (WIDTH-coords[0], coords[1])
                    player.pos = (WIDTH-coords[0], coords[1])
                except Exception as e:
                    print(e)
        cv2.flip(image, 1)
        cv2.line(image, (0,350), (640,350), (255, 255, 255), 2)
        cv2.putText(image, "OPENCV + PYGAME + MEDIAPIPE", (640//3, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            cap.release()
            cv2.destroyAllWindows()
            sys.exit()




def draw():
    if game_state == 0:
        # show a welcome screen and instructions to play the game 
        screen.clear()
        screen.draw.text("Press Enter to start", (200,200), color='red')
        screen.draw.text('use gesture to control the ironman', (200,250), color='green')

    elif game_state == 1:
        screen.clear()
        background.draw()
        player.draw()
        enemy.draw()

        coin.draw()
        screen.draw.text("Gesture controll game", (200,0), color='red')
        score_string = str(score)
        screen.draw.text(score_string, (0,0), color='green')
        time_string = str(round(time))
        screen.draw.text(time_string, (50,0), color='green')
    elif game_state == 2:
        # show game over screen
        screen.clear()
        screen.draw.text("Game Over", (200,200), color='red')
        score_string = str(score)
        screen.draw.text(score_string, (200,250), color='green')
        screen.draw.text("Press Enter to play again", (200,300), color='green')


    

def update(delta):
    global score, time, game_state
    time = time - delta
    if game_state == 0 or game_state == 2:
        if keyboard.RETURN:
            reset_game()
    if game_state == 1:
        if time <= 0:
            sounds.gameover.play()
            game_state = 2
        if keyboard.right:
            player.x = player.x + 4
        if keyboard.left:
            player.x = player.x - 4
        if keyboard.down:
            player.y = player.y + 4
        if keyboard.up:
            player.y = player.y - 4
        if keyboard.RETURN:
            reset_game()

        if player.x > WIDTH:
            player.x = 0
        if player.x < 0:
            player.x = WIDTH
        if player.y < 0:
            player.y = HEIGHT
        if player.y > HEIGHT:
            player.y = 0

        if enemy.x < player.x:
            enemy.x = enemy.x + 1
        if enemy.x > player.x:
            enemy.x = enemy.x - 1
        if enemy.y < player.y:
            enemy.y = enemy.y + 1
        if enemy.y > player.y:
            enemy.y = enemy.y - 1
        if player.colliderect(enemy):
            sounds.death2.play()
            game_state = 2

        if coin.colliderect(player):
            coin.x = random.randint(0, WIDTH)
            coin.y = random.randint(0, HEIGHT)
            score = score + 1
            sounds.coin.play()
            print("Score:", score)

    gesture_control()


pgzrun.go()
    
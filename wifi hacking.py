import pygame
import cv2
import sys
import threading
import random
import pyttsx3

# Initialize pygame and set up screen
pygame.init()
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Face Activated Racing Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Load images
car_image = pygame.image.load("car_image.jpg")
car_image = pygame.transform.scale(car_image, (50, 100))
obstacle_image = pygame.image.load("obstacle.jpg")
obstacle_image = pygame.transform.scale(obstacle_image, (50, 50))

# Car
car_width, car_height = 50, 100
car = pygame.Rect(WIDTH//2 - car_width//2, HEIGHT - car_height - 10, car_width, car_height)
car_speed = 5

# Obstacles
obstacle_width, obstacle_height = 50, 50
obstacles = []
obstacle_speed = 5

# Face detection flag
face_detected = False

# Load face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Voice assistant initialization
engine = pyttsx3.init()

# Function for speech synthesis
def speak(text):
    def run_speech():
        engine.say(text)
        engine.runAndWait()

    threading.Thread(target=run_speech, daemon=True).start()

# Function for face detection
def detect_face():
    global face_detected
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        detected_now = len(faces) > 0

        # Only speak when detection status changes and game hasn't been activated
        if detected_now and not face_detected:
            face_detected = True
            speak("Face detected. Game activated.")

        # Draw rectangles and label
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), GREEN, 2)
        label = "Face Detected!" if face_detected else "No Face"
        color = GREEN if face_detected else RED
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow("Face Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Start face detection in separate thread
threading.Thread(target=detect_face, daemon=True).start()

# Function to draw obstacles
def draw_obstacles():
    for obs in obstacles:
        screen.blit(obstacle_image, (obs.x, obs.y))

# Function to spawn obstacles
def spawn_obstacle():
    x = random.randint(0, WIDTH - obstacle_width)
    return pygame.Rect(x, -obstacle_height, obstacle_width, obstacle_height)

clock = pygame.time.Clock()
spawn_timer = 0
running = True

while running:
    clock.tick(60)
    screen.fill(WHITE)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Game logic if face is detected
    if face_detected:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and car.left > 0:
            car.x -= car_speed
        if keys[pygame.K_RIGHT] and car.right < WIDTH:
            car.x += car_speed

        # Obstacle logic
        spawn_timer += 1
        if spawn_timer >= 30:
            obstacles.append(spawn_obstacle())
            spawn_timer = 0

        for obs in obstacles:
            obs.y += obstacle_speed
        obstacles = [obs for obs in obstacles if obs.y < HEIGHT]

        # Drawing obstacles and car
        draw_obstacles()
        screen.blit(car_image, (car.x, car.y))

        # Collision detection
        for obs in obstacles:
            if car.colliderect(obs):
                speak("Game Over")
                print("Game Over")
                running = False

        # Face detected banner
        pygame.draw.rect(screen, BLUE, (10, 10, 250, 30))
        font = pygame.font.SysFont(None, 24)
        screen.blit(font.render("Face Detected - Game On", True, WHITE), (20, 15))
    else:
        font = pygame.font.SysFont(None, 48)
        text = font.render("No Face Detected", True, RED)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))

    pygame.display.flip()

pygame.quit()
sys.exit()


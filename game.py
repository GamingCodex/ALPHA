#Guilty Memories 
#Deadline: 26/06/2025

import pygame
import sys
import time
import os
import random  

# Inicialización
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(os.path.join("MUSIC", "menumusic.wav"))
pygame.mixer.music.play(-1)

# Configuración general
CELL_SIZE = 110
COLS = 6
ROWS = 4
BOARD_WIDTH = CELL_SIZE * COLS
BOARD_HEIGHT = CELL_SIZE * ROWS
BOARD_X_OFFSET = 150
BOARD_Y_OFFSET = 120
SCREEN_WIDTH = BOARD_WIDTH + BOARD_X_OFFSET * 2 + 200  # Extra espacio para piezas laterales
SCREEN_HEIGHT = BOARD_HEIGHT + BOARD_Y_OFFSET * 2 + 180  # Extra espacio para diálogo abajo
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Guilty Memories")

# Cargar imágenes
icono = pygame.image.load("icono.png.jpg")
pygame.display.set_icon(icono)

background_img = pygame.image.load("background.jpg").convert()
menu_background_img = pygame.image.load("menu.jpg").convert()
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
menu_background_img = pygame.transform.scale(menu_background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# VN imágenes
vn_bg = pygame.image.load("COMISARIA.png").convert()
vn_bg = pygame.transform.scale(vn_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
protagonist_img = pygame.image.load("PROTAGONIST.png").convert_alpha()
police_img = pygame.image.load("POLICE.png").convert_alpha()

# Escalamos personajes conservando proporción (alto 600 px aprox)
def scale_keep_aspect(image, height):
    w, h = image.get_size()
    scale_factor = height / h
    new_w = int(w * scale_factor)
    return pygame.transform.smoothscale(image, (new_w, height))

def position_piece_on_side(piece):
    if piece.side == 0: # Arriba
        piece.rect.x = BOARD_X_OFFSET + piece.slot * (CELL_SIZE + 5)
        piece.rect.y = BOARD_Y_OFFSET - CELL_SIZE - 20
    elif piece.side == 1: # Abajo
        piece.rect.x = BOARD_X_OFFSET + piece.slot * (CELL_SIZE + 5)
        piece.rect.y = BOARD_Y_OFFSET + BOARD_HEIGHT + 20
    elif piece.side == 2: # Izquierda
        piece.rect.x = BOARD_X_OFFSET - CELL_SIZE - 20
        piece.rect.y = BOARD_Y_OFFSET + piece.slot * (CELL_SIZE + 5)
    elif piece.side == 3: # Derecha
        piece.rect.x = BOARD_X_OFFSET + BOARD_WIDTH + 20
        piece.rect.y = BOARD_Y_OFFSET + piece.slot * (CELL_SIZE + 5)
    piece.board_pos = None  # Aseguramos que no esté en el tablero

protagonist_img = scale_keep_aspect(protagonist_img, 600)
police_img = scale_keep_aspect(police_img, 600)

# Colores
BG_COLOR = (20, 20, 20)
BOX_COLOR = (128, 0, 128)
GRID_COLOR = (0, 255, 128)
BOARD_BORDER_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (50, 50, 50)
BUTTON_HOVER_COLOR = (80, 80, 80)
GAME_OVER_COLOR = (255, 50, 50)
BLOOD_RED = (138, 3, 3)

# Tipografías
menu_font = pygame.font.Font("DailyMemory-EBdl.ttf", 30)
big_menu_font = pygame.font.Font("DailyMemory-EBdl.ttf", 80)
small_font = pygame.font.SysFont("courier new", 20)
generic_font = pygame.font.SysFont(None, 28)  # Para VN y cronómetro

# Tiempo total (10 minutos)
TOTAL_TIME = 600

# Diálogos para puzzles
puzzle_dialogs = [
    ["No recuerdo nada...", "Estas piezas me resultan familiares...", "Tengo que entender qué pasa..."],
    ["Este lugar... ya he estado aquí, ¿no?", "Mi cabeza está confundida...", "Pero no puedo detenerme."],
    ["Un recuerdo... veo una silueta familiar.", "El dolor es intenso, pero debo recordar.", "Algo muy importante se me escapa...", "¿Por qué olvidé esto?"],
    ["Escucho una voz... me llama por mi nombre.", "Cada pieza encaja como fragmentos de memoria.", "Necesito la verdad..."],
    ["Esa imagen... es mi familia. Pero está distorsionada.", "¿Qué hice? ¿Por qué lo olvidé?"],
    ["Ya no estoy tan perdido...", "Cada nivel revela más de mí."],
    ["Las piezas se sienten ligeras ahora.", "Como si aceptara lo que soy."],
    ["Estoy cerca del final.", "No temo lo que encontraré."],
    ["¡Dios...! Recuerdo todo ahora.", "Debo vivir con esto..."],
    ["Yo era el culpable...", "Este juego... esta memoria... es mi condena."]
]

# Escenas VN
vn_scenes = [
    {
        "bg": vn_bg,
        "dialogues": [
            ("POLICÍA", "¿Recuerdas algo de lo que ocurrió?"),
            ("TÚ", "No... por mas de que trate mi cabeza duele y mi corazon late, porfavor ayudame, me quema."),
            ("POLICÍA", "desde que despertaste solo dices incoherencias, necesitaras mucho mas para defenderte frente al juez, Necesitamos respuestas."),
            ("TÚ", "Estoy tratando, lo juro..."),
            ("TÚ", "¿si no recuerdo nada, como podre defenderme?", {
                "options": [
                    {"text": "Intentar recordar.", "next": 5},
                    {"text": "Pedir ayuda al policía.", "next": 6}
                ]
            }),
            ("TÚ", "Haré mi mejor esfuerzo por recordar..."),  # index 5
            ("TÚ", "¿Puede ayudarme a recordar algo?")         # index 6
        ]
    }
]

max_levels = 10

clock = pygame.time.Clock()

# Función para dibujar texto simple
def draw_text(surface, text, font, color, x, y):
    textobj = font.render(text, True, color)
    surface.blit(textobj, (x, y))

# Clase pieza
class Pieces:
    def __init__(self, index, image):
        self.index = index
        self.image = pygame.transform.smoothscale(image, (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect()
        self.placed = False  # Si está colocada en tablero
        self.board_pos = None  # (col, row) si está en tablero
        self.side = None 
        self.slot = None

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        # Opcional: borde para piezas fuera de tablero
        if not self.placed:
            pygame.draw.rect(surface, BOX_COLOR, self.rect, 3)

# Función para crear piezas de un puzzle
def create_pieces(num_pieces):
    pieces = []
    for i in range(num_pieces):
        img_path = os.path.join("PUZLE 1", f"pieza {i+1}.png")
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.smoothscale(img, (CELL_SIZE, CELL_SIZE))
        pieces.append(Pieces(i, img))
    return pieces

# Función para posicionar piezas fuera del tablero en los 4 costados
def assign_pieces_sides_and_slots(pieces):
    total = len(pieces)
    sides = [0, 1, 2, 3]
    slots_per_side = [0] * 4

    # Distribuir piezas en los 4 lados del tablero
    per_side = total // 4
    remainder = total % 4
    counts = [per_side] * 4
    for i in range(remainder):
        counts[i] += 1

    # Crear una lista de posiciones para cada lado
    side_slots_pairs = []
    for side, count in enumerate(counts):
        for slot in range(count):
            side_slots_pairs.append((side, slot))
    random.shuffle(side_slots_pairs)  # Mezclar posiciones

    for piece, (side, slot) in zip(pieces, side_slots_pairs):
        piece.side = side
        piece.slot = slot

# Función para dibujar el tablero con borde y celdas vacías
def draw_board():
    # Fondo tablero
    board_rect = pygame.Rect(BOARD_X_OFFSET, BOARD_Y_OFFSET, BOARD_WIDTH, BOARD_HEIGHT)
    pygame.draw.rect(screen, BG_COLOR, board_rect)
    pygame.draw.rect(screen, BOARD_BORDER_COLOR, board_rect, 4)

    # Dibujar líneas de la cuadrícula
    for c in range(1, COLS):
        x = BOARD_X_OFFSET + c * CELL_SIZE
        pygame.draw.line(screen, GRID_COLOR, (x, BOARD_Y_OFFSET), (x, BOARD_Y_OFFSET + BOARD_HEIGHT), 2)
    for r in range(1, ROWS):
        y = BOARD_Y_OFFSET + r * CELL_SIZE
        pygame.draw.line(screen, GRID_COLOR, (BOARD_X_OFFSET, y), (BOARD_X_OFFSET + BOARD_WIDTH, y), 2)

# Función para obtener la celda del tablero bajo un punto
def get_board_cell(pos):
    x, y = pos
    if BOARD_X_OFFSET <= x < BOARD_X_OFFSET + BOARD_WIDTH and BOARD_Y_OFFSET <= y < BOARD_Y_OFFSET + BOARD_HEIGHT:
        col = (x - BOARD_X_OFFSET) // CELL_SIZE
        row = (y - BOARD_Y_OFFSET) // CELL_SIZE
        return (col, row)
    return None

# Función para dibujar cuadro de diálogo abajo
def draw_dialog_box(text_lines):
    box_height = 110
    box_rect = pygame.Rect(0, SCREEN_HEIGHT - box_height - 10, SCREEN_WIDTH, box_height)
    s = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))  # semitransparente negro
    screen.blit(s, box_rect.topleft)

    y_offset = box_rect.top + 10
    for line in text_lines:
        draw_text(screen, line, small_font, TEXT_COLOR, 20, y_offset)
        y_offset += 25

# Función para dibujar cronómetro regresivo 10 minutos
def draw_timer(start_ticks):
    elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000
    remaining = max(0, TOTAL_TIME - elapsed_seconds)
    minutes = remaining // 60
    seconds = remaining % 60
    time_text = f"Tiempo: {minutes:02d}:{seconds:02d}"
    draw_text(screen, time_text, generic_font, TEXT_COLOR, SCREEN_WIDTH - 160, 10)

# Dibuja texto nivel actual arriba izquierda
def draw_level(level):
    level_text = f"Nivel: {level}"
    draw_text(screen, level_text, generic_font, TEXT_COLOR, 10, 10)

# Función para dibujar escena VN
def draw_vn_scene(scene, dialogue_index):
    screen.blit(scene["bg"], (0, 0))
    dialogue = scene["dialogues"][dialogue_index]
    name = dialogue[0]
    text = dialogue[1]

    # Dibuja personajes
    if name == "POLICÍA":
        # Policía a la derecha
        police_x = SCREEN_WIDTH - police_img.get_width() - 50
        police_y = SCREEN_HEIGHT - police_img.get_height() - 150
        screen.blit(police_img, (police_x, police_y))
    else:
        # Protagonista a la izquierda
        protagonist_x = 50
        protagonist_y = SCREEN_HEIGHT - protagonist_img.get_height() - 150
        screen.blit(protagonist_img, (protagonist_x, protagonist_y))

    # Caja diálogo (más abajo)
    box_height = 150
    box_rect = pygame.Rect(0, SCREEN_HEIGHT - box_height, SCREEN_WIDTH, box_height)
    s = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    screen.blit(s, box_rect.topleft)

    # Nombre (fuente genérica)
    name_text = f"{name}:"
    draw_text(screen, name_text, generic_font, TEXT_COLOR, 20, SCREEN_HEIGHT - box_height + 10)

    # Texto diálogo
    # Texto diálogo (envuelto)
    max_dialog_width = SCREEN_WIDTH - 40  # Leave some margin
    lines = wrap_text(text, generic_font, max_dialog_width)
    y = SCREEN_HEIGHT - box_height + 50
    for line in lines:
        draw_text(screen, line, generic_font, TEXT_COLOR, 20, y)
        y += generic_font.get_height() + 5

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    return lines

# Menú principal
def menu():
    pygame.mixer.music.load(os.path.join("MUSIC", "menumusic.wav"))
    pygame.mixer.music.play(-1)
    while True:
        screen.blit(menu_background_img, (0, 0))
        draw_text(screen, "Guilty Memories", big_menu_font, TEXT_COLOR, SCREEN_WIDTH//2 - 250, 100)

        mx, my = pygame.mouse.get_pos()

        button_jugar = pygame.Rect(SCREEN_WIDTH//2 - 100, 250, 200, 60)
        button_salir = pygame.Rect(SCREEN_WIDTH//2 - 100, 350, 200, 60)

        if button_jugar.collidepoint((mx, my)):
            color_jugar = BUTTON_HOVER_COLOR
        else:
            color_jugar = BUTTON_COLOR

        if button_salir.collidepoint((mx, my)):
            color_salir = BUTTON_HOVER_COLOR
        else:
            color_salir = BUTTON_COLOR

        pygame.draw.rect(screen, color_jugar, button_jugar)
        pygame.draw.rect(screen, color_salir, button_salir)

        draw_text(screen, "JUGAR", menu_font, TEXT_COLOR, button_jugar.x + 60, button_jugar.y + 10)
        draw_text(screen, "SALIR", menu_font, TEXT_COLOR, button_salir.x + 60, button_salir.y + 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_jugar.collidepoint(event.pos):
                    return  # Iniciar juego
                elif button_salir.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(60)

# Menú pausa
def pause_menu():
    while True:
        screen.blit(menu_background_img, (0, 0))
        # Title above the buttons
        draw_text(screen, "Guilty Memories", big_menu_font, TEXT_COLOR, SCREEN_WIDTH//2 - 250, 150)

        mx, my = pygame.mouse.get_pos()

        button_reiniciar = pygame.Rect(SCREEN_WIDTH//2 - 100, 250, 200, 60)
        button_salir = pygame.Rect(SCREEN_WIDTH//2 - 100, 350, 200, 60)

        if button_reiniciar.collidepoint((mx, my)):
            color_reiniciar = BUTTON_HOVER_COLOR
        else:
            color_reiniciar = BUTTON_COLOR

        if button_salir.collidepoint((mx, my)):
            color_salir = BUTTON_HOVER_COLOR
        else:
            color_salir = BUTTON_COLOR

        pygame.draw.rect(screen, color_reiniciar, button_reiniciar)
        pygame.draw.rect(screen, color_salir, button_salir)

        draw_text(screen, "REINICIAR NIVEL", menu_font, TEXT_COLOR, button_reiniciar.x + 10, button_reiniciar.y + 10)
        draw_text(screen, "SALIR", menu_font, TEXT_COLOR, button_salir.x + 70, button_salir.y + 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_reiniciar.collidepoint(event.pos):
                    return "restart"
                elif button_salir.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(60)

# Escena VN tras nivel 1 (por ejemplo)
def run_vn_scene():
    pygame.mixer.music.stop()
    pygame.mixer.music.load(os.path.join("MUSIC", "VisualN1.wav"))
    pygame.mixer.music.play(-1)
    current_scene_index = 0
    dialogue_index = 0
    selected_option = 0

    while True:
        scene = vn_scenes[current_scene_index]
        dialogue = scene["dialogues"][dialogue_index]
        options = None
        if isinstance(dialogue, tuple) and len(dialogue) > 2 and isinstance(dialogue[2], dict):
            options = dialogue[2]["options"]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif options:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        dialogue_index = options[selected_option]["next"]
                        selected_option = 0
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        dialogue_index += 1
                        if dialogue_index >= len(scene["dialogues"]):
                            current_scene_index += 1
                            dialogue_index = 0
                            if current_scene_index >= len(vn_scenes):
                                return

        screen.fill(BG_COLOR)
        draw_vn_scene(scene, dialogue_index)

        # Draw options if present
        if options:
            base_y = SCREEN_HEIGHT - 320
            option_height = 36
            option_padding = 10
            option_width = 500
            for i, opt in enumerate(options):
                y = base_y + i * (option_height + option_padding)
                rect_color = (80, 80, 80) if i == selected_option else (40, 40, 40)
                rect = pygame.Rect(50, y, option_width, option_height)
                pygame.draw.rect(screen, rect_color, rect, border_radius=8)
                if i == selected_option:
                    pygame.draw.rect(screen, (255, 255, 0), rect, 2, border_radius=8)
                text_color = (255, 255, 0) if i == selected_option else (200, 200, 200)
                draw_text(screen, opt["text"], generic_font, text_color, 60, y + 6)

        pygame.display.update()
        clock.tick(60)

# Juego principal (puzzle)
def game_loop():
    pygame.mixer.music.load(os.path.join("MUSIC", "music.wav"))
    pygame.mixer.music.play(-1)
    level = 1

    while level <= max_levels:
        restart_level = True
        while restart_level:
            # Crear piezas para el nivel
            num_pieces = ROWS * COLS
            pieces = create_pieces(num_pieces)
            assign_pieces_sides_and_slots(pieces)

            # Mezclar piezas y posicionar fuera del tablero
            for p in pieces:
                p.placed = False
                p.board_pos = None
            for piece in pieces:
                position_piece_on_side(piece)

            dragging_piece = None
            offset_x = 0
            offset_y = 0

            # Cronómetro inicio para nivel
            start_ticks = pygame.time.get_ticks()

            # Diálogo inicial nivel
            dialog_index = 0
            dialog_lines = [puzzle_dialogs[level-1][dialog_index]]

            running_level = True
            paused = False

            while running_level:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            paused = True

                    if paused:
                        continue  # Ignorar eventos de juego mientras está pausado

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            for p in reversed(pieces):  # Prioridad pieza encima
                                if p.rect.collidepoint(event.pos):
                                    dragging_piece = p
                                    mouse_x, mouse_y = event.pos
                                    offset_x = p.rect.x - mouse_x
                                    offset_y = p.rect.y - mouse_y
                                    break

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1 and dragging_piece:
                            cell = get_board_cell(event.pos)
                            if cell:
                                col, row = cell
                                # Validar no esté ocupado
                                occupied = any((other.board_pos == (col, row)) for other in pieces if other.placed)
                                if not occupied and can_place_piece(pieces, dragging_piece, col, row):
                                    dragging_piece.placed = True
                                    dragging_piece.board_pos = (col, row)
                                    # Ajustar posición al centro celda
                                    dragging_piece.rect.topleft = (BOARD_X_OFFSET + col*CELL_SIZE, BOARD_Y_OFFSET + row*CELL_SIZE)
                                else:
                                    # Regresa a su posición fuera del tablero
                                    dragging_piece.placed = False
                                    dragging_piece.board_pos = None
                                    position_piece_on_side(dragging_piece)
                            else:
                                # Regresa a su posición fuera del tablero
                                dragging_piece.placed = False
                                dragging_piece.board_pos = None
                                position_piece_on_side(dragging_piece)
                            dragging_piece = None

                    elif event.type == pygame.MOUSEMOTION:
                        if dragging_piece:
                            mouse_x, mouse_y = event.pos
                            dragging_piece.rect.x = mouse_x + offset_x
                            dragging_piece.rect.y = mouse_y + offset_y

                # Pausa menú
                while paused:
                    action = pause_menu()
                    if action == "restart":
                        paused = False
                        restart_level = True
                        running_level = False
                        break

                if not running_level:
                    break

                # Dibujar todo
                screen.blit(background_img, (0, 0))
                draw_board()

                for p in pieces:
                    p.draw(screen)

                draw_dialog_box(dialog_lines)

                draw_timer(start_ticks)
                draw_level(level)

                # Actualizar diálogo cada cierto tiempo (cada 6 segundos)
                elapsed = (pygame.time.get_ticks() - start_ticks) // 1000
                idx = elapsed // 6
                if idx < len(puzzle_dialogs[level-1]):
                    dialog_lines = [puzzle_dialogs[level-1][idx]]
                else:
                    dialog_lines = []

                # Verificar si todas piezas están colocadas (nivel completado)
                if all(p.placed and p.board_pos is not None for p in pieces):
                    # Pequeña pausa antes de avanzar
                    pygame.display.update()
                    pygame.time.delay(1000)
                    restart_level = False  # <-- Ensure we don't restart after completion
                    break

                # Verificar tiempo restante
                if (pygame.time.get_ticks() - start_ticks) // 1000 >= TOTAL_TIME:
                    # Mostrar pantalla Game Over y volver menú
                    game_over_screen()
                    return

                pygame.display.update()
                clock.tick(60)

            # If we exited the level loop because of restart, restart the level
            if restart_level:
                continue

            # Tras completar nivel 1, mostrar escena VN
            if level == 1:
                run_vn_scene()
                pygame.mixer.music.load(os.path.join("MUSIC", "music.wav"))
                pygame.mixer.music.play(-1)

            level += 1

    # Fin juego (puedes agregar pantalla de finalización)
    end_game_screen()

def game_over_screen():
    while True:
        screen.fill(BLOOD_RED)
        draw_text(screen, "GAME OVER", big_menu_font, TEXT_COLOR, SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50)
        draw_text(screen, "Presiona ESC para salir o R para reiniciar", small_font, TEXT_COLOR, SCREEN_WIDTH//2 - 170, SCREEN_HEIGHT//2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    return

        pygame.display.update()
        clock.tick(60)

def end_game_screen():
    while True:
        screen.fill(BG_COLOR)
        draw_text(screen, "¡Felicidades, has terminado Guilty Memories!", small_font, TEXT_COLOR, SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 10)
        draw_text(screen, "Presiona ESC para salir", small_font, TEXT_COLOR, SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(60)

def can_place_piece(pieces, piece, col, row):
    return True  # Allow any piece to be placed anywhere

# Programa principal
def main():
    while True:
        menu()
        game_loop()

if __name__ == "__main__":
    main()
import pygame
import math
import random
import copy
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 500, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
icon = pygame.image.load("assets/images/icon.png")
pygame.display.set_icon(icon)
pygame.mixer.music.load("assets/sound/background.mp3")
pygame.mixer.music.play(-1)
CLEAR_ROWS_SOUND = pygame.mixer.Sound("assets/sound/clear_rows.mp3")
CLEAR_ROWS_SOUND.set_volume(0.5)
HARD_DROP_SOUND = pygame.mixer.Sound("assets/sound/hard_drop.mp3")

NUM_OF_TILES_IN_ROW = 10
NUM_OF_TILES_IN_COLUMN = 20
TILE_WIDTH = 28
FRAME_WIDTH = NUM_OF_TILES_IN_ROW * TILE_WIDTH
FRAME_HEIGHT = NUM_OF_TILES_IN_COLUMN * TILE_WIDTH
FRAME_OFFSET_X = round(WIDTH / 20)
FRAME_OFFSET_Y = round((HEIGHT-FRAME_HEIGHT)/2)
BLOCK_TYPES = ["O", "L", "J", "I", "T", "Z", "S"]
START_X = math.floor(NUM_OF_TILES_IN_ROW / 2) - 1
FPS = 60
INITIAL_AUTO_DROP_SPEED = 1  # seconds
SOFT_DROP_SPEED = 0.05  # seconds
AUTO_SHIFT_SPEED = 0.05  # seconds
AUTO_SHIFT_DELAY = 0.2  # seconds
LOCK_DELAY = 0.8  # seconds
ENABLE_GHOST_PIECE = True

TETRIS_FONT = pygame.font.SysFont("aerial", 150)
COUNTDOWN_FONT = pygame.font.SysFont("aerial", 150)
GAME_OVER_FONT = pygame.font.SysFont("aerial", 80)
GAME_OVER_SCORE_FONT = pygame.font.SysFont("aerial", 50)
MENU_OPTIONS_FONT = pygame.font.SysFont("aerial", 50)
MENU_OPTIONS_SCORE_FONT = pygame.font.SysFont("aerial", 50)
SCORE_FONT = pygame.font.SysFont("aerial", 40)
NEXT_FONT = pygame.font.SysFont("aerial", 30)
NEXT_TEXT = NEXT_FONT.render("Next", 1, "black")
SCORE_TITLE_TEXT = NEXT_FONT.render("Score", 1, "black")

PREVIEW_FRAME_WIDTH = TILE_WIDTH * 5
PREVIEW_FRAME_X = round(FRAME_OFFSET_X + FRAME_WIDTH + WIDTH / 20)
PREVIEW_FRAME_Y = FRAME_OFFSET_Y + NEXT_TEXT.get_height() + 5
SCORE_FRAME_HEIGHT = 50
SCORE_FRAME_Y = PREVIEW_FRAME_Y + PREVIEW_FRAME_WIDTH + 50 + SCORE_TITLE_TEXT.get_height() + 5

class Block:
    def __init__(self, type, preview=False):
        self.type = type
        self.orientation = 0
        if preview:
            self.bounding_box_x = 0
            self.bounding_box_y = 0
        else:
            self.bounding_box_x = START_X - 1
            self.bounding_box_y = -1
        if type == "O":
            self.colour = (255, 255, 0)
            self.coord = [[self.bounding_box_x + 1, self.bounding_box_y + 1], [self.bounding_box_x + 2, self.bounding_box_y + 1],
                          [self.bounding_box_x + 1, self.bounding_box_y + 2], [self.bounding_box_x + 2, self.bounding_box_y + 2]]
        elif type == "L":
            self.colour = (255, 129, 0)
            self.coord = [[self.bounding_box_x, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                          [self.bounding_box_x + 2, self.bounding_box_y + 1], [self.bounding_box_x, self.bounding_box_y + 2]]
        elif type == "J":
            self.colour = (0, 0, 255)
            self.coord = [[self.bounding_box_x, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                          [self.bounding_box_x + 2, self.bounding_box_y + 1], [self.bounding_box_x + 2, self.bounding_box_y + 2]]
        elif type == "I":
            self.colour = (0, 255, 255)
            self.coord = [[self.bounding_box_x, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                          [self.bounding_box_x + 2, self.bounding_box_y + 1], [self.bounding_box_x + 3, self.bounding_box_y + 1]]
        elif type == "T":
            self.colour = (255, 0, 255)
            self.coord = [[self.bounding_box_x, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                          [self.bounding_box_x + 2, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 2]]
        elif type == "Z":
            self.colour = (255, 0, 0)
            self.coord = [[self.bounding_box_x, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                          [self.bounding_box_x + 1, self.bounding_box_y + 2], [self.bounding_box_x + 2, self.bounding_box_y + 2]]
        elif type == "S":
            self.colour = (0, 255, 0)
            self.coord = [[self.bounding_box_x + 1, self.bounding_box_y + 1], [self.bounding_box_x + 2, self.bounding_box_y + 1],
                          [self.bounding_box_x, self.bounding_box_y + 2], [self.bounding_box_x + 1, self.bounding_box_y + 2]]
    
    def drop(self):
        self.bounding_box_y += 1
        for coord in self.coord:
            coord[1] += 1
        
    def move_up(self):
        self.bounding_box_y -= 1
        for coord in self.coord:
            coord[1] -= 1
    
    def move_left(self):
        self.bounding_box_x -= 1
        for coord in self.coord:
            coord[0] -= 1
    
    def move_right(self):
        self.bounding_box_x += 1
        for coord in self.coord:
            coord[0] += 1

    def rotate(self, direction="clockwise"):
        if self.type != "O":
            if self.type in ["L", "J", "T"]:
                total_orientations = 4
            else:
                total_orientations = 2
            if direction == "clockwise":
                self.orientation = (self.orientation + 1) % total_orientations
            elif direction == "counterclockwise":
                self.orientation = (self.orientation - 1) % total_orientations

            if self.type == "L":
                if self.orientation == 0:
                    self.coord = [[self.bounding_box_x, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                                  [self.bounding_box_x + 2, self.bounding_box_y + 1], [self.bounding_box_x, self.bounding_box_y + 2]]
                elif self.orientation == 1:
                    self.coord = [[self.bounding_box_x, self.bounding_box_y], [self.bounding_box_x + 1, self.bounding_box_y],
                                  [self.bounding_box_x + 1, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 2]]
                elif self.orientation == 2:
                    self.coord = [[self.bounding_box_x + 2, self.bounding_box_y + 1], [self.bounding_box_x, self.bounding_box_y + 2],
                                  [self.bounding_box_x + 1, self.bounding_box_y + 2], [self.bounding_box_x + 2, self.bounding_box_y + 2]]
                elif self.orientation == 3:
                    self.coord = [[self.bounding_box_x + 1, self.bounding_box_y], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                                  [self.bounding_box_x + 1, self.bounding_box_y + 2], [self.bounding_box_x + 2, self.bounding_box_y + 2]]

            elif self.type == "J":
                if self.orientation == 0:
                    self.coord = [[self.bounding_box_x, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                                    [self.bounding_box_x + 2, self.bounding_box_y + 1], [self.bounding_box_x + 2, self.bounding_box_y + 2]]
                elif self.orientation == 1:
                    self.coord = [[self.bounding_box_x + 1, self.bounding_box_y], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                                  [self.bounding_box_x + 1, self.bounding_box_y + 2], [self.bounding_box_x, self.bounding_box_y + 2]]
                elif self.orientation == 2:
                    self.coord = [[self.bounding_box_x, self.bounding_box_y + 1], [self.bounding_box_x, self.bounding_box_y + 2],
                                  [self.bounding_box_x + 1, self.bounding_box_y + 2], [self.bounding_box_x + 2, self.bounding_box_y + 2]]
                elif self.orientation == 3:
                    self.coord = [[self.bounding_box_x + 1, self.bounding_box_y], [self.bounding_box_x + 2, self.bounding_box_y],
                                  [self.bounding_box_x + 1, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 2]]

            elif self.type == "T":
                if self.orientation == 0:
                    self.coord = [[self.bounding_box_x, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                                  [self.bounding_box_x + 2, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 2]]
                elif self.orientation == 1:
                    self.coord = [[self.bounding_box_x + 1, self.bounding_box_y], [self.bounding_box_x, self.bounding_box_y + 1],
                                  [self.bounding_box_x + 1, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 2]]
                elif self.orientation == 2:
                    self.coord = [[self.bounding_box_x + 1, self.bounding_box_y + 1], [self.bounding_box_x, self.bounding_box_y + 2],
                                  [self.bounding_box_x + 1, self.bounding_box_y + 2], [self.bounding_box_x + 2, self.bounding_box_y + 2]]
                elif self.orientation == 3:
                    self.coord = [[self.bounding_box_x + 1, self.bounding_box_y], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                                  [self.bounding_box_x + 2, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 2]]
                
            elif self.type == "I":
                if self.orientation == 0:
                    self.coord = [[self.bounding_box_x, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                                  [self.bounding_box_x + 2, self.bounding_box_y + 1], [self.bounding_box_x + 3, self.bounding_box_y + 1]]
                elif self.orientation == 1:
                    self.coord = [[self.bounding_box_x + 2, self.bounding_box_y], [self.bounding_box_x + 2, self.bounding_box_y + 1],
                                  [self.bounding_box_x + 2, self.bounding_box_y + 2], [self.bounding_box_x + 2, self.bounding_box_y + 3]]
                
            elif self.type == "Z":
                if self.orientation == 0:
                    self.coord = [[self.bounding_box_x, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                                  [self.bounding_box_x + 1, self.bounding_box_y + 2], [self.bounding_box_x + 2, self.bounding_box_y + 2]]
                elif self.orientation == 1:
                    self.coord = [[self.bounding_box_x + 2, self.bounding_box_y], [self.bounding_box_x + 1, self.bounding_box_y + 1],
                                  [self.bounding_box_x + 2, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 2]]

            elif self.type == "S":
                if self.orientation == 0:
                    self.coord = [[self.bounding_box_x + 1, self.bounding_box_y + 1], [self.bounding_box_x + 2, self.bounding_box_y + 1],
                                  [self.bounding_box_x, self.bounding_box_y + 2], [self.bounding_box_x + 1, self.bounding_box_y + 2]]
                elif self.orientation == 1:
                    self.coord = [[self.bounding_box_x, self.bounding_box_y], [self.bounding_box_x, self.bounding_box_y + 1],
                                  [self.bounding_box_x + 1, self.bounding_box_y + 1], [self.bounding_box_x + 1, self.bounding_box_y + 2]]

        
class Play_Area:
    def __init__(self):
        self.tiles = [[] for _ in range(NUM_OF_TILES_IN_COLUMN)]
        self.block = None
        self.bag = []
        self.preview_block = None
        self.ghost_piece = Block("O")
        self.score = 0
        self.lines_cleared = 0
        self.level = 0
        self.auto_drop_speed = INITIAL_AUTO_DROP_SPEED
        self.lock_delay_timer = 0
        self.rows_to_remove = []
        self.clear_completed_rows_timer = 0
        self.game_over = False
        self.game_over_surface = None

        # create play area surface
        WIN.fill((128, 128, 128))
        frame = pygame.Rect(FRAME_OFFSET_X, FRAME_OFFSET_Y, FRAME_WIDTH, FRAME_HEIGHT)
        pygame.draw.rect(WIN, "black", frame)
        WIN.blit(NEXT_TEXT, (PREVIEW_FRAME_X + PREVIEW_FRAME_WIDTH/2 - NEXT_TEXT.get_width()/2, FRAME_OFFSET_Y))
        preview_frame = pygame.Rect(PREVIEW_FRAME_X, PREVIEW_FRAME_Y, PREVIEW_FRAME_WIDTH, PREVIEW_FRAME_WIDTH)
        pygame.draw.rect(WIN, "black", preview_frame)
        WIN.blit(SCORE_TITLE_TEXT, (PREVIEW_FRAME_X + PREVIEW_FRAME_WIDTH/2 - SCORE_TITLE_TEXT.get_width()/2, PREVIEW_FRAME_Y + PREVIEW_FRAME_WIDTH + 50))
        score_frame = pygame.Rect(PREVIEW_FRAME_X, SCORE_FRAME_Y, PREVIEW_FRAME_WIDTH, SCORE_FRAME_HEIGHT)
        pygame.draw.rect(WIN, "black", score_frame)
        self.surface = WIN.copy()

    def generate_block(self):
        if not self.bag:
            self.bag = random.sample(BLOCK_TYPES, len(BLOCK_TYPES))
        type = self.bag.pop()
        self.block = Block(type)
        if not self.bag:
            self.bag = random.sample(BLOCK_TYPES, len(BLOCK_TYPES))
        type = self.bag[-1]
        self.preview_block = Block(type, preview=True)
        self.game_over = self.check_collision()
        while self.game_over and self.check_collision_with_tiles():
            self.block.move_up()
    
    def check_collision(self, ghost=False):
        collide = False
        if not ghost:
            coord = self.block.coord
        else:
            coord = self.ghost_piece.coord
        for block_tile in coord:
            if block_tile[0] < 0 or block_tile[0] >= NUM_OF_TILES_IN_ROW or block_tile[1] < 0 or block_tile[1] >= NUM_OF_TILES_IN_COLUMN:
                collide = True
                break
            else:
                for tile in self.tiles[block_tile[1]]:
                    if block_tile[0] == tile[0]:
                        collide = True
                        break
        return collide
    
    def check_block_on_ground(self):
        self.block.drop()
        is_on_ground = self.check_collision()
        self.block.move_up()
        return is_on_ground

    def check_collision_with_tiles(self):
        collide = False
        for block_tile in self.block.coord:
            if block_tile[1] >= 0:
                for tile in self.tiles[block_tile[1]]:
                    if block_tile[0] == tile[0]:
                        collide = True
                        break
        return collide
    
    def move_left(self):
        self.block.move_left()
        if self.check_collision():
            self.block.move_right()
        
    def move_right(self):
        self.block.move_right()
        if self.check_collision():
            self.block.move_left()
    
    def rotate(self):
        self.block.rotate("clockwise")
        if self.check_collision():
            self.block.rotate("counterclockwise")
    
    def auto_drop(self):
        self.block.drop()
        if self.check_collision():
            self.block.move_up()
        else:
            self.lock_delay_timer = 0

    def soft_drop(self):
        self.block.drop()
        if self.check_collision():
            self.block.move_up()
        else:
            self.score += 1
            self.lock_delay_timer = 0

    def hard_drop(self):
        while not self.check_collision():
            self.block.drop()
            self.score += 2
        self.block.move_up()
        self.score -= 2
        HARD_DROP_SOUND.play()
        return self.lock()

    def lock(self):
        colour = self.block.colour
        for tile in self.block.coord:
            self.tiles[tile[1]].append((tile[0], colour))
        self.block.coord = []
        self.check_completed_rows()
        if self.rows_to_remove:
            rows_completed = True
        else:
            rows_completed = False
            self.generate_block()
        self.lock_delay_timer = 0
        return rows_completed

    def check_completed_rows(self):
        self.rows_to_remove = []
        for id, row in enumerate(self.tiles):
            if len(row) == NUM_OF_TILES_IN_ROW:
                self.rows_to_remove.append(id)

    def update_ghost_piece(self):
        self.ghost_piece.coord = []
        if ENABLE_GHOST_PIECE and self.block.coord:
            self.ghost_piece.coord = copy.deepcopy(self.block.coord)
            while not self.check_collision(ghost=True):
                self.ghost_piece.drop()
            self.ghost_piece.move_up()
    
    def draw(self):
        WIN.blit(self.surface, (0, 0))

        for row_id, row in enumerate(self.tiles):
            for column_id, colour in row:
                tile = pygame.Rect(column_id * TILE_WIDTH + FRAME_OFFSET_X, row_id * TILE_WIDTH + FRAME_OFFSET_Y, TILE_WIDTH, TILE_WIDTH)
                pygame.draw.rect(WIN, colour, tile)
                pygame.draw.rect(WIN, "black", tile, width=round(TILE_WIDTH/20))
        
        colour = self.block.colour
        for column_id, row_id in self.block.coord:
            tile = pygame.Rect(column_id * TILE_WIDTH + FRAME_OFFSET_X, row_id * TILE_WIDTH + FRAME_OFFSET_Y, TILE_WIDTH, TILE_WIDTH)
            pygame.draw.rect(WIN, colour, tile)
            pygame.draw.rect(WIN, "black", tile, width=round(TILE_WIDTH/20))

        for column_id, row_id in self.ghost_piece.coord:
            tile = pygame.Rect(column_id*TILE_WIDTH + FRAME_OFFSET_X + TILE_WIDTH/20, row_id*TILE_WIDTH + FRAME_OFFSET_Y + TILE_WIDTH/20, 0.9*TILE_WIDTH, 0.9*TILE_WIDTH)
            pygame.draw.rect(WIN, colour, tile, width=round(TILE_WIDTH/20))

        colour = self.preview_block.colour
        for column_id, row_id in self.preview_block.coord:
            if self.preview_block.type == "I":
                tile = pygame.Rect(column_id*TILE_WIDTH + PREVIEW_FRAME_X + 14, row_id*TILE_WIDTH + PREVIEW_FRAME_Y + 30, TILE_WIDTH, TILE_WIDTH)
            elif self.preview_block.type == "O":
                tile = pygame.Rect(column_id*TILE_WIDTH + PREVIEW_FRAME_X + 15, row_id*TILE_WIDTH + PREVIEW_FRAME_Y + 15, TILE_WIDTH, TILE_WIDTH)
            else:
                tile = pygame.Rect(column_id*TILE_WIDTH + PREVIEW_FRAME_X + 28, row_id*TILE_WIDTH + PREVIEW_FRAME_Y + 15, TILE_WIDTH, TILE_WIDTH)
            pygame.draw.rect(WIN, colour, tile)
            pygame.draw.rect(WIN, "black", tile, width=round(TILE_WIDTH/20))

        score = SCORE_FONT.render(str(self.score), 1, "white")
        WIN.blit(score, (PREVIEW_FRAME_X + PREVIEW_FRAME_WIDTH/2 - score.get_width()/2, SCORE_FRAME_Y + 12))


class Start_Menu():
    def __init__(self):
        button_width, button_height = 300, 80
        self.start_game_button = {
            "rect": pygame.Rect(WIDTH/2 - button_width/2, 250, button_width, button_height),
            "is_pressed": False
        }
        self.show_controls_button = {
            "rect": pygame.Rect(WIDTH/2 - button_width/2, 380, button_width, button_height),
            "is_pressed": False
        }
        self.show_controls = False
        self.accept_click = False

        WIN.fill((128, 128, 128))
        title = "TETRIS"
        title_colours = [(255, 0, 0), (255, 129, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255)]
        title_coord = [(50, 80), (115, 80), (187, 80), (255, 80), (340, 80), (380, 80)]
        for letter, colour, coord in zip(title, title_colours, title_coord):
            text = TETRIS_FONT.render(letter, 1, colour)
            WIN.blit(text, coord)
        pygame.draw.rect(WIN, (80, 80, 80), self.start_game_button["rect"])
        text = MENU_OPTIONS_FONT.render("Start Game", 1, "white")
        WIN.blit(text, (WIDTH/2 - text.get_width()/2, 274))
        pygame.draw.rect(WIN, (80, 80, 80), self.show_controls_button["rect"])
        text = MENU_OPTIONS_FONT.render("Show Controls", 1, "white")
        WIN.blit(text, (WIDTH/2 - text.get_width()/2, 404))
        self.surface = WIN.copy()

        image = pygame.image.load("assets/images/controls.png")
        original_width, original_height = image.get_size()
        scale_factor = 0.7
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        self.controls_img = pygame.transform.smoothscale(image, (new_width, new_height))

        image = pygame.image.load("assets/images/close.png")
        original_width, original_height = image.get_size()
        scale_factor = 0.1
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        image = pygame.transform.smoothscale(image, (new_width, new_height))
        self.close_button = {
            "img": image.convert_alpha(),
            "pos": (420, 110),
            "is_pressed": False
        }

    def run(self, mouse_input):
        start_game = False
        if not self.show_controls:
            WIN.blit(self.surface, (0, 0))
            if not mouse_input["is_pressed"] and not self.accept_click:
                self.accept_click = True
        
            if self.accept_click and mouse_input["is_pressed"]:
                if self.start_game_button["rect"].collidepoint(mouse_input["pressed_pos"]):
                    self.start_game_button["is_pressed"] = True
                elif self.show_controls_button["rect"].collidepoint(mouse_input["pressed_pos"]):
                    self.show_controls_button["is_pressed"] = True
                
            elif self.accept_click and not mouse_input["is_pressed"]:
                if self.start_game_button["is_pressed"] and self.start_game_button["rect"].collidepoint(mouse_input["released_pos"]):
                    start_game = True
                    return start_game
                elif self.show_controls_button["is_pressed"] and self.show_controls_button["rect"].collidepoint(mouse_input["released_pos"]):
                    self.show_controls = True
                else:
                    self.start_game_button["is_pressed"] = False
                    self.show_controls_button["is_pressed"] = False
        
        if self.show_controls:
            WIN.blit(self.surface, (0, 0))
            dim_surface = pygame.Surface((WIDTH, HEIGHT))
            dim_surface.set_alpha(210)
            dim_surface.fill((0, 0, 0))
            WIN.blit(dim_surface, (0, 0))
            WIN.blit(self.controls_img, (WIDTH/2 - self.controls_img.get_width()/2, HEIGHT/2 - self.controls_img.get_height()/2))
            WIN.blit(self.close_button["img"], self.close_button["pos"])

            button_rect = self.close_button["img"].get_rect(topleft=self.close_button["pos"])
            if mouse_input["is_pressed"] and button_rect.collidepoint(mouse_input["pressed_pos"]):
                relative_x = mouse_input["pressed_pos"][0] - self.close_button["pos"][0]
                relative_y = mouse_input["pressed_pos"][1] - self.close_button["pos"][1]
                if self.close_button["img"].get_at((relative_x, relative_y)).a != 0:
                    self.close_button["is_pressed"] = True
            elif self.close_button["is_pressed"] and button_rect.collidepoint(mouse_input["released_pos"]):
                relative_x = mouse_input["released_pos"][0] - self.close_button["pos"][0]
                relative_y = mouse_input["released_pos"][1] - self.close_button["pos"][1]
                if self.close_button["img"].get_at((relative_x, relative_y)).a != 0:
                    self.show_controls = False
                    self.accept_click = False
                self.close_button["is_pressed"] = False
            else:
                self.close_button["is_pressed"] = False

        return start_game


class Start_Game_Animation():
    def __init__(self, play_area):
        self.play_area = play_area
        self.frame_count = 0
        self.done = False

    def play(self):
        self.done = False
        elapsed_time = math.floor(self.frame_count/FPS)
        if elapsed_time < 3:
            WIN.blit(self.play_area.surface, (0, 0))
            dim_surface = pygame.Surface((WIDTH, HEIGHT))
            dim_surface.set_alpha(210)
            dim_surface.fill((0, 0, 0))
            WIN.blit(dim_surface, (0, 0))
            text = COUNTDOWN_FONT.render(str(3 - elapsed_time), 1, "white")
            WIN.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))
            self.frame_count += 1
        else:
            self.done = True
            self.frame_count = 0


class Clear_Completed_Rows_Animation():
    def __init__(self, play_area):
        self.play_area = play_area
        self.frame_count = 0
        self.surface = None
        self.time_1 = 0.2   # seconds
        self.time_2 = 0.3   # seconds
        self.done = False

    def play(self):
        self.done = False
        if self.frame_count/FPS < self.time_2:
            if self.frame_count == 0:
                WIN.blit(self.play_area.surface, (0, 0))

                for row_id, row in enumerate(self.play_area.tiles):
                    for column_id, colour in row:
                        tile = pygame.Rect(column_id * TILE_WIDTH + FRAME_OFFSET_X, row_id * TILE_WIDTH + FRAME_OFFSET_Y, TILE_WIDTH, TILE_WIDTH)
                        pygame.draw.rect(WIN, colour, tile)
                        pygame.draw.rect(WIN, "black", tile, width=round(TILE_WIDTH/20))

                colour = self.play_area.preview_block.colour
                for column_id, row_id in self.play_area.preview_block.coord:
                    if self.play_area.preview_block.type == "I":
                        tile = pygame.Rect(column_id*TILE_WIDTH + PREVIEW_FRAME_X + 14, row_id*TILE_WIDTH + PREVIEW_FRAME_Y + 30, TILE_WIDTH, TILE_WIDTH)
                    elif self.play_area.preview_block.type == "O":
                        tile = pygame.Rect(column_id*TILE_WIDTH + PREVIEW_FRAME_X + 15, row_id*TILE_WIDTH + PREVIEW_FRAME_Y + 15, TILE_WIDTH, TILE_WIDTH)
                    else:
                        tile = pygame.Rect(column_id*TILE_WIDTH + PREVIEW_FRAME_X + 28, row_id*TILE_WIDTH + PREVIEW_FRAME_Y + 15, TILE_WIDTH, TILE_WIDTH)
                    pygame.draw.rect(WIN, colour, tile)
                    pygame.draw.rect(WIN, "black", tile, width=round(TILE_WIDTH/20))

                score = SCORE_FONT.render(str(self.play_area.score), 1, "white")
                WIN.blit(score, (PREVIEW_FRAME_X + PREVIEW_FRAME_WIDTH/2 - score.get_width()/2, SCORE_FRAME_Y + 12))
                
                self.surface = WIN.copy()
                CLEAR_ROWS_SOUND.play()
            
            WIN.blit(self.surface, (0, 0))

            for row_id in self.play_area.rows_to_remove:
                eraser = pygame.Rect(FRAME_OFFSET_X, row_id * TILE_WIDTH + FRAME_OFFSET_Y, min(self.frame_count/FPS/self.time_1, 1) * FRAME_WIDTH, TILE_WIDTH)
                pygame.draw.rect(WIN, "black", eraser)
            self.frame_count += 1

        else:
            for id in sorted(self.play_area.rows_to_remove, reverse=True):
                del self.play_area.tiles[id]
            for _ in self.play_area.rows_to_remove:
                self.play_area.tiles.insert(0, [])
            
            self.play_area.lines_cleared += len(self.play_area.rows_to_remove)
            if len(self.play_area.rows_to_remove) == 1:
                self.play_area.score += 100
            elif len(self.play_area.rows_to_remove) == 2:
                self.play_area.score += 400
            elif len(self.play_area.rows_to_remove) == 3:
                self.play_area.score += 900
            else:
                self.play_area.score += 2000

            self.play_area.level = self.play_area.lines_cleared // 4
            self.play_area.auto_drop_speed = max(INITIAL_AUTO_DROP_SPEED - self.play_area.level * 0.05, 0.05)
            self.play_area.generate_block()
            self.done = True
            self.frame_count = 0
        
        
class Game_Over_Animation():
    def __init__(self, play_area):
        self.play_area = play_area
        self.frame_count = 0
        self.timer = 0
        self.done = False

    def play(self):
        self.done = False
        if self.frame_count == 0:
            WIN.blit(self.play_area.surface, (0, 0))

            for row_id, row in enumerate(self.play_area.tiles):
                for column_id, colour in row:
                    tile = pygame.Rect(column_id * TILE_WIDTH + FRAME_OFFSET_X, row_id * TILE_WIDTH + FRAME_OFFSET_Y, TILE_WIDTH, TILE_WIDTH)
                    pygame.draw.rect(WIN, colour, tile)
                    pygame.draw.rect(WIN, "black", tile, width=round(TILE_WIDTH/20))
            
            colour = self.play_area.block.colour
            for column_id, row_id in self.play_area.block.coord:
                if row_id >= 0:
                    tile = pygame.Rect(column_id * TILE_WIDTH + FRAME_OFFSET_X, row_id * TILE_WIDTH + FRAME_OFFSET_Y, TILE_WIDTH, TILE_WIDTH)
                    pygame.draw.rect(WIN, colour, tile)
                    pygame.draw.rect(WIN, "black", tile, width=round(TILE_WIDTH/20))

            colour = self.play_area.preview_block.colour
            for column_id, row_id in self.play_area.preview_block.coord:
                if self.play_area.preview_block.type == "I":
                    tile = pygame.Rect(column_id*TILE_WIDTH + PREVIEW_FRAME_X + 14, row_id*TILE_WIDTH + PREVIEW_FRAME_Y + 30, TILE_WIDTH, TILE_WIDTH)
                elif self.play_area.preview_block.type == "O":
                    tile = pygame.Rect(column_id*TILE_WIDTH + PREVIEW_FRAME_X + 15, row_id*TILE_WIDTH + PREVIEW_FRAME_Y + 15, TILE_WIDTH, TILE_WIDTH)
                else:
                    tile = pygame.Rect(column_id*TILE_WIDTH + PREVIEW_FRAME_X + 28, row_id*TILE_WIDTH + PREVIEW_FRAME_Y + 15, TILE_WIDTH, TILE_WIDTH)
                pygame.draw.rect(WIN, colour, tile)
                pygame.draw.rect(WIN, "black", tile, width=round(TILE_WIDTH/20))

            score = SCORE_FONT.render(str(self.play_area.score), 1, "white")
            WIN.blit(score, (PREVIEW_FRAME_X + PREVIEW_FRAME_WIDTH/2 - score.get_width()/2, SCORE_FRAME_Y + 12))
            
            self.play_area.game_over_surface = WIN.copy()
        
        WIN.blit(self.play_area.game_over_surface, (0, 0))
        dim_surface = pygame.Surface((WIDTH, HEIGHT))
        dim_surface.set_alpha(min(round(self.frame_count * 10), 210))
        dim_surface.fill((0, 0, 0))
        WIN.blit(dim_surface, (0, 0))

        if self.frame_count / FPS >= 1:
            text = GAME_OVER_SCORE_FONT.render(f"Score: {self.play_area.score}", 1, "white")
            text.set_alpha(min(self.timer*5, 255))
            WIN.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2 + 20))
            self.timer += 1

        text = GAME_OVER_FONT.render("Game Over", 1, "white")
        WIN.blit(text, (WIDTH/2 - text.get_width()/2, min(HEIGHT/2 - text.get_height()/2 - 50 + self.frame_count*2 - 50, HEIGHT/2 - text.get_height()/2 - 50)))
        self.frame_count += 1

        if self.frame_count / FPS >= 3:
            self.done = True


class Play_Again_Menu():
    def __init__(self, play_area):
        self.play_area = play_area
        self.menu_width = WIDTH * 0.6
        self.menu_height = HEIGHT * 0.5
        self.accept_click = False
        self.play_again_button_pressed = False
        self.exit_game_button_pressed = False

    def run(self, mouse_input):
        WIN.blit(self.play_area.game_over_surface, (0, 0))
        dim_surface = pygame.Surface((WIDTH, HEIGHT))
        dim_surface.set_alpha(210)
        dim_surface.fill((0, 0, 0))
        WIN.blit(dim_surface, (0, 0))
        menu = pygame.Rect(WIDTH/2 - self.menu_width/2, HEIGHT/2 - self.menu_height/2, self.menu_width, self.menu_height)
        pygame.draw.rect(WIN, (128, 128, 128), menu)

        text = MENU_OPTIONS_SCORE_FONT.render(f"Score: {self.play_area.score}", 1, "white")
        WIN.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - self.menu_height/2 + 25))
        play_again_button = pygame.Rect(WIDTH/2 - self.menu_width*0.8/2, HEIGHT/2 - 30 - 30, self.menu_width * 0.8, 60)
        pygame.draw.rect(WIN, "green", play_again_button)
        text = MENU_OPTIONS_FONT.render("Play Again", 1, "white")
        WIN.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2 - 30))
        exit_game_button = pygame.Rect(WIDTH/2 - self.menu_width*0.8/2, HEIGHT/2 - 30 + 70, self.menu_width * 0.8, 60)
        pygame.draw.rect(WIN, "red", exit_game_button)
        text = MENU_OPTIONS_FONT.render("Exit Game", 1, "white")
        WIN.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2 + 70))

        if not mouse_input["is_pressed"] and not self.accept_click:
            self.accept_click = True
        
        if self.accept_click and mouse_input["is_pressed"]:
            if play_again_button.collidepoint(mouse_input["pressed_pos"]):
                self.play_again_button_pressed = True
            elif exit_game_button.collidepoint(mouse_input["pressed_pos"]):
                self.exit_game_button_pressed = True
            
        if self.accept_click and not mouse_input["is_pressed"]:
            if self.play_again_button_pressed and play_again_button.collidepoint(mouse_input["released_pos"]):
                return "play_again"
            elif self.exit_game_button_pressed and exit_game_button.collidepoint(mouse_input["released_pos"]):
                return "exit_game"
            else:
                self.play_again_button_pressed = False
                self.exit_game_button_pressed = False   
        return None


def main():
    play_area = Play_Area()
    start_menu = Start_Menu()
    start_game_animation = Start_Game_Animation(play_area)
    game_over_animation = Game_Over_Animation(play_area)
    clear_completed_rows_animation = Clear_Completed_Rows_Animation(play_area)
    play_again_menu = Play_Again_Menu(play_area)
    play_area.generate_block()

    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
    mouse_input = {
        "is_pressed": False,
        "pressed_pos" : None,
        "released_pos" : None
    }
    left_key_pressed = False
    right_key_pressed = False
    down_key_pressed = False
    left_key_pressed_time = 0
    right_key_pressed_time = 0
    auto_drop_timer = 0
    soft_drop_timer = 0
    auto_shift_left_timer = 0
    auto_shift_right_timer = 0
    animation = True    # block inputs during animation or menu
    in_start_menu = True
    start_game = False
    rows_completed = False
    in_play_again_menu = False
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(FPS)
        auto_drop_timer += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if not animation:
                        play_area.rotate()
                elif event.key == pygame.K_LEFT:
                    left_key_pressed = True
                    if not animation:
                        play_area.move_left()
                elif event.key == pygame.K_RIGHT:
                    right_key_pressed = True
                    if not animation:
                        play_area.move_right()
                elif event.key == pygame.K_DOWN:
                    down_key_pressed = True
                    if not animation:
                        play_area.soft_drop()
                elif event.key == pygame.K_SPACE:
                    if not animation:
                        rows_completed = play_area.hard_drop()
                        if rows_completed:
                            animation = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    left_key_pressed = False
                    left_key_pressed_time = 0
                    auto_shift_left_timer = 0
                elif event.key == pygame.K_RIGHT:
                    right_key_pressed = False
                    right_key_pressed_time = 0
                    auto_shift_right_timer = 0
                elif event.key == pygame.K_DOWN:
                    down_key_pressed = False
                    soft_drop_timer = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_input["is_pressed"] = True
                mouse_input["pressed_pos"] = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_input["is_pressed"] = False
                mouse_input["released_pos"] = event.pos
        
        if left_key_pressed:
            left_key_pressed_time += 1
        if right_key_pressed:
            right_key_pressed_time += 1
        
        if left_key_pressed_time == round(AUTO_SHIFT_DELAY * FPS):
            if not animation:
                play_area.move_left()
        elif left_key_pressed_time > round(AUTO_SHIFT_DELAY * FPS):
            if auto_shift_left_timer < round(AUTO_SHIFT_SPEED * FPS):
                auto_shift_left_timer += 1
            else:
                if not animation:
                    play_area.move_left()
                auto_shift_left_timer = 0

        if right_key_pressed_time == round(AUTO_SHIFT_DELAY * FPS):
            if not animation:
                play_area.move_right()
        elif right_key_pressed_time > round(AUTO_SHIFT_DELAY * FPS):
            if auto_shift_right_timer < round(AUTO_SHIFT_SPEED * FPS):
                auto_shift_right_timer += 1
            else:
                if not animation:
                    play_area.move_right()
                auto_shift_right_timer = 0

        if down_key_pressed:
            if soft_drop_timer < round(SOFT_DROP_SPEED * FPS):
                soft_drop_timer += 1
            else:
                if not animation:
                    play_area.soft_drop()
                soft_drop_timer = 0
        
        if auto_drop_timer == round(play_area.auto_drop_speed * FPS):
            play_area.auto_drop()
            auto_drop_timer = 0
            
        if not animation and play_area.check_block_on_ground():
            if play_area.lock_delay_timer < round(LOCK_DELAY * FPS):
                auto_drop_timer = 0
                play_area.lock_delay_timer += 1
            else:
                rows_completed = play_area.lock()

        if in_start_menu:
            start_game = start_menu.run(mouse_input)
            if start_game:
                in_start_menu = False

        if start_game:
            animation = True
            start_game_animation.play()
            if start_game_animation.done:
                start_game = False
                animation = False

        if rows_completed:
            animation = True
            clear_completed_rows_animation.play()
            if clear_completed_rows_animation.done:
                rows_completed = False
                animation = False

        if play_area.game_over:
            animation = True
            game_over_animation.play()
            if game_over_animation.done:
                play_area.game_over = False
                in_play_again_menu = True
        
        if in_play_again_menu:
            selection = play_again_menu.run(mouse_input)
            if selection == "play_again":
                in_play_again_menu = False
                start_game = True
                play_area = Play_Area()
                start_game_animation = Start_Game_Animation(play_area)
                game_over_animation = Game_Over_Animation(play_area)
                clear_completed_rows_animation = Clear_Completed_Rows_Animation(play_area)
                play_again_menu = Play_Again_Menu(play_area)
                play_area.generate_block()
            elif selection == "exit_game":
                break

        if not animation:
            play_area.update_ghost_piece()
            play_area.draw()
        else:
            auto_drop_timer = 0

        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    main()
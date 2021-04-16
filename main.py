import pygame as pg
import threading
import random
import os
import sys
from pygame import K_UP, K_DOWN, K_RIGHT, K_LEFT, KEYDOWN, K_w, K_s, K_d, K_a, K_ESCAPE
clock = pg.time.Clock()
pg.init()
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (198, 40, 40)
GREEN = (76, 175, 80)
BLUE = (65, 105, 225)
PINK = (225, 97, 170)
PURPLE = (135, 97, 225)
GRAY = (190, 190, 190, 100)
D_W_H = 600
T_C = 19
T_S = 600 // (T_C + 1)
ZM_W = T_S
ZM_H = T_S
sc = pg.display.set_mode((D_W_H, D_W_H))
main_menu = True
pause = False
game_for_one = False
game_for_two = False
game_over = False
screenshot = None
record = int(open("public/record.txt").readline().rstrip())
score = 0


def create_grid():
    surf = pg.Surface((D_W_H, D_W_H))
    grid = []
    surf.set_colorkey(BLACK)
    surf.fill(BLACK)
    for y in range(T_C + 1):
        line = []
        for x in range(T_C + 1):
            tile = pg.Rect(x * T_S, y * T_S, T_S, T_S)
            line.append(tile)
            pg.draw.rect(surf, GRAY, tile, 1)
        grid.append(line)

    return grid, surf


class SnakeBodyElement(pg.sprite.Sprite):
    def __init__(self, grid, snake):
        super().__init__()
        self.image = pg.Surface((T_S, T_S))
        self.rect = self.image.get_rect()
        last_index = -1
        if len(snake.body) == 0:
            self.rect.center = grid[snake.head_y][snake.head_x].center
            self.x = snake.head_x
            self.y = snake.head_y
        else:
            last_index = [i for i, e in enumerate(snake.body) if e.last][0]
            last_element = snake.body[last_index]
            last_element.last = False
            self.rect.center = grid[last_element.y][last_element.x].center
            self.x = last_element.x
            self.y = last_element.y
        self.image.fill(GREEN if snake.which == 1 else RED)
        self.last = True
        if last_index != -1 and len(snake.body) > 1:
            snake.body.insert(last_index + 1, self)
        else:
            snake.body.append(self)

    def draw(self):
        sc.blit(self.image, self.rect)

    def update_pos(self, grid, snake):
        self.rect.center = grid[snake.head_y][snake.head_x].center
        self.x = snake.head_x
        self.y = snake.head_y


class Snake(pg.sprite.Sprite):
    def __init__(self, grid, which=False):
        super().__init__()
        self.image = pg.image.load(
            os.path.join('public', 'snake_head_2.png' if which == 2 else 'snake_head.png'))

        self.image = pg.transform.scale(self.image, (T_S, T_S))
        self.rect = self.image.get_rect()
        if which != 1 and which != 2:
            self.rect.center = grid[T_C // 2][T_C // 2].center
            self.head_x = T_C // 2
            self.which = 1
        else:
            self.rect.center = grid[T_C // 4][T_C // 4].center if which == 1 else grid[T_C - (
                T_C // 4)][T_C - (T_C // 4)].center
            self.head_x = T_C // 4 if which == 1 else T_C - (T_C // 4)
            self.which = which
        self.head_y = T_C // 2
        self.TOP = True
        self.RIGHT = self.LEFT = self.BOTTOM = False
        self.body = []

    def lengthen(self, grid):
        SnakeBodyElement(grid, self)

    def key_press(self):
        global pause
        pressed = pg.key.get_pressed()
        strelka = self.which == 1
        if pressed[K_ESCAPE]:
            pause = True
            pause_draw()
        if pressed[K_UP if strelka else K_w] and not(self.BOTTOM) and not(self.TOP):
            self.image = pg.transform.rotate(
                self.image,  -90 if self.LEFT else 90)
            self.RIGHT = self.LEFT = False
            self.TOP = True
            return
        if pressed[K_DOWN if strelka else K_s] and not(self.TOP) and not(self.BOTTOM):
            self.image = pg.transform.rotate(
                self.image, 90 if self.LEFT else -90)
            self.RIGHT = self.LEFT = False
            self.BOTTOM = True
            return
        if pressed[K_RIGHT if strelka else K_d] and not(self.LEFT) and not(self.RIGHT):
            self.image = pg.transform.rotate(
                self.image, -90 if self.TOP else 90)
            self.TOP = self.BOTTOM = False
            self.RIGHT = True
            return
        if pressed[K_LEFT if strelka else K_a] and not(self.RIGHT) and not(self.LEFT):
            self.image = pg.transform.rotate(
                self.image, 90 if self.TOP else -90)
            self.TOP = self.BOTTOM = False
            self.LEFT = True

    def update(self, grid, snakes=None):
        # изменение позиции последнего элемента
        if len(self.body) != 0:
            l_i = 0
            for index, body_element in enumerate(self.body):
                if body_element.last:
                    body_element.update_pos(grid, self)
                    if len(self.body) != 1:
                        body_element.last = False
                        l_i = index - 1

            self.body[l_i].last = True
            [i.draw() for i in self.body]

        self.key_press()

        # изменение позиции головы
        if self.TOP:
            if self.head_y >= 0:
                self.head_y -= 1
                self.rect.center = grid[self.head_y][self.head_x].center
            else:
                self.rect.center = grid[T_C][self.head_x].center
                self.head_y = T_C
        elif self.BOTTOM:
            if self.head_y < T_C:
                self.head_y += 1
                self.rect.center = grid[self.head_y][self.head_x].center
            else:
                self.head_y = 0
                self.rect.center = grid[0][self.head_x].center
        elif self.RIGHT:
            if self.head_x < T_C:
                self.head_x += 1
                self.rect.center = grid[self.head_y][self.head_x].center
            else:
                self.head_x = 0
                self.rect.center = grid[self.head_y][0].center
        else:
            if self.head_x >= 0:
                self.head_x -= 1
                self.rect.center = grid[self.head_y][self.head_x].center
            else:
                self.head_x = T_C
                self.rect.center = grid[self.head_y][T_C].center
        self.crossing(snakes)

    def crossing(self, snakes=None):

        def crossing_mini(which, b_e):
            global game_over
            if b_e.x == self.head_x and b_e.y == self.head_y:
                game_over = True
                game_over_draw("Red" if which == 1 else "Green")

        if snakes:
            body_elements = snakes[0].body + snakes[1].body
            [crossing_mini(self.which, b_e) for b_e in body_elements]
        else:
            [crossing_mini(self.which, b_e) for b_e in self.body]

    def draw(self):
        sc.blit(self.image, self.rect)


def game_for_one_draw():
    global score
    global record
    global screenshot
    grid, grid_surf = create_grid()
    snake = Snake(grid)
    point = Point(grid)
    while game_for_one:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                save_record()
                pg.quit()
                sys.exit()

        # сохраняем экран
        screenshot = sc.copy()

        # очистка поля
        sc.fill(BLACK)

        # рисование сетки
        sc.blit(grid_surf, (0, 0))

        # проверка пересечение змейки с поинтом
        if not(pause):
            if snake.head_x == point.x and snake.head_y == point.y:
                snake.lengthen(grid)
                point.update(grid, snake.body)
                if score == record:
                    record += 1
                score += 1
            snake.update(grid)

        # рисуем все элементы
        snake.draw()
        point.draw()
        score_text = text_objects(str(score), 20, D_W_H - 40, GREEN)
        record_text = text_objects(str(record), 20, D_W_H - 100, RED)
        sc.blit(*score_text)
        sc.blit(*record_text)
        pg.display.flip()
        clock.tick(10)


def game_for_two_draw():
    global screenshot
    grid, grid_surf = create_grid()
    snake1 = Snake(grid, 1)
    snake2 = Snake(grid, 2)
    point = Point(grid)
    snakes = pg.sprite.Group(snake1, snake2)
    while game_for_two:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        # сохраняем экран
        screenshot = sc.copy()

        # очистка поля
        sc.fill(BLACK)

        # рисование сетки
        sc.blit(grid_surf, (0, 0))
        if not(pause):
            # проверка пересечение первой змейки с поинтом
            if snake1.head_x == point.x and snake1.head_y == point.y:
                snake1.lengthen(grid)
                point.update(grid, snakes.sprites()[
                             0].body + snakes.sprites()[1].body)
            # проверка пересечение второй змейки с поинтом
            if snake2.head_x == point.x and snake2.head_y == point.y:
                snake2.lengthen(grid)
                point.update(grid, snakes.sprites()[
                             0].body + snakes.sprites()[1].body)
            snakes.update(grid, snakes.sprites())
        snakes.draw(sc)
        point.draw()
        pg.display.flip()
        clock.tick(10)


class Point(pg.sprite.Sprite):
    def __init__(self, grid):
        super().__init__()
        self.image = pg.Surface((T_S, T_S))
        self.rect = self.image.get_rect()
        self.x = random.randint(0, T_C)
        self.y = random.randint(0, T_C)
        self.rect.center = grid[self.y][self.x].center
        self.image.fill(PURPLE)

    def update(self, grid, body=None):
        self.x = random.randint(0, T_C)
        self.y = random.randint(0, T_C)

        def crossing_mini(b_e):
            if b_e.x == self.x and b_e.y == self.y:
                self.update(grid, body)
                return
        [crossing_mini(b_e) for b_e in body]
        self.rect.center = grid[self.y][self.x].center

    def draw(self):
        sc.blit(self.image, self.rect)


def game_over_draw(winner):
    GAME_OVER = 300
    over_sc = pg.Surface((GAME_OVER, GAME_OVER - 50))
    save_record()
    sc.blit(screenshot, (0, 0))
    while game_over:
        for i in pg.event.get():
            if i.type == pg.QUIT:
                save_record()
                pg.quit()
                sys.exit()
        pg.draw.rect(over_sc, BLUE, (0, 0, GAME_OVER,
                                     GAME_OVER - 50), border_radius=6)
        game_over_text = text_objects("Game over!", 40)
        score_or_winner_text = text_objects(
            "Score:" + str(score) if game_for_one else winner + " player win!", 80)
        over_sc.blit(*game_over_text)
        over_sc.blit(*score_or_winner_text)
        button(over_sc, "Restart", 50, 120, 200,
               50, WHITE, RED, "restart_" + ("1" if game_for_one else "2"))
        button(over_sc, "Exit to menu", 50, 180, 200,
               50, WHITE, RED, "exit_to_menu")
        sc.blit(over_sc, ((D_W_H // 2 - GAME_OVER // 2,
                           D_W_H // 2 - (GAME_OVER - 50) // 2)))
        pg.display.flip()
        clock.tick(10)


def pause_draw():
    GAME_PAUSE = 300
    pause_sc = pg.Surface((GAME_PAUSE, GAME_PAUSE - 50))
    sc.blit(screenshot, (0, 0))
    while pause:
        for i in pg.event.get():
            if i.type == pg.QUIT:
                save_record()
                pg.quit()
                sys.exit()
        pg.draw.rect(pause_sc, BLUE, (0, 0, GAME_PAUSE,
                                      GAME_PAUSE - 50), border_radius=6)
        pause_text = text_objects("Pause", 40)
        pause_sc.blit(*pause_text)
        button(pause_sc, "Continue", 50, 120, 200,
               50, WHITE, RED, "continue")
        button(pause_sc, "Exit to menu", 50, 180, 200,
               50, WHITE, RED, "exit_to_menu")
        sc.blit(pause_sc, ((D_W_H // 2 - GAME_PAUSE // 2,
                            D_W_H // 2 - (GAME_PAUSE - 50) // 2)))
        pg.display.flip()
        clock.tick(10)


def text_objects(text, y, x=150, color=WHITE, size=30):
    font = pg.font.Font(os.path.join(
        'public', 'FreeSansBold.ttf'), size)
    textSurface = font.render(text, True, color)
    rect = textSurface.get_rect()
    rect.center = (x, y)

    return (textSurface, rect)


def save_record():
    if score >= record:
        f = open('public/record.txt', 'w')
        f.write(str(score))
        f.close()


def button(surf, text, x, y, w, h, c, ic, action=None):
    global main_menu
    mouse = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()
    pg.draw.rect(surf, c, (x, y, w, h), border_radius=6)
    button_text = text_objects(text, (y+(h/2)), (x+(w/2)), BLACK, 20)
    surf.blit(*button_text)
    s_w = 150
    s_h = 150 if main_menu else 175
    if x + w + s_w > mouse[0] > x + s_w and y + h + s_h > mouse[1] > y + s_h:
        pg.draw.rect(surf, ic, (x, y, w, h), border_radius=6)
        global game_for_one
        global game_for_two
        global game_over
        global score
        global pause
        if click[0] == 1 != None:
            if action == "play_one_draw":
                main_menu = False
                game_for_one = True
                game_for_one_draw()
            elif action == "play_two_draw":
                main_menu = False
                game_for_two = True
                game_for_two_draw()
            elif action == "exit_to_menu":
                game_over = False
                game_for_one = False
                game_for_two = False
                pause = False
                score = 0
                main_menu = True
                sc.fill(BLACK)
                main_menu_draw()
            elif action == "restart_1":
                score = 0
                game_over = False
                game_for_one = True
                game_for_one_draw()
            elif action == "restart_2":
                game_over = False
                game_for_two = True
                game_for_two_draw()
            elif action == "continue":
                pause = False
            elif action == "exit":
                pg.quit()
                sys.exit()
        button_text = text_objects(text, (y+(h/2)), (x+(w/2)), WHITE, 20)
        surf.blit(*button_text)


def main_menu_draw():
    MAIN_MENU = 300
    main_sc = pg.Surface((MAIN_MENU, MAIN_MENU))
    while main_menu:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        pg.draw.rect(main_sc, BLUE, (0, 0, MAIN_MENU,
                                     MAIN_MENU), border_radius=6)
        main_menu_text = text_objects("Main Menu", 40)
        main_sc.blit(*main_menu_text)
        button(main_sc, "Play alone", 50, 80, 200,
               50, WHITE, RED, "play_one_draw")
        button(main_sc, "Play together", 50, 150, 200,
               50, WHITE, RED, "play_two_draw")
        button(main_sc, "Exit", 50, 220, 200,
               50, WHITE, RED, "exit")
        sc.blit(main_sc, ((D_W_H // 2 - MAIN_MENU // 2, D_W_H // 2 - MAIN_MENU // 2)))
        pg.display.flip()
        clock.tick(10)


if __name__ == "__main__":
    main_menu_draw()

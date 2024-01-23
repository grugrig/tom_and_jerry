# необходимые импорты
import os
import sys

import pygame

# константы, которые используются в проекте
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 600, 600
FPS = 15
FPS_S = 50
TILE_SIZE = 40
ENEMY_EVENT_TYPE = 30

# инициализация pygame
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('Том и Джерри')
clock = pygame.time.Clock()


# функция, которая отвечает за закрытие программы
def terminate():
    pygame.quit()
    sys.exit()


# функция финального экрана
def finish_screen():
    all_sprites = pygame.sprite.Group()
    sprite = Picture(all_sprites)

    while True:
        screen.fill(pygame.Color('blue'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        sprite.update(1)
        all_sprites.draw(screen)
        pygame.display.flip()
        if sprite.rect.x >= 0:
            pygame.time.delay(3000)
            return


# функция стартового экрана
def start_screen():
    intro_text = ["ПРАВИЛА ИГРЫ:", "",
                  "Задача мышонка Джерри",
                  "добраться до норки и,",
                  "не быть съеденным котом",
                  "Томом. Управляйте",
                  "мышонком клавишами",
                  "со стрелками.",
                  "Для продолжения нажмите",
                  "любую кнопку.",
                  "УДАЧИ!!!",]
    fon = pygame.transform.scale(load_image('fon.jpg'),
                                 (WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coords = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))
        intro_rect = string_rendered.get_rect()
        text_coords += 10
        intro_rect.top = text_coords
        intro_rect.x = 10
        text_coords += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if (event.type == pygame.KEYDOWN
               or event.type == pygame.MOUSEBUTTONDOWN):
                return
        pygame.display.flip()
        clock.tick(FPS_S)


# функция для загрузки изображения
def load_image(name, colorkey=None):
    fullname = os.path.join('/home/gruand69/Dev/tom_and_jerry/images', name)
    if not os.path.isfile(fullname):
        print(f'Файл с изображением "{fullname}" не найден')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Picture(pygame.sprite.Sprite):
    '''Класс, создающий спрайт
    изображения.'''
    image = pygame.transform.scale(load_image("picture.jpg"),
                                   (WINDOW_WIDTH, WINDOW_HEIGHT))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Picture.image
        self.rect = self.image.get_rect()
        self.rect.x = - WINDOW_WIDTH
        self.rect.y = 0

    def update(self, dx):
        if self.rect.x <= 0:
            self.rect.x += dx


class Labyrinth:
    '''Класс, создающий игровое
    поле.'''
    def __init__(self, filename, free_tiles, finish_tile) -> None:
        self.map = []
        with open(os.path.join('/home/gruand69/Dev/tom_and_jerry/maps',
                               filename)) as input_file:
            for line in input_file:
                self.map.append(list(map(int, line.split())))
        self.height = len(self.map)
        self.width = len(self.map[0])
        self.tile_size = TILE_SIZE
        self.free_tiles = free_tiles
        self.finish_tile = finish_tile

    def render(self, screen):
        tile_images = {0: pygame.transform.scale(load_image('grass.jpeg'),
                                                 (TILE_SIZE, TILE_SIZE)),
                       1: pygame.transform.scale(load_image('box1.jpeg'),
                                                 (TILE_SIZE, TILE_SIZE)),
                       2: pygame.transform.scale(load_image('exit.png'),
                                                 (TILE_SIZE, TILE_SIZE))}
        for y in range(self.height):
            for x in range(self.width):
                image = tile_images[self.get_tile_id((x, y))]
                delta = (image.get_width() - TILE_SIZE) // 2
                screen.blit(image, (x * TILE_SIZE - delta,
                                    y * TILE_SIZE - delta))

    def get_tile_id(self, position):
        return self.map[position[1]][position[0]]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles

    def find_path_step(self, start, target):
        INF = 1000
        x, y = start
        distance = [[INF] * self.width for _ in range(self.height)]
        distance[y][x] = 0
        prev = [[None] * self.width for _ in range(self.height)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if (0 <= next_x < self.width and 0 <= next_y < self.height
                    and self.is_free((next_x, next_y))
                   and distance[next_y][next_x] == INF):
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        if distance[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y


class Hero:
    '''Класс, создающий мышонка.'''
    def __init__(self, pic, position) -> None:
        self.x, self.y = position
        self.image = pygame.transform.scale(load_image(pic, -1),
                                            (TILE_SIZE, TILE_SIZE))

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image, (self.x * TILE_SIZE - delta,
                                 self.y * TILE_SIZE - delta))


class Enemy:
    '''Класс, создающий кота.'''
    def __init__(self, pic, position) -> None:
        self.x, self.y = position
        self.delay = 200
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)
        self.image = pygame.transform.scale(load_image(pic, -1),
                                            (TILE_SIZE, TILE_SIZE))

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image, (self.x * TILE_SIZE - delta,
                                 self.y * TILE_SIZE - delta))


class Game:
    '''Класс, объединяющий созданные классы.'''
    def __init__(self, labyrinth, hero, enemy) -> None:
        self.labyrinth = labyrinth
        self.hero = hero
        self.enemy = enemy

    def render(self, screen):
        self.labyrinth.render(screen)
        self.hero.render(screen)
        self.enemy.render(screen)

    def update_hero(self):
        next_x, next_y = self.hero.get_position()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.labyrinth.is_free((next_x, next_y)):
            self.hero.set_position((next_x, next_y))

    def move_enemy(self):
        next_position = self.labyrinth.find_path_step(
            self.enemy.get_position(),
            self.hero.get_position()
        )
        self.enemy.set_position(next_position)

    def check_win(self):
        return (self.labyrinth.get_tile_id(self.hero.get_position())
                == self.labyrinth.finish_tile)

    def check_lose(self):
        return self.hero.get_position() == self.enemy.get_position()


# функция, выводящая сообщение
def show_message(screen, message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, 1, (50, 70, 0))
    text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
    text_y = WINDOW_HEIGHT // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (200, 150, 50),
                     (text_x - 10, text_y - 10,
                      text_w + 20, text_h + 20))
    screen.blit(text, (text_x, text_y))


# список списков с параметрами уровней игры
stages = [
    ["simple_map1.txt", "hero.png", (7, 7), "enemy.png", (1, 7)],
    ["simple_map.txt", "hero.png", (7, 7), "enemy.png", (1, 7)],
    ["simple_map2.txt", "hero.png", (7, 7), "enemy.png", (1, 7)]
]


# основная функция программы
def main():
    start_screen()
    for i, stage in enumerate(stages):
        labyrinth = Labyrinth(stage[0], [0, 2], 2)
        hero = Hero(stage[1], stage[2])
        enemy = Enemy(stage[3], stage[4])
        game = Game(labyrinth, hero, enemy)
        running = True
        game_over = False
        has_lost = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == ENEMY_EVENT_TYPE and not game_over:
                    game.move_enemy()
            if not game_over:
                game.update_hero()
            screen.fill((0, 0, 0))
            game.render(screen)
            if game.check_win():
                game_over = True
                if i < len(stages) - 1:
                    show_message(screen, "Следующий этап!")
                else:
                    show_message(screen, "Вы выиграли!")
                running = False
            if game.check_lose():
                game_over = True
                show_message(screen, "Вы проиграли!")
                running = False
                has_lost = True
            pygame.display.flip()
            clock.tick(FPS)
        pygame.time.delay(1000)
        if has_lost:
            pygame.time.delay(1000)
            break

    finish_screen()
    terminate()


if __name__ == '__main__':
    main()

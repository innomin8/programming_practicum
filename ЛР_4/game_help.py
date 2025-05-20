import pygame
from constants import *


class Help():
    def __init__(self):
        self.small_font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)

        # Создаем поверхность для меню
        self.menu_width = round(win_width * 0.7)
        self.menu_height = round(win_height * 0.7)
        self.menu_surface = pygame.Surface((self.menu_width, self.menu_height), pygame.SRCALPHA)
        self.menu_surface.fill((50, 50, 50, 200))  # Полупрозрачный темный фон

        # Рисуем рамку
        pygame.draw.rect(self.menu_surface, C_YELLOW, (0, 0, self.menu_width, self.menu_height), 3)

        # Добавляем текст
        title = self.big_font.render("Управление в игре", True, C_YELLOW)
        controls = [
            "Движение влево: 'A' или стрелка влево",
            "Движение вправо: 'D' или стрелка вправо",
            "Прыжок: 'W' или стрелка вверх",
            "Выстрел: Пробел",
            "Пауза/меню: 'H'",
            "Музыка вкл/выкл: 'M'",
            "Громкость +: 'U', Громкость -: 'J'",
            "Выход: ESC или крестик окна"
        ]

        # Размещаем текст на поверхности меню
        y_offset = 20
        self.menu_surface.blit(title, (self.menu_width // 2 - title.get_width() // 2, y_offset))
        y_offset += 50

        for line in controls:
            text = self.small_font.render(line, True, C_WHITE)
            self.menu_surface.blit(text, (30, y_offset))
            y_offset += 40

        # Подпись внизу
        footer = self.small_font.render("Нажмите H чтобы продолжить", True, C_YELLOW)
        self.menu_surface.blit(footer, (self.menu_width // 2 - footer.get_width() // 2, self.menu_height - 40))

        # Текст для игровой строки состояния
        self.text_points = self.small_font.render("Очки: ", True, C_YELLOW)
        self.text_lives = self.small_font.render("Жизни: ", True, C_YELLOW)
        self.text_help = self.small_font.render("Пауза - H", True, C_YELLOW)
        self.text_height = max(self.text_points.get_height(),
                               self.text_lives.get_height(),
                               self.text_help.get_height())

    def show(self, window):
        """Отображает меню по центру экрана"""
        window.blit(self.menu_surface,
                    (win_width // 2 - self.menu_width // 2,
                     win_height // 2 - self.menu_height // 2))

    def line(self, points=0, lives=1):
        """Создает строку состояния с очками и жизнями"""
        img = pygame.Surface((win_width, self.text_height), pygame.SRCALPHA)

        # Очки
        img.blit(self.text_points, (10, 0))
        points_text = self.small_font.render(str(points), True, C_WHITE)
        img.blit(points_text, (10 + self.text_points.get_width(), 0))

        # Жизни (рисуем сердечки)
        lives_x = win_width - 150
        img.blit(self.text_lives, (lives_x, 0))

        # Загружаем изображение сердца (убедитесь, что файл heart.png есть в папке)
        try:
            heart_img = pygame.image.load("heart.png").convert_alpha()
            heart_img = pygame.transform.scale(heart_img, (20, 20))
            for i in range(lives):
                img.blit(heart_img, (lives_x + self.text_lives.get_width() + 5 + i * 25, 0))
        except:
            # Если нет картинки, рисуем текстом
            lives_text = self.small_font.render(str(lives), True, C_WHITE)
            img.blit(lives_text, (lives_x + self.text_lives.get_width(), 0))

        # Подсказка
        img.blit(self.text_help, (win_width // 2 - self.text_help.get_width() // 2, 0))

        return img
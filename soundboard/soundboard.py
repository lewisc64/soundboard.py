import pygame
import os
import player

pygame.init()

WIDTH = 300
HEIGHT = 600
FPS = 60

display = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

class Item:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Consolas", int(height * 0.8))
        self.font_color = (255, 255, 255)
        self.padding = 2
        self.background_color = (90, 90, 90)
        self.line_color = (180, 180, 180)
        
    def render_text(self, text):
        self.text = self.font.render(text, True, self.font_color)

    def fit_width_to_text(self):
        self.width = self.text.get_width() + self.padding * 2
    
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.background_color, self.get_rect())
        pygame.draw.rect(surface, self.line_color, self.get_rect(), 1)

    def onclick(self, x, y):
        pass

class FolderItem(Item):
    def __init__(self, folder, x, y, width, height):
        super().__init__(x, y, width, height)
        self.folder = folder
        self.render_text(str(folder))
        self.fit_width_to_text()
        
    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.text, (self.x + self.padding, self.y + self.height // 2 - self.text.get_height() // 2))

class FileItem(Item):
    def __init__(self, file, x, y, width, height):
        super().__init__(x, y, width, height)
        self.background_color = (255, 90, 90)
        self.file = file
        self.render_text(str(file))
        self.fit_width_to_text()
        player.load(self.file.path)
    
    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.text, (self.x + self.padding, self.y + self.height // 2 - self.text.get_height() // 2))

    def onclick(self, x, y):
        super().onclick(x, y)
        player.play(self.file.path)
        
class Structure:
    def __init__(self, path="sounds"):
        self.folder = Folder(path, path)
        self.build(self.folder)
        self.items = []
        self.item_width = 100
        self.item_height = 16
        self.item_padding = 5
        self.item_indentation = 16
        self.scroll_speed = self.item_height + self.item_padding
        self.create_items(self.folder)
        self.x = 0
        self.y = 0

    def __str__(self):
        return self.tree()
    
    def tree(self):
        return self.folder.tree()
    
    def build(self, folder):
        for item in os.listdir(folder.path):
            if "." in item:
                folder.add_file(File(item, "{}/{}".format(folder.path, item)))
            else:
                subfolder = Folder(item, "{}/{}".format(folder.path, item))
                folder.add_subfolder(subfolder)
                self.build(subfolder)

    def create_items(self, folder, position=None):
        if position is None:
            position = [0, 0]
        for file in folder.files:
            self.items.append(FileItem(file, position[0], position[1], self.item_width, self.item_height))
            position[1] += self.item_height + self.item_padding
        for subfolder in folder.subfolders:
            self.items.append(FolderItem(subfolder, position[0], position[1], self.item_width, self.item_height))
            position[0] += self.item_indentation
            position[1] += self.item_height + self.item_padding
            self.create_items(subfolder, position)
            position[0] -= self.item_indentation

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        for item in self.items:
            item.x += dx
            item.y += dy
    
    def handle(self, e):

        if e.type == pygame.MOUSEBUTTONUP:

            if e.button == 1:
                for item in self.items:
                    x, y = e.pos
                    if x >= item.x and y >= item.y and x <= item.x + item.width and y <= item.y + item.height:
                        item.onclick(x, y)
            
            elif e.button == 4:
                if self.y < 0:
                    self.move(0, self.scroll_speed)
                    
            elif e.button == 5:
                self.move(0, -self.scroll_speed)
    
    def draw(self, surface):
        for item in self.items:
            item.draw(surface)

class Folder:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.subfolders = []
        self.files = []

    def __str__(self):
        return self.name
    
    def tree(self, indent=4):
        out = " " * max(indent - 4, 0) + str(self) + "\n"
        for file in self.files:
            out += " " * indent + file.name + "\n"
        for folder in self.subfolders:
            out += folder.tree(indent + 4)
        return out
    
    def add_file(self, file):
        self.files.append(file)
    
    def add_subfolder(self, folder):
        self.subfolders.append(folder)

class File:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __str__(self):
        return self.name

structure = Structure()
print(structure.tree())

while True:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif e.type == pygame.VIDEORESIZE:
            display = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
        else:
            structure.handle(e)

    display.fill((255, 255, 255))
    structure.draw(display)
    
    clock.tick(60)
    pygame.display.update()


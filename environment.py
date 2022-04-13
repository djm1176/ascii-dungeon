from itertools import chain
from tkinter import HORIZONTAL


class room():
    
    CORNER_TL = '┌'
    CORNER_BL = '└'
    CORNER_TR = '┐'
    CORNER_BR = '┘'
    HORIZONTAL = '─'
    VERTICAL = '│'

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def __init__(self, width=5, height=5, doors=[], items=[]):
        self.width = width
        self.height = height
        self.doors = doors
        self.items = items

    # Returns an ASCII rendering string of this room.
    def draw(self) -> str:

        # Construct main outline
        s = []

        #print(room.HORIZONTAL for i in range(self.width))
        s.append([item for items in [room.CORNER_TL, room.HORIZONTAL * (self.width - 2), room.CORNER_TR] for item in items])

        for i in range(self.height - 2):
            s.append([item for items in [room.VERTICAL + ' ' * (self.width - 2) + room.VERTICAL] for item in items])
        
        s.append([item for items in [room.CORNER_BL + room.HORIZONTAL * (self.width - 2) + room.CORNER_BR] for item in items])


        # Place doors
        if self.doors != None:
            for door in self.doors:
                s[door[1]][door[0]] = 'X'

        # Place items
        if self.items != None:
            for item in self.items:
                pass

        _ = ''
        for row in s:
            for ele in row:
                _ += ele
            _ += '\n'

        return _

    def place_door(self, x, y):
        if x < 0 or x > self.width - 1 or y < 0 or y > self.height - 1:
            print(f"Invalid door placement: ({x}, {y}) when room is sized ({self.width}, {self.height})")
            return

        self.doors.append((x, y))

class generator():
    def make_room(width=5, height=5, doors=[], items=[]):
        r = room(width, height, doors, items)
        return r
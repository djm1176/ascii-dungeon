from textprocessing import parse_command

class game():
    def __init__(self, current_room=None):
        self.current_room: room = current_room
        pass

    # Takes a user string, parses it, and performs an action from it
    def process_input(self, message):
        result = parse_command(message)

        if result.error:
            print(f"Command error: {result.message}")
        
        else:
            print(result.action.action_class, result.action.action_subclass, result.subject)


    def run(self, shell=False):
        if shell:
            while True:

                if self.current_room != None:
                    pass#print(self.current_room.draw())

                s = input()

                self.process_input(s)

        else:
            # TODO Discord input
            pass



class entity():
    def __init__(self, posx=0, posy=0):
        self.posx = posx
        self.posy = posy
        self.allow_overlap = True

class player(entity):
    def __init__(self, posx=0, posy=0):
        super().__init__(posx, posy)

    def draw_to(self, target):
        target[self.posy][self.posx] = 'P'

class chest(entity):
    def __init__(self, posx=0, posy=0):
        super().__init__(posx, posy)

    def draw_to(self, target):
        target[self.posy][self.posx] = 'C'

class door(entity):
    def __init__(self, posx, posy):
        super().__init__(posx, posy)
    
    def draw_to(self, target):
        target[self.posy][self.posx] = 'D'

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

    def __init__(self, width=5, height=5, entities=[]):
        self.width = width
        self.height = height
        self.entities: list = entities

        # Can entities be placed outside the bounds of the room?
        self.allow_exterior_entities = False

    # Returns an ASCII rendering string of this room.
    def draw(self) -> str:

        # Construct main outline
        s = []

        #print(room.HORIZONTAL for i in range(self.width))
        s.append([item for items in [room.CORNER_TL, room.HORIZONTAL * (self.width - 2), room.CORNER_TR] for item in items])

        for i in range(self.height - 2):
            s.append([item for items in [room.VERTICAL + ' ' * (self.width - 2) + room.VERTICAL] for item in items])
        
        s.append([item for items in [room.CORNER_BL + room.HORIZONTAL * (self.width - 2) + room.CORNER_BR] for item in items])

        # Draw entities
        if self.entities != None:
            for entity in self.entities:
                entity.draw_to(s)

        # Collapse room graphic into a string
        _ = ''
        for row in s:
            for ele in row:
                _ += ele
            _ += '\n'

        return _

    # Registers an entity as being in this room, which lets it be drawn and interacted with.
    def add_entity(self, entity: entity):

        # Make sure entity isn't outside of bounds, if it's not allowed
        if not self.allow_exterior_entities and (entity.posx < 0 or entity.posx > self.width - 1 or entity.posy < 0 or entity.posy > self.height - 1):
            print(f"Invalid entity placement: Cannot place {type(entity)} outside of room")
            return

        # Make sure entity doesn't overlap another entity, if it's not allowed
        for e in self.entities:
            if e.posx == entity.posx and e.posy == entity.posy and (not e.allow_overlap or not entity.allow_overlap):
                print(f"Invalid entity placement: Cannot place {type(entity)} on top of another entity ({type(e)} at ({e.posx}, {e.posy})")
                return

        # Check door requirements
        if isinstance(entity, door):
            if entity.posx < 0 or entity.posx > self.width - 1 or entity.posy < 0 or entity.posy > self.height - 1:
                print(f"Invalid door placement: Position ({entity.posx}, {entity.posy}) when room is sized ({self.width}, {self.height})")
                return

            # Place the door, do anything else necessary when that happens
            self.entities.append(entity)
            return

        if isinstance(entity, player):
            self.entities.append(entity)
            return

        
        # At this point, no checks have been made for an explicit entity type
        print(f"Warning, no implementation for entity of type {type(entity)}")
        self.entities.append(entity)
        return

    def add_entities(self, *entities):
        if entities != None:
            for entity in entities:
                self.add_entity(entity)

    def remove_entity(self, entity: entity):
        try:
            self.entities.remove(entity)
        except Exception as e:
            pass



class generator():
    def make_room(width=5, height=5, entities=[]):
        r = room(width, height, entities)
        return r

    def make_chest(posx=1, posy=1):
        c = chest(posx, posy)
        return c

    def make_door(posx=0, posy=1):
        d = door(posx, posy)
        return d

    def make_player(posx=1, posy=1):
        p = player(posx, posy)
        return p
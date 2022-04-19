from constants import CardinalDirection, ClassDefinitions, ErrorMessage, cardinality

class entity():
    def __init__(self, name, description='No Description', shortDescription='No Description', posx=0, posy=0):
        self.name = name
        self.description = description
        self.shortDescription = shortDescription
        self.posx = posx
        self.posy = posy
        self.allow_overlap = True
        self.allow_movement = False

    def __str__(self):
        return f"{type(self)} (\'{self.name}\') at ({self.posx}, {self.posy})"


class player(entity):
    def __init__(self, posx=0, posy=0):
        super().__init__(
            name=ClassDefinitions.PlayerName,
            description=ClassDefinitions.PlayerDescription,
            shortDescription=ClassDefinitions.PlayerShortDescription,
            posx=posx, posy=posy)
        
        self.allow_overlap = True # The player can stand on stuff
        self.allow_movement = True

    def draw_to(self, target):
        target[self.posy][self.posx] = 'P'


class chest(entity):
    def __init__(self, posx=0, posy=0):
        super().__init__(
            name=ClassDefinitions.ChestName,
            description=ClassDefinitions.ChestDescription,
            shortDescription=ClassDefinitions.ChestShortDescription,
            posx=posx, posy=posy
        )

    def draw_to(self, target):
        target[self.posy][self.posx] = 'C'


class door(entity):
    def __init__(self, posx, posy):
        super().__init__(
            name=ClassDefinitions.DoorName,
            description=ClassDefinitions.DoorDescription,
            shortDescription=ClassDefinitions.DoorShortDescription,
            posx=posx, posy=posy
        )
    
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
        # Useful for setup, and disallowing after player can move stuff.
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
        # TODO: Return an error message instead!
        if not self.allow_exterior_entities and not self.in_bounds(entity.x, entity.y):
            print(f"Invalid entity placement: Cannot place {type(entity)} outside of room")
            return

        # Make sure entity doesn't overlap another entity, if it's not allowed
        for e in self.entities:
            if e.posx == entity.posx and e.posy == entity.posy and (not e.allow_overlap or not entity.allow_overlap):
            # TODO: Return an error message instead!
                print(f"Invalid entity placement: Cannot place {type(entity)} on top of another entity ({type(e)} at ({e.posx}, {e.posy})")
                return

        # Check door requirements
        if isinstance(entity, door):
            if entity.posx < 0 or entity.posx > self.width - 1 or entity.posy < 0 or entity.posy > self.height - 1:
            # TODO: Return an error message instead!
                print(f"Invalid door placement: Position ({entity.posx}, {entity.posy}) when room is sized ({self.width}, {self.height})")
                return

            # Place the door, do anything else necessary when that happens
            self.entities.append(entity)
            return

        if isinstance(entity, player):
            self.entities.append(entity)
            return

        if isinstance(entity, chest):
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

    # Is an (x, y) point within the walls of the room?
    def in_bounds(self, x, y):
        return x > 0 and x < self.width and y > 0 and y < self.height


    # Is an entity (with optional x, y point) causing an invalid overlap?
    def has_overlap(self, e: entity, new_x=None, new_y=None):
        new_x = new_x if new_x != None else e.posx
        new_y = new_y if new_y != None else e.posy

        for _ in self.entities:
            if _.posx == new_x and _.posy == new_y and (not e.allow_overlap or not _.allow_overlap):
                return True
        
        return False


    # Attempts to move given entity in the room.
    # Returns a tuple, where:
    # [0] = True/False: The entity was successfully moved
    # [1] = str: A message, if unsuccessful
    def move_entity_cardinal(self, entity:entity, cardinal: cardinality) -> tuple:
        if entity in self.entities:
            # Check if the entity can even move
            if not entity.allow_movement:
                return (False, ErrorMessage.EntityCannotMove)

            dx = 1 if cardinal == cardinality.East else -1 if cardinal == cardinality.West else 0
            dy = 1 if cardinal == cardinality.South else -1 if cardinal == cardinality.North else 0
            
            # Check if the entity will hit a wall
            if not self.in_bounds(entity.posx + dx, entity.posy + dy):
                return (False, ErrorMessage.EntityNotInRoom)

            # Check if the entity will overlap another
            if self.has_overlap(entity, new_x = entity.posx + dx, new_y = entity.posy + dy):
                return (False, ErrorMessage.EntityCausesOverlap)

            # Welp, looks like we can move the entity
            entity.posx += dx
            entity.posy += dy

        else:
            return (False, ErrorMessage.EntityNotInroom)

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
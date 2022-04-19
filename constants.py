# Class name/description definitions
from enum import Enum


class ClassDefinitions():    
    PlayerName = 'Player'
    PlayerShortDescription = 'You!'
    PlayerDescription = 'TODO'

    ChestName = 'Chest'
    ChestShortDescription = 'A container'
    ChestDescription = 'A large, wooden container, with a handle on either side and a clam-shell style lid. It looks like it can store an abundant of items within.'

    DoorName = 'Door'
    DoorShortDescription = 'A door'
    DoorDescription = 'Looks like a door. It\'s something you can walk through. Enough said.'

# TODO: Most, if not all, Error Messages should be formatted. Especially ones that say 'entity'
class ErrorMessage():
    CommandWithNoVerb = 'Command must start with an action!'
    NoSubjectInferenceMatch = 'There is no entity by the name {0}!'
    NoCommandFound = 'That is not a valid command!'
    EntityNotInRoom = 'The entity cannot be moved to there!'
    EntityIsBlocked = 'The entity is blocked!'
    EntityCannotMove = 'The entity can\'t be moved!'

class CardinalDirection():
    North = ['north', 'up']
    East = ['east', 'right']
    South = ['south', 'down']
    West = ['west', 'left']

class cardinality(Enum):
    North=0
    East=1
    South=2
    West=3
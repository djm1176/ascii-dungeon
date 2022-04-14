import nltk
from nltk.tokenize import word_tokenize
from nltk.sem import relextract
from enum import Enum

include_tags_verbs = [
    'VB',
    'VBG',
    'VBD',
    'VBN',
    'VBP',
    'VBZ'
]

include_tags_nouns = [
    'NN',
    'NNP',
    'NNS'
]

include_tags = [
    *include_tags_verbs,
    *include_tags_nouns, 
    'PDT'
]

# Class that is used to pair with strings of valid commands.
# Sample usage:
# plant_tree_actions = action(['plant', 'grow'], actionclass.Gardening, actionsubclass.Planting)
class action():
    class actionclass(Enum):
        Empty = -1
        Game = 0
        Movement = 1
        Interaction = 2
        Inventory = 3
        Combat = 4

    class actionsubclass(Enum):
        Empty = -1

        # Game subclasses
        Exit = 0
        Help = 1
        Pause = 2
        Play = 3

        # Movement subclasses
        Posture = 11
        Direction = 12

        # Interaction subclasses
        Container = 21
        Speech = 22

        # Inventory subclasses
        Drop = 31
        Take = 32
        Consume = 33

        # Combat subclasses
        Hands = 41
        Melee = 42
        Ranged = 43

    def __init__(self, action_strs: list, action_class: actionclass=actionclass.Empty, action_subclass: actionsubclass=actionsubclass.Empty):
        self.action_strs = action_strs
        self.action_class = action_class
        self.action_subclass = action_subclass

class parsecommand():
    def __init__(self):
        self.action: action = None
        self.message = ''
        self.error = False
        self.subject = '' # TODO Temporary implementation. This will store string representing what entity this command is interacting on, if there is one.
        self.valid = False # A valid command results in an action being performed in the game.
        pass

game_actions_exit = action(['quit'], action.actionclass.Game, action.actionsubclass.Exit)
game_actions_menu = action(['menu', 'pause'], action.actionclass.Game, action.actionsubclass.Pause)
game_actions_help = action(['help', 'info'], action.actionclass.Game, action.actionsubclass.Help)
game_actions_play = action(['play', 'resume'], action.actionclass.Game, action.actionsubclass.Play)

user_actions_movement = action(['move', 'go', 'walk', 'travel'], action.actionclass.Movement, action.actionsubclass.Empty)
user_actions_movement_posture = action(['sit', 'stand', 'crouch'], action.actionclass.Movement, action.actionsubclass.Posture)
user_actions_movement_direction = action(['up', 'down', 'left', 'right', 'north', 'east', 'south', 'west', 'forward', 'backward'], action.actionclass.Movement, action.actionsubclass.Direction)

user_actions_interact = action(['interact', 'investigate'], action.actionclass.Interaction, action.actionsubclass.Empty)
user_actions_interact_container = action(['open'], action.actionclass.Interaction, action.actionsubclass.Container)
user_actions_interact_speak = action(['talk', 'speak', 'yell', 'shout', 'scream', 'whisper'], action.actionclass.Interaction, action.actionsubclass.Speech)

user_actions_inventory_drop = action(['drop', 'delete', 'remove'], action.actionclass.Inventory, action.actionsubclass.Drop)
user_actions_inventory_take = action(['take', 'grab', 'steal', 'store'], action.actionclass.Inventory, action.actionsubclass.Take)
user_actions_inventory_food = action(['eat', 'bite', 'consume', 'drink'], action.actionclass.Inventory, action.actionsubclass.Consume)

user_actions_combat = action(['attack', 'hurt', 'damage', 'hit'], action.actionclass.Combat, action.actionsubclass.Empty)
user_actions_combat_hands = action(['punch', 'slap', 'kick', 'shove'], action.actionclass.Combat, action.actionsubclass.Hands)
user_actions_combat_melee = action(['stab', 'strike'], action.actionclass.Combat, action.actionsubclass.Melee)
user_actions_combat_ranged = action(['shoot'], action.actionclass.Combat, action.actionsubclass.Ranged)

entity_quantity = ['all', 'half', 'quarter', 'none']

actions = [
    game_actions_exit,
    game_actions_menu,
    game_actions_help,
    game_actions_play,

    user_actions_movement,
    user_actions_movement_posture,
    user_actions_movement_direction,

    user_actions_interact,
    user_actions_interact_container,
    user_actions_interact_speak,

    user_actions_inventory_drop,
    user_actions_inventory_take,
    user_actions_inventory_food,

    user_actions_combat,
    user_actions_combat_hands,
    user_actions_combat_melee,
    user_actions_combat_ranged
]

def parse_command(command) -> parsecommand:
    command = 'I ' + command # Avoid imperative semantics issues

    tokens = word_tokenize(command)
    tags = nltk.pos_tag(tokens)

    # Strip off the first tag, since we forced in a pronoun
    tags = tags[1:]

    f_tags = []
    for tag in tags:
        if tag[1] in include_tags:
            f_tags.append(tag)
    print(tags)

    result = parsecommand()

    # First token should be a verb
    verb_tag = tags[0]
    if not verb_tag[1] in include_tags_verbs:
        result.message = 'Command must start with an action!'
        result.error = True

        return result

    # Figure out which action it belongs to
    # This could be done with a list comprehension [a for a in actions if v_tag[0] in a.action_strs][0]
    for a in actions:
        if verb_tag[0] in a.action_strs:
            result.action = a
            break

    # Find the first noun, which we'll force to be the subject
    if len(tags) > 1:
        for tag in tags[1:]:
            if tag[1] in include_tags_nouns:
                result.subject = tag[0]
                break
    

    print("<DEBUG>\t" + ' '.join(i[0] for i in f_tags))
    return result
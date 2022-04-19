from cmath import sqrt
from msilib.schema import Error
from random import randint
from math import dist
from typing import Callable
import nltk
from nltk.tokenize import word_tokenize
from enum import Enum
from entity import entity, player
from constants import ErrorMessage, CardinalDirection, cardinality

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
    'PDT',
    'RB' # Adverbs
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

    def __init__(self, action_strs: list, action_class: actionclass=actionclass.Empty, action_subclass: actionsubclass=actionsubclass.Empty, invoke: Callable=None):
        self.action_strs = action_strs
        self.action_class = action_class
        self.action_subclass = action_subclass
        self.invoke = invoke

class parsecommand():
    def __init__(self):
        self.action: action = game_action_none
        self.message = ''
        self.error = False
        self.subject_str = ''
        self.valid = False # A valid command results in an action being performed in the game.
        self.cardinality: cardinality = None
        self.subject: entity = None

    # Sets error status to False, and clears any existing error message
    def clear_status(self):
        self.message = ''
        self.error = False

game_action_none = action([], action.actionclass.Empty, action.actionsubclass.Empty, invoke=lambda game: None)

game_actions_exit = action(['quit'], action.actionclass.Game, action.actionsubclass.Exit, invoke=lambda game, cmd: game.quit())
game_actions_help = action(['help', 'info'], action.actionclass.Game, action.actionsubclass.Help, invoke=lambda game, cmd: game.help())
game_actions_menu = action(['menu', 'pause'], action.actionclass.Game, action.actionsubclass.Pause, invoke=lambda game, cmd: game.pause())
game_actions_play = action(['play', 'resume'], action.actionclass.Game, action.actionsubclass.Play, invoke=lambda game, cmd: game.play())
game_actions = [game_actions_exit, game_actions_help, game_actions_menu, game_actions_play]

user_actions_movement_general = action(['move', 'go', 'walk', 'travel'], action.actionclass.Movement, action.actionsubclass.Empty, invoke=lambda game, cmd: game.current_room.move_entity_cardinal(cmd.subject, cmd.cardinality))
user_actions_movement_posture = action(['sit', 'stand', 'crouch'], action.actionclass.Movement, action.actionsubclass.Posture, invoke=lambda game, cmd: game.main_player.posture=player.posture(cmd.extra))
user_actions_movement_cardinal = action([x for x in [*CardinalDirection.North, *CardinalDirection.East, *CardinalDirection.South, *CardinalDirection.West]], action.actionclass.Movement, action.actionsubclass.Direction)
user_actions_movement = [user_actions_movement_general, user_actions_movement_posture, user_actions_movement_cardinal]

user_actions_interact_general = action(['interact', 'investigate'], action.actionclass.Interaction, action.actionsubclass.Empty, invoke=lambda game, cmd: game.main_player.interact(cmd.subject))
user_actions_interact_container = action(['open'], action.actionclass.Interaction, action.actionsubclass.Container, invoke=lambda game, cmd: game.main_player.open_container(cmd.subject))
user_actions_interact_speak = action(['talk', 'speak', 'yell', 'shout', 'scream', 'whisper'], action.actionclass.Interaction, action.actionsubclass.Speech)
user_actions_interact = [user_actions_interact_general, user_actions_interact_container, user_actions_interact_speak]

user_actions_inventory_drop = action(['drop', 'delete', 'remove'], action.actionclass.Inventory, action.actionsubclass.Drop)
user_actions_inventory_take = action(['take', 'grab', 'steal', 'store'], action.actionclass.Inventory, action.actionsubclass.Take)
user_actions_inventory_food = action(['eat', 'bite', 'consume', 'drink'], action.actionclass.Inventory, action.actionsubclass.Consume)
user_actions_inventory = [user_actions_inventory_drop, user_actions_inventory_take, user_actions_inventory_food]

user_actions_combat_general = action(['attack', 'hurt', 'damage', 'hit'], action.actionclass.Combat, action.actionsubclass.Empty)
user_actions_combat_hands = action(['punch', 'slap', 'kick', 'shove'], action.actionclass.Combat, action.actionsubclass.Hands)
user_actions_combat_melee = action(['stab', 'strike'], action.actionclass.Combat, action.actionsubclass.Melee)
user_actions_combat_ranged = action(['shoot'], action.actionclass.Combat, action.actionsubclass.Ranged)
user_actions_combat = [user_actions_combat_general, user_actions_combat_hands, user_actions_combat_melee, user_actions_combat_ranged]

# Pass in a list of actions, and out comes its strings!
def action_strs(actions: list):
    return [*[a.action_strs for a in actions]]

entity_quantity = ['all', 'half', 'quarter', 'none']

actions = [x for x in [
    *game_actions,
    *user_actions_movement,
    *user_actions_interact,
    *user_actions_inventory,
    *user_actions_combat
    ]]


def to_cardinal(string) -> cardinality:
    if str.lower(string) in CardinalDirection.North:
        return cardinality.North
    if str.lower(string) in CardinalDirection.East:
        return cardinality.East
    if str.lower(string) in CardinalDirection.South:
        return cardinality.South
    if str.lower(string) in CardinalDirection.West:
        return cardinality.West
    return None

# Takes a user-entered command and returns a parsed version that represents the action the user is wanting to take.
def parse_command(command) -> parsecommand:
    # TODO Implement an NLTK grammar from scratch
    command = 'I ' + command # Avoid imperative semantics issues by adding a pronoun to the front

    tokens = word_tokenize(command)
    tags = nltk.pos_tag(tokens)

    ###########################
    # Modify POS As Necessary #
    ###########################
    # NOTE: Tag modifications here are a workaround, since NLTK's base pos_tagger wasn't trained on ideal
    # data for a text-based dungeon game. A better approach, as mentioned above, is to implement a grammar
    # from scratch, which assigns Parts Of Speech (POS) to *every* possible word the game will recognize.
    # This will take time to implement, so this is a workaround for now.

    # Strip off the first tag, since we forced in a pronoun
    tags = tags[1:]

    f_tags = []
    for i in range(len(tags)):
        # Apply tag modifications, one at a time

        # 1.) Force cardinal directions to be adverbs, since NLTK likes to make some of them into nouns
        if tags[i][0] in user_actions_movement_cardinal.action_strs:
            tags[i] = (tags[i][0], 'RB')

        # 2.) Force game actions to be verbs, so user can pause/start/open menu, etc.
        if tags[i][0] in action_strs(game_actions):
            tags[i] = (tags[i][0], 'VB')


        # Finally...
        if tags[i][1] in include_tags:
            f_tags.append(tags[i])

    ###########################

    print(tags)
    result = parsecommand()

    # Catch empty strings
    if len(tags) < 1:
        return result

    # First token should be a verb (I can't think of another reason why not)
    verb_tag = tags[0]
    if not verb_tag[1] in include_tags_verbs:
        result.error = True
        result.message = ErrorMessage.CommandWithNoVerb

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
                result.subject_str = tag[0]
                break

    for tag in tags[1:]:
        # Find out if a cardinal direction is mentioned. If multiple are mentioned, only the first is taken
        if tag[1] == 'RB' and result.cardinality == None:
            result.cardinality = to_cardinal(tag[0])


    print("<DEBUG>\t" + ' '.join(i[0] for i in f_tags))

    if result.action.action_class == action.actionclass.Empty and result.action.action_subclass == action.actionsubclass.Empty:
        result.error = True
        result.message = ErrorMessage.NoCommandFound
    return result


# Determines what the subject is, if there is any, from an action the user is taking
# and a list of all entities the user can currently interact with.
#
# If there's multiple entities that match in the environment, then the priority of which is returned follows:
# (If multiple matches are still returned for a given pattern, then the following indented lines are used to narrow the search)
#
# If the action is in the Interact or Inventory action class:
#   1.) Check the player's inventory:
#       a.) The first occurrence of an entity name matching exactly
#
#   2.) Check the player's environment:
#       a.) The first occurrence of an entity that is closest to the player with an exact name match
#           i.) (TODO) The entity with matching description or adjectives, if provided
#
#   3.) Return No Match
#
# If the action is in the Combat action class:
#   Same implementation as above (TODO)
#
def infer_subject(cmd: parsecommand, player: player, environment: list, inventory=None):
    cmd.clear_status()

    # Default the subject to the player under certain conditions:
    # 1.) The action is to Move (this is player-only)
    # 2.) The action is a Game Action (pausing/menu)
    # 3.) No subject was matched in the original command str, therefore subject is technically none
    if cmd.subject_str == '' or cmd.action.action_class in [action.actionclass.Game, action.actionclass.Movement]:
        cmd.subject = player
        return

    # 1.) Check inventory
    _env = []
    if inventory != None and isinstance(inventory, list):
        for inv in inventory:
            # 1a.) First occurrence where the name matches exactly
            if str.lower(inv.name) == str.lower(cmd.subject_str):
                _env.append(inv)
                break

        # Did we find something in the inventory?
        if len(_env) > 0:
            cmd.subject = _env[0]
            return

    # 2.) Check environment
    for item in environment:
        if item.name != None and str.lower(item.name) == str.lower(cmd.subject_str):
            _env.append(item)
    
    # 2a.) Closest to player
    if len(_env) > 0:
        closest=_env[0]
        d = dist((player.posx, player.posy), (closest.posx, closest.posy))

        for test in _env[1:]:
            d2 = dist((player.posx, player.posy), (test.posx, test.posy))
            if d2 < d:
                closest = test
                d = d2
        
        cmd.subject_str = closest
        return
        
    # 3.) No match
    else:
        # Determine if a subject is required, based on the type of action
        if cmd.action.action_class in action.actionclass.Inventory: # Make a list of any actions that MUST have an entity provided!
            cmd.error = True
            cmd.message = str.format(ErrorMessage.NoSubjectInferenceMatch, cmd.subject_str)

        cmd.subject = None

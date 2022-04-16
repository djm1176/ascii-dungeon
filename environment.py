from textprocessing import infer_subect, parse_command
from constants import ClassDefinitions
from entity import entity, room, player

class game():
    def __init__(self, current_room=None, main_player=None):
        self.current_room: room = current_room
        self.main_player: player = main_player

    def set_player(self, main_player):
        # TODO: Any required setup when player is set or changed?
        self.main_player = main_player

    # TODO
    # Returns the entities that are currently accessible to the player, based on player's distance, context, etc.
    def filtered_entities(self):
        return self.current_room.entities

    # Takes a user string, parses it, and performs an action from it
    def process_input(self, message):
        
        # Parse the string into an object
        result = parse_command(message)

        if result.error:
            print(f"Command error: {result.message}")
            return

        print("<DEBUG>", result.action.action_class, result.action.action_subclass, result.subject)

        avail_entities = self.filtered_entities()
        subject = infer_subect(result, self.main_player, avail_entities)

        if not result.error:
            print("<DEBUG> Inferred entity as:", str(subject))
        else:
            print("<DEBUG>", f"No entity match:'{result.message}'")


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

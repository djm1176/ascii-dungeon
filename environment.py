from textprocessing import infer_subject, parse_command
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
        infer_subject(result, self.main_player, avail_entities)

        if not result.error:
            print("<DEBUG> Inferred entity as:", str(result.subject))
        else:
            print("<DEBUG>", f"No entity match:'{result.message}'")

        # Take the action!
        result.clear_status()
        result.action.invoke(self, result)
        
        # Result's message field should contain a status/result message
        if result.message != '':
            print(result.message)


    def run(self, shell=False):
        if shell:
            while True:

                if self.current_room != None:
                    print(self.current_room.draw())

                s = input()

                self.process_input(s)

        else:
            # TODO Discord input
            pass
    
    def quit(s):
        print("Quit function")

    def help(s):
        print("Help function")

    def pause(s):
        print("Pause function")

    def play(s):
        print("Play function")
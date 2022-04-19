from environment import game
from entity import generator

if __name__ == "__main__":
    print("Running in terminal")
    g = game()
    
    room = generator.make_room(20, 5)
    door1 = generator.make_door(0, 3)
    door2 = generator.make_door(10, 4)
    chest = generator.make_chest(4, 2)
    player = generator.make_player()

    room.allow_exterior_entities = True # Let us add doors to the walls
    room.add_entities(door1, door2, chest, player)
    room.allow_exterior_entities = False # Now set it back to disallow

    g.main_player = player
    g.current_room = room

    g.run(shell=True)
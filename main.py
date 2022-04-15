from environment import generator, game

if __name__ == "__main__":
    print("Running in terminal")
    g = game()
    
    room = generator.make_room(20, 5)
    door1 = generator.make_door(0, 3)
    door2 = generator.make_door(10, 4)
    chest = generator.make_chest(4, 2)
    player = generator.make_player()

    room.add_entities(door1, door2, chest, player)

    g.main_player = player
    g.current_room = room

    g.run(shell=True)
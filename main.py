from environment import generator

if __name__ == "__main__":
    print("Running in terminal")
    
    room = generator.make_room(20, 5)
    room.place_door(0, 3)
    room.place_door(10, 4)

    print(room.draw())
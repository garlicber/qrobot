import random
import collections

__author__ = 'jakob'

# Field Types
NORMAL = 0
BLOCKED = 1
_size = 10

actions = ['n', 's', 'w', 'e']
dirs = {'n':(0,1),'s':(0,-1),'w':(1,0),'e':(-1,0)}
cheese = [(1, 7)]
mouse_startpoint = (7,1)


def add_tuple(a,b):
    return tuple(map(sum,zip(a,b)))

class World:

    def __init__(self,actor_loc):
        self.height = 10
        self.width = 10
        self.actor_loc = actor_loc

    def create_landscape(self):
        self.landscape = {}
        for x in range(0,  _size):
            for y in range(0, _size):
                if y == 0 or y == _size-1:
                    self.landscape[(x,y)] = Field(BLOCKED)
                elif x == 0 or x == _size-1:
                    self.landscape[(x,y)] = Field(BLOCKED)
                elif (2 >= x or x > 3) and y == 5:
                    self.landscape[(x,y)] = Field(BLOCKED)
                else:
                    self.landscape[(x,y)] = Field(NORMAL)

    def __str__(self):
        world_string = ""
        for x in range(0,  _size):
            for y in range(0, _size):
                if (x,y) == self.actor_loc:
                    world_string +=  DrawObject(  self.landscape[(x,y)].type,
                                        True).draw()
                else:
                    world_string += DrawObject(  self.landscape[(x,y)].type,
                                        False).draw()
            world_string += '\n'
        return world_string


class Field:
    def __init__(self, type):
        self.type = type

class Actor:

    def __init__(self):
        self.loc = mouse_startpoint;

    def move(self, dir, world):
        assert(dir in dirs)
        x = tuple(map(sum, zip(dirs[dir], self.loc)))
        print("Mouse moves to "+str(x))
        self.loc = x
        world.actor_loc = self.loc

    def get_possible_actions(self, world):
        out = []
        for k,v in dirs.items():
            loc = add_tuple(v,self.loc)
            if world.landscape[loc].type != BLOCKED:
                out.append(k)
        return out


class DrawObject:

    def __init__(self,type, player):
        self.type = type
        self.player = player

    def draw(self):
        output="";
        if self.type == NORMAL and self.player:
            output = "[P]"
        elif self.type == NORMAL and ~self.player:
            output = "[ ]"
        elif self.type == BLOCKED:
            output = "[B]"
        elif self.type == "path":
            output == "[+]"
        return output

class QLearning:

    def __init__(self):
        self.q = collections.defaultdict(float)


    def reward(self,  hero, action):
        new_position = add_tuple(dirs[action],hero.loc)
        if new_position in cheese:
            return 10
        return 0

    def learn(self, hero, action, world):
        alpha = 0.5
        gamma = 0.5

        max_q = self.find_best_q(hero, action, world);

        self.q[(hero.loc, action)] += alpha * (self.reward(hero, action) +
                                            gamma * max_q - self.q[hero.loc, action])

    def find_best_q(self, hero, action, world):
        old_hero_loc = hero.loc
        hero.move(action, world)
        max_q = 0
        for future_actions in hero.get_possible_actions(world):
            if max_q < self.q[(hero.loc, future_actions)]:
                max_q = self.q[(hero.loc, future_actions)]
        hero.loc = old_hero_loc
        return max_q

    def find_best_action(self, hero, world):
        max_q = -9999
        best_action = []
        for action in hero.get_possible_actions(world):
            if max_q == self.q[(hero.loc, action)]:
                best_action.append(action)
            elif max_q < self.q[(hero.loc, action)]:
                max_q = self.q[(hero.loc, action)]
                best_action = [action]

        return best_action[random.randint(0, len(best_action)-1)]

    def __str__(self):
        last_loc = (-1,-1)
        print(len(self.q))
        output = ""

        for x in range(_size):
            for y in range(_size):
                sum_field = 0
                for a in actions:
                    sum_field +=  self.q[((x,y),a)]
                output += "[" + str(sum_field)[0:3] + "]"
            output += "\n"
        return output

def main():
    q_learning = QLearning()
    hero = Actor()
    world = World(hero.loc)
    world.create_landscape()

    for trainings in range(200):
        for x in range(50):
            if random.randint(0,5) <= 1:
                actions = hero.get_possible_actions(world)
                if actions == []:
                    print("break_hit")
                    break

                r = random.randint(0,len(actions)-1)
                action = actions[r]
            else:
                action = q_learning.find_best_action(hero, world)
                if action == []:
                    print("break_hit")
                    break
            q_learning.learn(hero, action, world)
            hero.move(action, world)
        hero.loc = mouse_startpoint
    # Walk best way
    way = []
    for i in range(100):
        best_dir = q_learning.find_best_action(hero, world)
        hero.move(best_dir,world)
        if hero.loc in cheese:
            print("Found chese in " + str(i) +" Steps")
            break
    print(world)
    print(q_learning)

if __name__ == "__main__":
    main()


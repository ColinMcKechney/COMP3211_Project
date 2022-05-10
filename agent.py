import dis
from importlib.resources import path
from mimetypes import init
from sre_parse import State
import time
from typing import List
import numpy as np
from base import (BaseAgent, action_dict, move,
                  set_timeout, after_timeout, TIMEOUT)
from util import PriorityQueue,Point,ListPaths,convert_ListPath,convert_point,adapt_point,adapt_Listpath, euclideanDist
import sqlite3

##################################################################################
# Here is a demo agent.                                                          #
# You can implement any helper functions.                                        #
# You must not remove the set_timeout restriction.                               #
# You can start your code any where but only the get_action() will be evaluated. #
##################################################################################


class MyAgent(BaseAgent):
    def __init__(self, name, env):
        super().__init__(name, env)
        self.firstIter = True
        self.locations = {}
        self.initials = {}
        self.paths = {}
    
    #Give the available actions but only regarded to the map not players
    def get_avai_actions_map(self,pos):
        avai_actions = []
        for action in action_dict:
            if action != 'nil':
                newPos = move(pos,action)
                if self.env.is_valid_pos(newPos):
                    avai_actions.append(action)
        return avai_actions
    
    def get_avai_actions(self, game_state, agent):
        avai_actions = []
        for action in action_dict:
            fake_action_profile = dict()
            for name in game_state:
                if name == agent:
                    fake_action_profile[name] = action
                else:
                    fake_action_profile[name] = 'nil'
            succ_state = self.env.transition(game_state, fake_action_profile)
            if succ_state:
                avai_actions.append(action)
        return avai_actions

    def successors(self,pos,actions):
        return [(move(pos,action),action,1) for action in actions]

    class State:
        def __init__(self,pos,actions):
            self.pos = pos
            self.actions = actions

        def getPos(self):
            return self.pos

        def getActions(self):
            return self.actions

        def __eq__(self,other):
            if isinstance(other,self.__class__):
                return self.pos==other.getPos()
            else:
                False

    def aStarSearch(self,game_state,heuristic):
        openList = PriorityQueue()
        closedList = []
        startingPos = game_state[self.name]
        goal = self.env.get_goals()[self.name]
        openList.push(MyAgent.State(startingPos,list()),heuristic(startingPos,goal))
        while not openList.isEmpty():
            newElem = openList.pop()
            newPos = newElem.getPos()
            actions = newElem.getActions()
            if(newPos==goal):
                return actions
            succs = self.successors(newPos,self.get_avai_actions_map(newPos))
            for succ,action,cost in succs:
                newCost = len(actions)+cost+heuristic(succ,goal)
                if succ not in closedList:
                    openList.update(MyAgent.State(succ,actions+[action]),newCost)
            closedList.append(newPos)
        
    
    def convertPathPosToActions(self,pathPos, name):
        currentPos = self.initials[name].getValue()        
        actions = []
        for pos in pathPos:
            action = list(action_dict.keys())[list(action_dict.values()).index(list(np.subtract(pos,currentPos)))]
            currentPos = pos
            actions.append(action)
        return actions

    @set_timeout(TIMEOUT,after_timeout)
    def get_action(self,game_state):
        
        if self.firstIter:
            
            mapName = self.env.env_name.capitalize()
            mapName = 'ShortestPath'+ mapName + '.db'
            
            sqlite3.register_converter("Point", convert_point)
            sqlite3.register_converter("ListPaths", convert_ListPath)
            sqlite3.register_adapter(Point, adapt_point)
            sqlite3.register_adapter(ListPaths,adapt_Listpath)
            
            con = sqlite3.connect(mapName,detect_types=sqlite3.PARSE_DECLTYPES)
            cur = con.cursor()
            
            for name in game_state.keys():
                self.initials[name] = Point(game_state[name][0], game_state[name][1])
                cur.execute("SELECT path FROM paths WHERE agent = (?) and position = (?)",(name,Point(game_state[name][0], game_state[name][1])))
                cur.fetchone
                self.locations[name] = cur.fetchone()[0]

                if(self.locations[name] != None):
                    self.paths[name] = self.convertPathPosToActions(self.locations[name].getValue(), name)
                else:
                    self.paths = list()

                

                if name == self.name:
                    self.initPos = self.initials[name]

            self.firstIter = False

            cur.close()
            con.close()         

        #if len(self.bestPath) <= 1 :
            #self.firstIter = True
        
        next_move = 'nil'
        for name in self.locations.keys():
            if len(self.paths[name]) != 0:
                other_loc = list(self.locations.items())
                other_loc.remove((name, self.locations[name]))
                for key, l in other_loc: #loop through the other agents 
                    test_point = self.locations[name].getValue()[-1 * len(self.paths[name])] #this is the point we're working with at the moment, the next spot the agent is going to go
                    if test_point in l.getValue():  #if it's in the path of the other 
                        
                        test_index = self.locations[name].getValue().index(test_point) #index of point
                        if l.getValue().index(test_point) == test_index or (l.getValue().index(test_point) == len(l.getValue()) - 1 and test_index >= len(l.getValue()) -1) or (test_index < len(l.getValue())-1  and test_point == l.getValue()[test_index -1] and self.locations[name].getValue()[test_index -1] == l.getValue()[test_index]): #either they meet along the way or one has finished
                            
                            new_act = self.collision_avoid(test_index, name) #get the new action that you are going to do instead
                            

                            #grabbing new path from new position
                            mapName = self.env.env_name.capitalize()
                            mapName = 'ShortestPath'+ mapName + '.db'
                            old_init = self.locations[name].getValue()[-1 * len(self.paths[name]) -1 ]

                            self.initials[name] = Point(new_act[0],new_act[1])
                            if name ==self.name:
                                self.initPos = Point(new_act[0],new_act[1])
                            
                            
                            sqlite3.register_converter("Point", convert_point)
                            sqlite3.register_converter("ListPaths", convert_ListPath)
                            sqlite3.register_adapter(Point, adapt_point)
                            sqlite3.register_adapter(ListPaths,adapt_Listpath)
                            
                            con = sqlite3.connect(mapName,detect_types=sqlite3.PARSE_DECLTYPES)
                            cur = con.cursor()
                            cur.execute("SELECT path FROM paths WHERE agent = (?) and position = (?)",(name,self.initials[name]))
                            
                            cur.fetchone
                            pathPos = cur.fetchone()[0]

                            
                            #add back in the old values that you've already traveled, keeps indexes in line
                            tmp = [self.locations[name].getValue()[i] for i in range(test_index)]
                            tmp.append(self.initials[name].getValue())

                            for val in pathPos.getValue():
                                tmp.append(val)

                            self.locations[name] = ListPaths(tmp)
                            pathPos.getValue().insert(0,self.initials[name].getValue())
                            if name == self.name:
                                self.initPos = Point(old_init[0], old_init[1]) #reset initPoint to keep path to actions working 
                            self.initials[name] = Point(old_init[0], old_init[1])
                            
                            if(pathPos != None):
                                self.paths[name] = self.convertPathPosToActions(pathPos.getValue(), name)
                            else:
                                self.paths[name] = list()
                            
                            #potential broadcast point for database


                        


        for name in self.paths.keys():
            if len(self.paths[name]) > 0:
                if name == self.name:
                    next_move = self.paths[name].pop(0)
                else:
                    self.paths[name].pop(0)

            

            #next_move = self.bestPath.pop(0)
            
        return next_move

    def collision_avoid(self,k,name):
        #collision avoidance alg
        game_state = {name: self.locations[name].getValue()[k-1]} #create a game state
        other_loc = list(self.locations.items())
        other_loc.remove((name, self.locations[name]))
        for key, item in other_loc:
            if k-1 > len(item.getValue()):
                game_state[key] = item.getValue()[-1]
            else:
                game_state[key] = item.getValue()[k-1]
        actions = self.get_avai_actions(game_state, name)
        
        actions.remove(self.paths[name][0]) #remove the action causing the conflict
        actions.remove('nil') #can't do nothing to avoid deadlock
        
        #find the option that keeps the distance the best 
        min_euclid = 999999
        min_act = self.locations[name].getValue()[k-1]
        for action in actions:
            tmp = move(game_state[name],action)
            tmp_dist = euclideanDist(tmp,self.env.get_goals()[name])
            if tmp_dist < min_euclid:
                min_euclid = tmp_dist
                min_act = tmp
        return min_act
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
        self.bestPath = []
        self.locations = {}
        self.pathPos = []
    
    #Give the available actions but only regarded to the map not players
    def get_avai_actions_map(self,pos):
        avai_actions = []
        for action in action_dict:
            if action != 'nil':
                newPos = move(pos,action)
                if self.env.is_valid_pos(newPos):
                    avai_actions.append(action)
        return avai_actions
    
    def get_avai_actions(self, game_state):
        avai_actions = []
        for action in action_dict:
            fake_action_profile = dict()
            for name in game_state:
                if name == self.name:
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
        
    
    def convertPathPosToActions(self,pathPos):
        currentPos = self.initPos.getValue()
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
            self.initPos = Point(game_state[self.name][0],game_state[self.name][1])
            
            sqlite3.register_converter("Point", convert_point)
            sqlite3.register_converter("ListPaths", convert_ListPath)
            sqlite3.register_adapter(Point, adapt_point)
            sqlite3.register_adapter(ListPaths,adapt_Listpath)
            
            con = sqlite3.connect(mapName,detect_types=sqlite3.PARSE_DECLTYPES)
            cur = con.cursor()
            cur.execute("SELECT path FROM paths WHERE agent = (?) and position = (?)",(self.name,self.initPos))
            
            cur.fetchone
            pathPos = cur.fetchone()[0]
            
            for name in game_state.keys():
                if name == self.name:
                    continue
                cur.execute("SELECT path FROM paths WHERE agent = (?) and position = (?)",(name,Point(game_state[name][0], game_state[name][1])))
                cur.fetchone
                self.locations[name] = cur.fetchone()[0].getValue()


            cur.close()
            con.close()

            self.pathPos = pathPos
            
            if(pathPos != None):
                self.bestPath = self.convertPathPosToActions(pathPos.getValue())
            else:
                self.bestPath = list()
            self.firstIter = False

        #if len(self.bestPath) <= 1 :
            #self.firstIter = True
        
        next_move = 'nil'
        if len(self.bestPath) != 0:

            for l in self.locations.values():
                if self.pathPos.getValue()[-1 * len(self.bestPath)] in l:
                    if l.index(self.pathPos.getValue()[-1 * len(self.bestPath)]) == self.pathPos.getValue().index(self.pathPos.getValue()[-1 * len(self.bestPath)]) or (l.index(self.pathPos.getValue()[-1 * len(self.bestPath)]) == len(l) - 1 and self.pathPos.getValue().index(self.pathPos.getValue()[-1 * len(self.bestPath)]) >= len(l) -1):
                        #continue
                        new_act = self.collision_avoid(self.pathPos.getValue().index(self.pathPos.getValue()[-1 * len(self.bestPath)]) )

                        mapName = self.env.env_name.capitalize()
                        mapName = 'ShortestPath'+ mapName + '.db'
                        old_init = self.pathPos.getValue()[-1 * len(self.bestPath) -1 ]
                        self.initPos = Point(new_act[0],new_act[1])
                        
                        
                        sqlite3.register_converter("Point", convert_point)
                        sqlite3.register_converter("ListPaths", convert_ListPath)
                        sqlite3.register_adapter(Point, adapt_point)
                        sqlite3.register_adapter(ListPaths,adapt_Listpath)
                        
                        con = sqlite3.connect(mapName,detect_types=sqlite3.PARSE_DECLTYPES)
                        cur = con.cursor()
                        cur.execute("SELECT path FROM paths WHERE agent = (?) and position = (?)",(self.name,self.initPos))
                        
                        cur.fetchone
                        pathPos = cur.fetchone()[0]

                        cur.close()
                        con.close()

                        tmp = [self.pathPos.getValue()[i] for i in range(self.pathPos.getValue().index(self.pathPos.getValue()[-1 * len(self.bestPath)]))]
                        tmp.append(self.initPos.getValue())

                        for val in pathPos.getValue():
                            tmp.append(val)

                        self.pathPos = ListPaths(tmp)
                        pathPos.getValue().insert(0,self.initPos.getValue())
                        self.initPos = Point(old_init[0], old_init[1])
                        
                        if(pathPos != None):
                            self.bestPath = self.convertPathPosToActions(pathPos.getValue())
                        else:
                            self.bestPath = list()
                        


            next_move = self.bestPath.pop(0)
            
        return next_move

    def collision_avoid(self,k):
        game_state = {self.name: self.pathPos.getValue()[k-1]}

        for key, item in self.locations.items():
            if k-1 > len(item):
                game_state[key] = item[-1]
            else:
                game_state[key] = item[k-1]
        actions = self.get_avai_actions(game_state)
        actions.remove(self.bestPath[0])
        
        min_euclid = 999999
        min_act = self.pathPos.getValue()[k-1]
        for action in actions:
            tmp = move(game_state[self.name],action)
            tmp_dist = euclideanDist(tmp,self.env.get_goals()[self.name])
            if tmp_dist < min_euclid:
                min_euclid = tmp_dist
                min_act = tmp
        return min_act
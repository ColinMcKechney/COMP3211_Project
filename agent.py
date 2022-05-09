import dis
from importlib.resources import path
from mimetypes import init
from sre_parse import State
import time
from typing import List
import numpy as np
from base import (BaseAgent, action_dict, move,
                  set_timeout, after_timeout, TIMEOUT)
from util import PriorityQueue,Point,ListPaths,convert_ListPath,convert_point,adapt_point,adapt_Listpath
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
    
    #Give the available actions but only regarded to the map not players
    def get_avai_actions_map(self,pos):
        avai_actions = []
        for action in action_dict:
            if action != 'nil':
                newPos = move(pos,action)
                if self.env.is_valid_pos(newPos):
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
            
            cur.close()
            con.close()
            if(pathPos != None):
                self.bestPath = self.convertPathPosToActions(pathPos.getValue())
            else:
                self.bestPath = list()
            self.firstIter = False

        if len(self.bestPath) <= 1 :
            self.firstIter = True
        
        next_move = 'nil'
        if len(self.bestPath) != 0:
            next_move = self.bestPath.pop(0)
        return next_move

      

    # @set_timeout(TIMEOUT, after_timeout)
    # def get_action(self, game_state):
    #     # Step 1. figure out what is accessible
    #     obs = self.observe(game_state)
    #     avai_actions = self.get_avai_actions_map(game_state)
    #     goal = self.env.get_goals()[self.name]

    #     # Step 2. production system or any rule-based system
    #     min_dist = 999999
    #     best_action = None
    #     for action in avai_actions:
    #         succ = move(obs[0], action)
    #         if succ in obs[1:]:
    #             continue
    #         else:
    #             dist = (goal[0] - succ[0]) ** 2 + (goal[1] - succ[1]) ** 2
    #             if dist <= min_dist:
    #                 min_dist = dist
    #                 best_action = action

    #     return best_action

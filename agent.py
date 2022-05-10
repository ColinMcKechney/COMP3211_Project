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
        self.other_initials = {}
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
                self.other_initials[name] = game_state[name]
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

        #potential for update database call to keep the locations correct
        '''mapName = self.env.env_name.capitalize()
        mapName = 'ShortestPath'+ mapName + '.db'
        
        sqlite3.register_converter("Point", convert_point)
        sqlite3.register_converter("ListPaths", convert_ListPath)
        sqlite3.register_adapter(Point, adapt_point)
        sqlite3.register_adapter(ListPaths,adapt_Listpath)
        
        con = sqlite3.connect(mapName,detect_types=sqlite3.PARSE_DECLTYPES)
        cur = con.cursor()

        for name in self.locations.keys():
            if name == self.name:
                continue
            cur.execute("SELECT path FROM paths WHERE agent = (?) and position = (?)",(name,Point(self.other_initials[name][0], self.other_initials[name][1])))
            cur.fetchone
            self.locations[name] = cur.fetchone()[0].getValue()

        cur.close()
        con.close()'''
        
        next_move = 'nil'
        if len(self.bestPath) != 0:

            for key, l in self.locations.items(): #loop through the other agents 
                test_point = self.pathPos.getValue()[-1 * len(self.bestPath)] #this is the point we're working with at the moment, the next spot the agent is going to go
                if test_point in l:  #if it's in the path of the other 
                    
                    # 
                    #this or is for swaps, will work on later 
                    test_index = self.pathPos.getValue().index(test_point) #index of point
                    if l.index(test_point) == test_index or (l.index(test_point) == len(l) - 1 and test_index >= len(l) -1) or (test_index < len(l)-1  and test_point == l[test_index -1] and self.pathPos.getValue()[test_index -1] == l[test_index]): #either they meet along the way or one has finished
                        #continue
                        new_act = self.collision_avoid(test_index ) #get the new action that you are going to do instead

                        #grabbing new path from new position
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

                        
                        #add back in the old values that you've already traveled, keeps indexes in line
                        tmp = [self.pathPos.getValue()[i] for i in range(test_index)]
                        tmp.append(self.initPos.getValue())

                        for val in pathPos.getValue():
                            tmp.append(val)

                        self.pathPos = ListPaths(tmp)
                        pathPos.getValue().insert(0,self.initPos.getValue())
                        self.initPos = Point(old_init[0], old_init[1]) #reset initPoint to keep path to actions working 
                        
                        if(pathPos != None):
                            self.bestPath = self.convertPathPosToActions(pathPos.getValue())
                        else:
                            self.bestPath = list()
                        
                        #potential broadcast point for database
                        '''updated_name = 'update_' + self.name
                        print('before')
                            #cur.execute("INSERT INTO paths (agent, position, path) VALUES((?), (?), (?))",(updated_name,self.initPos,self.pathPos))
                        cur.execute("SELECT * FROM paths WHERE agent = (?)",(updated_name))
                        print(cur.fetchall())
                        print('here')

                        #cur.execute("SELECT path FROM paths WHERE agent = (?) and position = (?)",(updated_name,self.initPos))
                        
                        cur.fetchone
                        pathPos = cur.fetchone()[0]
                        print(pathPos)
                        print(self.pathPos)

                        cur.close()
                        con.close()'''


                        
                        '''TODO: create a new entry in the database to broadcast changes'''
                        


            next_move = self.bestPath.pop(0)
            
        return next_move

    def collision_avoid(self,k):
        #collision avoidance alg
        game_state = {self.name: self.pathPos.getValue()[k-1]} #create a game state

        for key, item in self.locations.items():
            if k-1 > len(item):
                game_state[key] = item[-1]
            else:
                game_state[key] = item[k-1]
        actions = self.get_avai_actions(game_state, self.name)
        
        actions.remove(self.bestPath[0]) #remove the action causing the conflict
        actions.remove('nil') #can't do nothing to avoid deadlock
        
        #find the option that keeps the distance the best 
        min_euclid = 999999
        min_act = self.pathPos.getValue()[k-1]
        for action in actions:
            tmp = move(game_state[self.name],action)
            tmp_dist = euclideanDist(tmp,self.env.get_goals()[self.name])
            if tmp_dist < min_euclid:
                min_euclid = tmp_dist
                min_act = tmp
        return min_act
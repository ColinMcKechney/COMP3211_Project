from asyncio.windows_events import NULL
from base import (BaseAgent, action_dict, move,
                  set_timeout, after_timeout, TIMEOUT)

##################################################################################
# Here is a demo agent.                                                          #
# You can implement any helper functions.                                        #
# You must not remove the set_timeout restriction.                               #
# You can start your code any where but only the get_action() will be evaluated. #
##################################################################################


class MyAgent(BaseAgent):

    def __init__(self, name, env):
        super().__init__(name, env)
        self.locations = {}

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

    @set_timeout(TIMEOUT, after_timeout)
    def get_action(self, game_state):
        # Step 1. figure out what is accessible
        if self.locations == {}:
            self.locations = #get locations from the database
            other_loc = self.locations.values() - self.locations[self.name]
            for j in range(len(other_loc)): #go through the other locations of the agents 
                k=0
                #need a while loop to pause iteration
                while k in range(len(self.locations[self.name])): #check each step
                    if k > len(other_loc[j]): #if the other agent finishes first we don't have to check anymore
                        break

                    #if then end up in the same location or if the locations swap, both would be a collision
                    if self.locations[self.name][k] == other_loc[j][k] or (self.locations[self.name][k] == other_loc[j][k-1] and self.locations[self.name][k-1] == other_loc[j][k]):
                        #collision avoidance
                        new_loc = self.collision_avoid(k)
                        continue
                        #call algorithm to find shortest path to goal from new position             
                    k+=1

        '''your code to get the next location, I'm assuming you already wrote this'''
            

        return best_action
    
    def collision_avoid(self, k):
        #need: k, i, j, goals
        game_state = {}
        for key, item in self.locations.items():
            game_state[key] = item[k]

        actions = self.get_avai_actions(game_state)
        try:
            actions.remove(to_action(self.locations[self.name][k])) #to_action is a placeholder for your action function
        except(ValueError):
            pass
            
        if len(actions) > 0:
            return self.env.transition(actions[0])[self.name] 
        else:
            return NULL




    







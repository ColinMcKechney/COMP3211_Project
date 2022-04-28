from base import (BaseAgent, action_dict, move,
                  set_timeout, after_timeout, TIMEOUT)

##################################################################################
# Here is a demo agent.                                                          #
# You can implement any helper functions.                                        #
# You must not remove the set_timeout restriction.                               #
# You can start your code any where but only the get_action() will be evaluated. #
##################################################################################


class MyAgent(BaseAgent):

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
        obs = self.observe(game_state)
        avai_actions = self.get_avai_actions(game_state)
        goal = self.env.get_goals()[self.name]

        # Step 2. production system or any rule-based system
        min_dist = 999999
        best_action = None
        for action in avai_actions:
            succ = move(obs[0], action)
            if succ in obs[1:]:
                continue
            else:
                dist = (goal[0] - succ[0]) ** 2 + (goal[1] - succ[1]) ** 2
                if dist <= min_dist:
                    min_dist = dist
                    best_action = action

        # TODO: you may want to start here
        # Feel free erase all the demo code above

        return best_action

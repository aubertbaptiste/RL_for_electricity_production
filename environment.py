import gymnasium as gym
from gymnasium import spaces, Env
import numpy as np
def conso_match(conso,prod):
    return sum(prod) >= conso , sum(prod)-conso

def battery_availability(battery,prod): # Risque d'y avoir un problème car l'agent ne connait pas le niveau de battery
    prod_as_list = list(prod)
    if prod_as_list[2]>battery:
        print(f"La batterie n'a pas assez de puissance disponible : Demandé : {prod[2]}, Disponible : {battery}")
        prod_as_list[2]=battery
    return tuple(prod_as_list)

def update_battery(battery,gain):
    return battery + gain


class PowerGridEnv(Env):
    def __init__(self,scenario=np.array([(1,1)]),battery_max=1):
        """ Un scenario est un array de tuple, un tuple représente 
        (Consommation instantanée, Prévision de Consommation, Puissance solaire)
        Pendant 1h.
        Battery_max représente la capacité maximale disponible en stockage"""
        self.cons_max = scenario[:,[0]].max()
        self.puissance_solaire_max = scenario[:,1].max()
        self.scenario = scenario
        self.max_hour = len(scenario)
        self.battery_max = battery_max

        self.action_space = spaces.Tuple((
            spaces.Discrete(self.cons_max),
            spaces.Discrete(self.cons_max),
            spaces.Discrete(battery_max))
            )
        self.observation_space = spaces.Box(
            low=-1.0, 
            high=1.0, 
            shape=(4,), 
            dtype=np.float32)
        
        self._reset()
    def step(self,action):
        return self._step(action)
    def reset(self):
        return self._reset()


    def _step(self,action):
        assert self.action_space.contains(action)
        action_corrected = battery_availability(self.battery,action) # On check si on a assez de battery
        sufficient,gain = conso_match(self.scenario[self.hour][0],action)
        reward = -action_corrected[0]*0.5 # On pénalise la production au gaz
        print(reward,gain) # A SUPR 
        if sufficient:
            reward = reward
            self.battery = update_battery(self.battery,gain)
        else:
            reward = reward + gain*2  # On pénalise beaucoup le déficit
        self.hour += 1
        if self.hour >= self.max_hour:
            done = True
        else : 
            done = False

        return self._get_obs(),reward,done
    
    def _reset(self,seed=None):
        self.hour = self.np_random.integers(0,24)
        self.battery = self.np_random.uniform(0.1,0.9)*self.battery_max
        return self._get_obs()

    def _get_obs(self):
        current_index = self.hour % len(self.scenario)
        norm_cons = self.scenario[current_index][0]/self.cons_max
        norm_sol = self.scenario[current_index][1]/self.puissance_solaire_max
        norm_battery = self.battery/self.battery_max
        norm_hour = self.hour/24.0
        return norm_cons,norm_sol,norm_battery,norm_hour

            

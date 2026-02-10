import gymnasium as gym
from gymnasium import spaces, Env
import numpy as np
def conso_match(conso,solaire,Pbat,action_possible):
    if action_possible:
        gaz= max(0,conso-solaire-Pbat)
        penalty=0
    else:
        print("Puissance exigée non disponible")
        gaz= max(0,conso-solaire-Pbat)
        penalty = -gaz # On double la pénalité du gaz si on a chargé la battery alors qu'il ne fallait pas
    return gaz,penalty

def check_battery(self,action):
    if action == 0: # Charger à 100%
        if self.battery == 0:
            self.battery = self.battery_max
            Pbat = -self.battery_max
            penalty = 0
        else : 
            print("Battery supérieur au max") # Debug 
            penalty = -self.battery_max
            Pbat =0
        return True, Pbat,penalty
    if action == 1 : # Charger à 50%
        if self.battery + 0.5*self.battery_max > self.battery_max : 
            print("Battery supérieur au max") # Debug
            penalty = -0.5*self.battery_max
            Pbat=0
        else :
            self.battery += 0.5*self.battery_max
            Pbat = -0.5*self.battery_max
            penalty = 0
        return True, Pbat,penalty   
    if action == 2 : # On bouge pas
        Pbat = 0
        return True, Pbat,0
    if action == 3 : # On décharge de 50%
        if self.battery >= 0.5*self.battery_max:
            self.battery -= 0.5*self.battery_max
            Pbat= 0.5*self.battery_max
            return True,Pbat,0
        else : return False,0,0
    if action == 4 : 
        if self.battery == self.battery_max:
            self.battery = 0
            Pbat = self.battery_max
            return True,Pbat,0
        else : return False,0,0




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

        self.action_space = spaces.Discrete(5) # On a 5 actions : Charger à 100% 50% 0%, décharger à 50% ou 100%
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
        action_possible,Pbat,overcharge = check_battery(self,action) # On check si on a assez de battery et on l'update
        gaz,penalty = conso_match(self.scenario[self.hour][0],self.scenario[self.hour][1],Pbat,action_possible)
        reward = min(-gaz,0)+penalty+overcharge # On pénalise la production au gaz. Si on a un surplus solaire alors on pénalise pas
        self.hour += 1
        if self.hour >= self.max_hour:
            done = True
        else : 
            done = False

        return self._get_obs(),reward,done
    
    def _reset(self,seed=None):
        self.hour = self.np_random.integers(0,24)
        self.battery = self.np_random.choice([0,0.5,1])*self.battery_max
        return self._get_obs()

    def _get_obs(self):
        current_index = self.hour % len(self.scenario)
        norm_cons = self.scenario[current_index][0]/self.cons_max
        norm_sol = self.scenario[current_index][1]/self.puissance_solaire_max
        norm_battery = self.battery/self.battery_max
        norm_hour = self.hour/24.0
        return norm_cons,norm_sol,norm_battery,norm_hour

            

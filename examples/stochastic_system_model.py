from actualcauses import SCM, BaseNumpyModel, AverageNumpyModel, LUCBNumpyModel
import numpy as np

class RockThrowingModel(BaseNumpyModel):
    def simulate(self, u):
        self["ST"] = u[0]
        self["BT"] = u[1]
        self["SH"] = self["ST"]
        self["BH"] = self["BT"] & ~self["SH"]
        self["BS"] = self["BH"] | self["SH"]

class AvgRockThrowingModel(AverageNumpyModel):
    def simulate(self, u): 
        return RockThrowingModel.simulate(self, u)
        
class LUCBRockThrowingModel(LUCBNumpyModel):
    def simulate(self, u): 
        return RockThrowingModel.simulate(self, u)
        
suzzy_vars = ("ST", "BT", "SH", "BH", "BS")

t = .05 # 5% chance of “flipping” a value
N = 20 # Evaluate on average 15 times each intervention to estimate phi and psi
eps = .2 # An intervention “cancels” the consequence if we estimate phi(e)<20%
beam_size = 10
lucb_params = {"a": eps, 
               "cause_eps": .1, 
               "non_cause_eps": .1, 
               "beam_eps": .1, 
               "max_iter": N, 
               "verbose": 0, 
               "init_batch_size": 15,
               "batch_size": 2,
               "delta": .05,
               "beam_size": beam_size
               }

noisy_suzzy_avg = SCM(
    V=suzzy_vars,
    U=("st", "bt"),
    D=(0,1),
    u=(1,1),
    dag=None,
    model=AvgRockThrowingModel(suzzy_vars, t, N)
    )

noisy_suzzy_lucb = SCM(
    V=suzzy_vars,
    U=("st", "bt"),
    D=(0,1),
    u=(1,1),
    dag=None,
    model=LUCBRockThrowingModel(suzzy_vars, t, lucb_params)
    )

if __name__ == "__main__":
    print("======= Identifying causes with average estimator =======")
    np.random.seed(0)
    noisy_suzzy_avg.find_causes(epsilon=eps, verbose=1, beam_size=beam_size)
    print()
    noisy_suzzy_avg.show_identification_result()
    print()
    print("-"*20)
    print()
    print("======= Identifying causes with LUCB estimator =======")
    np.random.seed(0)
    noisy_suzzy_lucb.find_causes(epsilon=eps, verbose=1, beam_size=beam_size)
    print()
    noisy_suzzy_lucb.show_identification_result()
    

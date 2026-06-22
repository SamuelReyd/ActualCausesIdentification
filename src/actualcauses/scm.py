from collections.abc import Iterable
import json
import time

import numpy as np
from .mbs import beam_search, show_rules
from .isi import iterative_identification
from .system_model import SystemModel, SuzzyExampleSystemModel
from typing import Any

class SCM:
    def __init__(self, V:list[str], U:list[str], D:list[list], u:list,
                 model:SystemModel, dag:list[list]=None, v:list=None, target:int=-1):
        """
        SCM object that includes everything needed to execute the algorithms
            V: list of endogenous variables labels (the target must be the last variable)
            U: list of exogenous variables labels
            D: list of discrete domains for the variables in V (in the same order)
            u: context (values of U in the right order)
            model: a SystemModel object that must implement __call__ and evaluate_batch 
            dag (optional): a list of lists where each element i is the set of causal parents of V[i].
            v (optional): a list of values for v. If none is provided, then F(u,[]) is used. 
                Providing v can be useful for stochastic experiments.
            target (int): the index of the target variable in V.
        """
        # Mandatory parameters
        self.V = V
        self.U = U
        self.model = model
        if isinstance(D[0], Iterable):
            self.D = D
        else:
            self.D = [D] * len(V)
        self.u = u
        if v is None:
            self.v = self({})
        else:
            self.v = v
            
        # Interventions and evaluation functions
        self.dag = dag
        self.target = target
        self.init_vars = dag[V[self.target]] if dag is not None else None
        
        self.causes = None
        self.causes_hashable = None
        self.witnesses = None
        self.identification_output = None
        self.interventions = None
        self.identification_time = None
        self.n_calls = None
    
    def __call__(self, e:list[tuple[str,Any]]) -> list[Any]:
        return self.model(self.u, e)
        
    def evaluate_batch(self, E: list[list[tuple[str,Any]]], N:int=1) -> list[tuple[float,float]]:
        return self.model.evaluate_batch(self.u, E, N)

    def get_input(self, base=True):
        if base:
            return self.get_input_beam_search()
        assert self.dag is not None
        return self.get_input_beam_search() | {"dag": self.dag, "PA_T":self.init_vars}

    def get_input_beam_search(self):
        return {"v": self.v[:-1], "V": self.V[:-1], "D": self.D[:-1], "simulation": self.evaluate_batch}

    def find_causes(self, ISI=False, save_path=None, **kwargs):
        t = time.time()
        self.model.n_calls = 0
        if ISI:
            out = iterative_identification(**self.get_input(False), **kwargs)
        else:
            out = beam_search(**self.get_input(), **kwargs)
        self.identification_time = time.time() - t
        if out:
            self.interventions, self.phi_values, self.psi_values, self.causes, self.witnesses = zip(*out)
        else:
            self.interventions, self.phi_values, self.psi_values, self.causes, self.witnesses = [], [], [], {}, {}
        self.causes_hashable = [tuple(sorted(elt)) for elt in self.causes]
        self.witnesses_hashable = [tuple(sorted(elt)) for elt in self.witnesses]
        self.n_calls = self.model.n_calls
        self.identification_params = kwargs
        if hasattr(self.model, "lucb_params"):
            self.identification_params["lucb_params"] = self.model.lucb_params
        if save_path is not None:
            self.save(save_path)
        
    def show_identification_result(self):
        print(f"Found {len(self.causes)} causes in {self.identification_time:.3f}s with {self.n_calls} model calls\n")
        show_rules(self.identification_output)

    def save(self, path):
        save_keys = ("V", "U", "D", "target", "init_vars", 
                     "causes_hashable", "witnesses_hashable", "phi_values", "psi_values", 
                     "identification_time", "interventions",
                     "n_calls", "identification_params")
        save_dict = {key: self.__dict__[key] for key in save_keys}
        for key in ("u", "v"):
            value = self.__dict__[key]
            if type(value) == np.ndarray:
                save_dict[key] = value.tolist()
            else:
                save_dict[key] = list(value)
        if self.dag is not None:
            save_dict["dag"] = {key: list(value) for key, value in self.dag.items()}
        with open(path, "w") as file:
            file.write(json.dumps(save_dict, indent=2))

    @classmethod
    def load(cls, path, model=None):
        # if model is None:
        #     print("Warning: no model provided, the resulting SCM won't be able to evaluate interventions")
        with open(path) as file:
            load_dict = json.load(file)
        if "dag" in load_dict:
            load_dict["dag"] = {key:set(value) for key, value in load_dict["dag"].items()}
        else:
            load_dict["dag"] = None
        init_keys = ("V", "U", "D", "u", "dag", "v", "target")
        scm = cls(model=model, **{key:load_dict[key] for key in init_keys})

        update_keys = ("causes_hashable", "witnesses_hashable", "interventions", 
                       "phi_values", "psi_values", "identification_time", "n_calls", 
                       "identification_params")
        scm.__dict__ |= {key: load_dict[key] for key in update_keys}
        scm.causes = [set(C) for C in scm.causes_hashable] 
        scm.witnesses = [set(W) for W in scm.witnesses_hashable] 
        return scm

suzzy_example_scm = SCM(
    V=("ST", "BT", "SH", "BH", "BS"),
    U=("st", "bs"),
    D=(0,1),
    u=(1,1),
    model=SuzzyExampleSystemModel(),
    dag={"ST":[], "BT":[], "SH":["ST"], "BH":["BT","SH"], "BS":["BH","SH"]}
)
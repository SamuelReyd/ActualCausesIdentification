from actualcauses import SCM, SystemModel, SuzzyExampleSystemModel, suzzy_example_scm

class SuzzyCustomPsi(SuzzyExampleSystemModel):
    # A model for the rock throwing example, with variables ST, BT, SH, BH, BS
    def __init__(self, psi):
        super().__init__()
        self.psi = psi

v = suzzy_example_scm.v

heuristics = {
    "sum of negative variables": lambda s: sum(s),
    "sum of positive variables": lambda s: len(s) - sum(s),
    "sum of counteractual variables": lambda s: sum([s_val != v_val for s_val, v_val in zip(s, v)]),
    "sum of actual variables": lambda s: sum([s_val == v_val for s_val, v_val in zip(s, v)]),
}

def run():
    print("Finding causes with various heuristics")
    for desc, psi in heuristics.items():
        system_model = SuzzyCustomPsi(psi)
        scm = SCM(
            V=("ST", "BT", "SH", "BH", "BS"),
            U=("st", "bs"),
            D=(0,1),
            u=(1,1),
            model=system_model,
            dag={"ST":[], "BT":[], "SH":["ST"], "BH":["BT","SH"], "BS":["BH","SH"]}
        )
        scm.find_causes()

        print(f" -> Using heuristic {desc}:")
        scm.show_identification_result()
        print("-"*20)

if __name__ == "__main__":
    run()
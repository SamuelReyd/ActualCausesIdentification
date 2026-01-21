from actualcauses import SCM, SystemModel

class ForestFireExampleSystemModel(SystemModel):
    # A model for the forest fire scenario
    def __init__(self, disjuctive=True):
        super().__init__(
            phi=lambda s: s[-1], 
            psi=lambda s: sum(s)
        )
        self.disjunctive = disjuctive

    def __call__(self, u:list, e: list[tuple]) -> list:
        # Variables are Match Drops (MD), Lighning (L) and Forest Fire (FF)
        md, l = u
        e = dict(e)
        MD = e.get("MD", md)
        L = e.get("L", l)
        if self.disjunctive:
            FF = e.get("FF", int(L or MD))
        else:
            FF = e.get("FF", int(L and MD))
        self.n_calls += 1
        return [MD, L, FF]

dis_ff_example = SCM(
    V=("MD", "L", "FF"),
    U=("md", "l"),
    D=(0,1),
    u=(1,1),
    model=ForestFireExampleSystemModel(disjuctive=True),
    dag={"MD":[], "L":[], "FF":["MD", "L"]}
)

conj_ff_example = SCM(
    V=("MD", "L", "FF"),
    U=("md", "l"),
    D=(0,1),
    u=(1,1),
    model=ForestFireExampleSystemModel(disjuctive=False),
    dag={"MD":[], "L":[], "FF":["MD", "L"]}
)

def run():
    print("Disjunctive Forest Fire Scenario: ")
    print(f"             MD <- 0: {dis_ff_example({"MD":0})=}")
    print(f"              L <- 0: {dis_ff_example({"L":0})=}")
    print(f"  MD <- 0 and L <- 0: {dis_ff_example({"L":0,"MD":0})=}")
    print()

    
    print("Conjunctive Forest Fire Scenario: ")
    print(f"             MD <- 0: {conj_ff_example({"MD":0})=}")
    print(f"              L <- 0: {conj_ff_example({"L":0})=}")
    print(f"  MD <- 0 and L <- 0: {conj_ff_example({"L":0,"MD":0})=}")
    print()
    dis_ff_example.find_causes()
    conj_ff_example.find_causes()
    print("-"*20)

    print("Causes for disjunctive case")
    dis_ff_example.show_identification_result()
    print("-"*20)
    print("Causes for conjunctive case")
    conj_ff_example.show_identification_result()
    

if __name__ == "__main__":
    run()
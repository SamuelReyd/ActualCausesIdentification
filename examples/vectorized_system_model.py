from actualcauses import BaseNumpyModel, SCM

class LampModel(BaseNumpyModel):
    def simulate(self, u):
        self["A"] = u[0]
        self["B"] = u[1]
        self["C"] = u[2]
        self["L"] = (self["A"] == self["B"]) | (self["A"] == self["C"]) | (self["C"] == self["B"])

scm_lamp = SCM(V=["A","B", "C", "L"], U=["a","b", "c"], D=[(-1,0,1)]*3+[(0,1)], 
                model=LampModel(V=["A","B", "C", "L"], dtype=int), 
                u=(1,-1,-1), 
                dag={"A":[], "B": [], "C":[], "L":["A", "B", "C"]})

test_interventions = [((var,value),) for var, domain in zip(scm_lamp.V, scm_lamp.D) for value in domain]

def run():
    print(f"Lamp SCM: V={scm_lamp.V} / v={scm_lamp.v}")
    print()
    print(f"Simulate several interventions:")
    res = scm_lamp.evaluate_batch(test_interventions)
    for intervention, (phi, psi) in zip(test_interventions, res):
        print(f"  {intervention[0][0]}<-{intervention[0][1]} ==> {phi=:.0f}, {psi=:.0f}")
    scm_lamp.find_causes(beam_size=-1)
    print()
    scm_lamp.show_identification_result()

if __name__ == "__main__":
    run()
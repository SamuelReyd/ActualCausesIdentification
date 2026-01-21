from actualcauses import suzzy_example_scm

def run():
    print("Suzzy SCM:")
    print(f"  Exogenous variables: {suzzy_example_scm.U=}")
    print(f"  Endogenous variables: {suzzy_example_scm.V=}")
    print(f"  Domains: {suzzy_example_scm.D=}")
    print(f"  Context: {suzzy_example_scm.u=}")
    print(f"  Actual state: {suzzy_example_scm.v=}")
    print(f"  Causal graph: {suzzy_example_scm.dag=}")
    
    print("\n======= Identifying causes with MBS =======")
    suzzy_example_scm.find_causes(ISI=False, max_steps=5, beam_size=20, epsilon=.05, early_stop=False, verbose=2)
    print()
    suzzy_example_scm.show_identification_result()
    print("\n======= Identifying causes with ISI =======")
    suzzy_example_scm.find_causes(ISI=True, max_steps=5, beam_size=20, epsilon=.05, early_stop=False, verbose=2)
    print()
    suzzy_example_scm.show_identification_result()

if __name__ == "__main__":
    run()
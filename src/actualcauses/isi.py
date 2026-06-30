from itertools import combinations, islice, count
from collections.abc import Iterable, Iterator

from .mbs import beam_search, remove_duplicates, minimal_merge

import numpy as np
from tqdm import tqdm


def merge_set_lists(list1:list[set], list2:list[set])->list[set]:
    # Convert each set in the lists to a frozenset and add to a set to remove duplicates
    unique_frozensets = set()
    for s in list1:
        unique_frozensets.add(frozenset(s))
    for s in list2:
        unique_frozensets.add(frozenset(s))
    # Convert the frozensets back to sets
    return [set(fs) for fs in unique_frozensets]

def make_beam_search(v:list[object], D:list[list], V:list[str], K:tuple, minimality:bool, 
                     **kargs) -> tuple:
    # Use K to update D (using W_0) and build new V=W_0 U I
    I, W_0, R_C, r_C, R_W = K
    I = I|W_0
    R = tuple(r_C.items())
    R += tuple([(var, value) for var, value in zip(V,v) if var in R_W])
    D = [D[i] if var not in W_0 else [value] for i, (var, value) in enumerate(zip(V,v))]
    
    if minimality:
        E = beam_search(v=v, D=D, V=V, I=I, R=R, **kargs)
        full_E = None
    else:
        E, full_E = beam_search(v=v, D=D, V=V, I=I, R=R, minimality=False, **kargs)
        full_E = remove_duplicates(full_E)
    return E, full_E

def subsets(s:Iterable, n:int=None) -> Iterator[tuple]:
    s = list(s)
    if n is None:
        n = len(s)
    n = min(n + 1, len(s) + 1)
    for size in range(1, n):
        for subset in combinations(s, size):
            yield set(subset)

def CH_set(S: set[str], CH: dict[str, set[str]]) -> set[str]:
    chs = [CH[var] for var in S]
    return set.union(*chs) if chs else set()
 
 
def PA_set(S: set[str], PA: dict[str, set[str]]) -> set[str]:
    pas = [set(PA[var]) for var in S]
    return set.union(*pas) if pas else set()
 
 
def desc(S: set[str], CH: dict[str, set[str]]) -> set[str]:
    ch = CH_set(S, CH)
    des: set[str] = set()
    while ch:
        des |= ch
        ch = CH_set(ch, CH)
    return des
 
 
def anc(S: set[str], PA: dict[str, set[str]]) -> set[str]:
    pa = PA_set(S, PA)
    an: set[str] = set()
    while pa:
        an |= pa
        pa = PA_set(pa, PA)
    return an

def expand(C:set, e:dict, W:set, S:set, PA:dict[str:set[str]], CH:dict[str:set[str]]) -> tuple[set, set, set, dict,set]:
    I = PA_set(S, PA) - C
    W_0 = (desc(I, CH) - I) & (anc(C, PA) - C)
    R_C = C - S
    r_C = {var:e[var] for var in R_C}
    R_W = W | (desc(I, CH) - I - (desc(C, CH) | C | anc(C, PA)))
    return I, W_0, R_C, r_C, R_W

def covers(K_ref: tuple, K: tuple) -> bool:
    """True iff the constrained search space of K is contained in K_ref's.
 
    In other words: running the beam search under K_ref already covers
    everything that running it under K would explore, so K can be skipped.
    """
    I_r, W0_r, RC_r, rC_r, RW_r = K_ref
    I,   W_0,  R_C,  r_C,  R_W  = K
    return (
        set(rC_r.items()) <= set(r_C.items())   # fewer fixed cause vars, same values
        and R_C | I       <= RC_r | I_r         # cause pool contained
        and RW_r          <= R_W               # fewer forced witness vars
        and R_W | W_0 | I <= RW_r | W0_r | I_r # witness pool contained
    )

def sample_subsets(subs: list, n_sample: int) -> list:
    """Randomly sub-sample *n_sample* elements from *subs* without replacement."""
    n = len(subs)
    if n <= n_sample:
        return subs
    ids = np.random.choice(range(n), n_sample, replace=False)
    return [subs[i] for i in ids]

def iterative_identification(
        v, D, simulation, V, dag, PA_T, 
        cache_size: int=-1,
        sample_backtrack: int = -1,
        max_backtrack: int = -1,
        **kargs
        ):
    """Iterative Subinstance Identification (ISI).
 
    Parameters
    ----------
    v, D, simulation, V, dag, PA_T
        Standard SCM / search inputs (forwarded from SCM.find_causes).
    cache_size : int
        Maximum number of cached beam-search results. -1 = unlimited.
    sample_backtrack : int
        If > 0, keep only this many randomly sampled constraints at each
        backtracking level (approximation mode). -1 = keep all.
    max_backtrack : int
        Maximum number of backtracking levels. -1 = unlimited.
    **kargs
        Forwarded verbatim to make_beam_search / beam_search.
    """
    PA = dag
    CH = {
        var: {child for child, parents in PA.items() if var in parents}
        for var in dag.keys()
    }
    minimality = max(map(len, D)) <= 2
    verbose    = kargs.get("verbose", 0)
    early_stop = kargs.get("early_stop", False)
    kargs["simulation"] = simulation

    K_0 = (set(PA_T), set(), set(), dict(), set())

    cache  = dict() if cache_size >= 0 else None
    memory: list[tuple] = []
    ret:   list         = []
    Cs:    list[set]    = []

    Ks      = [K_0]

    if max_backtrack == -1 or max_backtrack is None:
        iterator = count(start=1, step=1)
    else:
        iterator = range(1, max_backtrack + 1)

    for _ in tqdm(iterator, disable=(verbose != 1), desc="Backtracking steps"):
        if not Ks:
            break
        next_Ks: list[tuple] = []

        for K in tqdm(Ks, disable=(verbose != 1), desc="Constraints"):
            # ---- maintain cache size ----
            if cache is not None:
                if len(cache) > cache_size:
                    cache = dict(islice(cache.items(), cache_size))
 
            if verbose > 1:
                if any(map(lambda k: len(k) > 15, K)):
                    print("Large K")
                else:
                    print(f"{K=}")

            # ---- beam search under this constraint ----
            E, full_E = make_beam_search(
                v, D, V, K, minimality, cache=cache, Cs=Cs, **kargs
            )

            Cs = merge_set_lists([e[3] for e in E], Cs)
            if early_stop and E:
                return E
            ret = minimal_merge(E, ret)

            # ---- generate child constraints ----
            E_expand = E if minimality else full_E
            for e in E_expand:
                C, W = e[3], e[4]
                for S in subsets(C):
                    K_new = expand(C, dict(e[0]), W, S, PA, CH)
                    if not K_new[0]:
                        continue  # no free intervention variables
                    # Skip if already covered by a previously visited constraint
                    add = not any(covers(K_ref, K_new) for K_ref in memory)
                    if verbose > 1:
                        print(f"  ({'V' if add else 'X'}) {C=} -> {S=} -> {K_new=}")
                    if add:
                        # Prune next_Ks entries already dominated by K_new
                        next_Ks = [K_q for K_q in next_Ks if not covers(K_new, K_q)]
                        next_Ks.append(K_new)
                        memory.append(K_new)
                    if verbose > 1:
                        print(f"  (V) {C=} -> {S=} -> {K_new=}")

        # ---- optional approximation: sub-sample next level ----
        if sample_backtrack > 0:
            if verbose > 1:
                print(f"  Keeping {sample_backtrack} out of {len(next_Ks)} constraints…")
            Ks = sample_subsets(next_Ks, sample_backtrack)
        else:
            Ks = next_Ks
 
        if not Ks:
            break
    return ret

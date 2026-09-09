# data/prospective_validation

Reserved for future wet-lab results of the local validation design around the frozen
decision point (N-, OPT, N+, C-, C+; pre-MDI blend and prepolymer; 80/90/100/110/120 C;
Ea; %NCO).

`agent_access = false` (see `access_policy.json`). Nothing in this directory may be read by
the primary blind Agent benchmark. The runtime guard in `pur_agent.data_access` refuses any
path under this directory. A separate, secondary post-experiment Agent task may be defined
later with its own bundle builder; it must not reuse the primary benchmark ID.

The experiment validates whether the frozen computational decision transfers to reality.
The blind Agent benchmark validates whether the frozen decision is reproducible from the
admissible data. These are two independent lines and are never merged.

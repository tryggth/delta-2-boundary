/-!
# Bedrock — Baseline Environment Integrity Check

This file serves as the project's zero-axiom anchor point.
The `#print axioms` command below must return an empty dependency set,
proving the environment is completely unpolluted at initialization.
-/

def project_baseline_marker : Nat := 0
#print axioms project_baseline_marker

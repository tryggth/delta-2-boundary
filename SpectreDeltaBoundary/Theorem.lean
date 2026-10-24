/-
Copyright (c) 2026 Tryggth. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Tryggth
-/
import SpectreDeltaBoundary.Bedrock
import SpectreDeltaBoundary.Paths
import SpectreDeltaBoundary.Monotile
import SpectreDeltaBoundary.Certificate
import SpectreDeltaBoundary.CertificateData

/-!
# Main Tiling Uniqueness Theorem (3-Anchor-Lock Priority Proof)

Ties the 71-step computational peeling certificate directly to the
computable 3-anchor-lock (`L2 > L1 > L4`) state machine validator to prove
complete, non-vacuous boundary reduction of the $\Delta_2$ metatile patch.
-/

set_option linter.style.setOption false
set_option maxRecDepth 200000
set_option maxHeartbeats 2000000

/-- Verifies that the $\Delta_2$ certificate contains all 71 monotiles and uses
    exclusively the 3 anchor locks (`300049` = Lock #2, `300033` = Lock #1, `400110` = Lock #4). -/
theorem delta2_three_anchor_lock_invariants :
    pythonPeelingCertificate.steps.length = 71 ∧
    (pythonPeelingCertificate.steps.all (fun s =>
      s.lockId == 300049 || s.lockId == 300033 || s.lockId == 400110)) = true := by
  decide

/-- Theorem establishing that the 71-step 3-Anchor-Lock (`L2 > L1 > L4`) priority
    peeling certificate successfully and uniquely reduces the complete initial
    $\Delta_2$ metatile patch boundary to `some []` (zero remaining boundary edges)
    with zero structural validation anomalies. -/
theorem verify_delta2_uniqueness :
  executeCertificate initialMetatileBoundary pythonPeelingCertificate = some [] := by
  decide

#print axioms delta2_three_anchor_lock_invariants
#print axioms verify_delta2_uniqueness

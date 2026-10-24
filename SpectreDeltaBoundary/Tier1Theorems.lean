/-
Copyright (c) 2026 tryggth. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: tryggth
-/
import SpectreDeltaBoundary.Bedrock
import SpectreDeltaBoundary.Paths
import SpectreDeltaBoundary.Monotile
import SpectreDeltaBoundary.Certificate
import SpectreDeltaBoundary.Tier1Certificates

/-!
# Formal Uniqueness Verification for Tier 1 Metatiles
-/

set_option linter.style.header false
set_option maxRecDepth 200000

/-- Decidability proof validating that Tier-1 Gamma uniquely reduces to `some []` -/
theorem verify_tier1_gamma_uniqueness :
  executeCertificate initialMetatileBoundary_Gamma certificate_Gamma = some [] := by
  decide

/-- Decidability proof validating that Tier-1 Delta uniquely reduces to `some []` -/
theorem verify_tier1_delta_uniqueness :
  executeCertificate initialMetatileBoundary_Delta certificate_Delta = some [] := by
  decide

/-- Decidability proof validating that Tier-1 Theta uniquely reduces to `some []` -/
theorem verify_tier1_theta_uniqueness :
  executeCertificate initialMetatileBoundary_Theta certificate_Theta = some [] := by
  decide

/-- Decidability proof validating that Tier-1 Lambda uniquely reduces to `some []` -/
theorem verify_tier1_lambda_uniqueness :
  executeCertificate initialMetatileBoundary_Lambda certificate_Lambda = some [] := by
  decide

/-- Decidability proof validating that Tier-1 Xi uniquely reduces to `some []` -/
theorem verify_tier1_xi_uniqueness :
  executeCertificate initialMetatileBoundary_Xi certificate_Xi = some [] := by
  decide

/-- Decidability proof validating that Tier-1 Pi uniquely reduces to `some []` -/
theorem verify_tier1_pi_uniqueness :
  executeCertificate initialMetatileBoundary_Pi certificate_Pi = some [] := by
  decide

/-- Decidability proof validating that Tier-1 Sigma uniquely reduces to `some []` -/
theorem verify_tier1_sigma_uniqueness :
  executeCertificate initialMetatileBoundary_Sigma certificate_Sigma = some [] := by
  decide

/-- Decidability proof validating that Tier-1 Phi uniquely reduces to `some []` -/
theorem verify_tier1_phi_uniqueness :
  executeCertificate initialMetatileBoundary_Phi certificate_Phi = some [] := by
  decide

/-- Decidability proof validating that Tier-1 Psi uniquely reduces to `some []` -/
theorem verify_tier1_psi_uniqueness :
  executeCertificate initialMetatileBoundary_Psi certificate_Psi = some [] := by
  decide

/-- Helper predicate verifying that every step in a certificate uses strictly one of the 3 anchor locks. -/
def usesOnlyThreeAnchorLocks (cert : PeelingCertificate) : Bool :=
  cert.steps.all (fun s => s.lockId == 300049 || s.lockId == 300033 || s.lockId == 400110)

/-- Theorem confirming all 9 Tier-1 supertile certificates use exclusively the 3 anchor locks (`L2`, `L1`, `L4`). -/
theorem tier1_three_anchor_lock_invariants :
    usesOnlyThreeAnchorLocks certificate_Gamma = true ∧
    usesOnlyThreeAnchorLocks certificate_Delta = true ∧
    usesOnlyThreeAnchorLocks certificate_Theta = true ∧
    usesOnlyThreeAnchorLocks certificate_Lambda = true ∧
    usesOnlyThreeAnchorLocks certificate_Xi = true ∧
    usesOnlyThreeAnchorLocks certificate_Pi = true ∧
    usesOnlyThreeAnchorLocks certificate_Sigma = true ∧
    usesOnlyThreeAnchorLocks certificate_Phi = true ∧
    usesOnlyThreeAnchorLocks certificate_Psi = true := by
  decide

#print axioms tier1_three_anchor_lock_invariants
#print axioms verify_tier1_gamma_uniqueness
#print axioms verify_tier1_delta_uniqueness
#print axioms verify_tier1_psi_uniqueness


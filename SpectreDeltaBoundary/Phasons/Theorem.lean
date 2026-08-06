import SpectreDeltaBoundary.Bedrock
import SpectreDeltaBoundary.Paths
import SpectreDeltaBoundary.Monotile
import SpectreDeltaBoundary.Certificate
import SpectreDeltaBoundary.CertificateData
import SpectreDeltaBoundary.Theorem
import SpectreDeltaBoundary.Phasons.Basic
import SpectreDeltaBoundary.Phasons.Rigidity

theorem all_states_phason_free : ∀ (t1 : List PlacedTile) (t2 : List PlacedTile) (state : PeelingState),
    IsValidTiling t1 state → IsValidTiling t2 state → t1 = t2
| [], [], state, h1, h2 => rfl
| [], b::bs, state, h1, h2 => by
  have hs : state = [] := h1
  subst hs
  have : [] ≠ [] := h2.1
  contradiction
| a::as, [], state, h1, h2 => by
  have hs : state = [] := h2
  subst hs
  have : [] ≠ [] := h1.1
  contradiction
| a::as, b::bs, state, h1, h2 => by
  obtain ⟨s, hs⟩ := h1.2.2.1
  have ha := (h1.2.2.2 s hs).1
  have hb := (h2.2.2.2 s hs).1
  subst ha; subst hb
  have h_as := (h1.2.2.2 s hs).2
  have h_bs := (h2.2.2.2 s hs).2
  have h_tail := all_states_phason_free as bs s.nextState h_as h_bs
  rw [h_tail]

theorem execute_certificate_preserves_phason_free
    (cert : PeelingCertificate) (state : PeelingState)
    (h_exec : executeCertificate state cert = []) :
    IsPhasonFree state := by
  intro t1 t2 h1 h2
  exact all_states_phason_free t1 t2 state h1 h2

theorem delta2_patch_phason_free :
    IsPhasonFree initialMetatileBoundary := by
  apply execute_certificate_preserves_phason_free pythonPeelingCertificate
  exact verify_delta2_uniqueness

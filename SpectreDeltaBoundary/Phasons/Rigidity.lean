import SpectreDeltaBoundary.Bedrock
import SpectreDeltaBoundary.Paths
import SpectreDeltaBoundary.Monotile
import SpectreDeltaBoundary.Locks
import SpectreDeltaBoundary.Certificate
import SpectreDeltaBoundary.Phasons.Basic

theorem lock_forces_unique_tile
    (state : PeelingState) (step : PeelingStep)
    (h_exec : executePeelingStep state step = step.nextState)
    (h_non_empty : step.nextState ≠ []) :
    ∀ a as, IsValidTiling (a :: as) state → a = step.tile := by
  intro a as h_val
  exact (h_val.2.2.2 step h_exec).1

theorem lock_bearing_boundary_no_minimal_phason
    (state : PeelingState) (step : PeelingStep)
    (h_exec : executePeelingStep state step = step.nextState)
    (h_non_empty : step.nextState ≠ []) :
    ∀ t1 t2, ¬ IsMinimalPhasonState state t1 t2 := by
  intro t1 t2 ⟨h1, h2, hneq, hdisj⟩
  cases t1 with
  | nil =>
    have hs : state = [] := h1
    subst hs
    cases t2 with
    | nil => contradiction
    | cons b bs => exfalso; exact h2.1 rfl
  | cons a as =>
    have h_in_t1 : a ∈ (a :: as) := by simp
    have h_forced : a = step.tile :=
      lock_forces_unique_tile state step h_exec h_non_empty a as h1
    have h_not_t2 : a ∉ t2 := hdisj a h_in_t1
    subst h_forced
    cases t2 with
    | nil =>
      have hs2 : state = [] := h2
      subst hs2
      exfalso; exact h1.1 rfl
    | cons b bs =>
      have h_in_t2 : b ∈ (b :: bs) := by simp
      have h_forced2 : b = step.tile :=
        lock_forces_unique_tile state step h_exec h_non_empty b bs h2
      subst h_forced2
      exact h_not_t2 h_in_t2

theorem peeling_step_preserves_phason_free
    (state : PeelingState) (step : PeelingStep)
    (h_exec : executePeelingStep state step = step.nextState)
    (h_next_rigid : IsPhasonFree step.nextState) :
    IsPhasonFree state := by
  intro t1 t2 h1 h2
  cases t1 with
  | nil =>
    cases t2 with
    | nil => rfl
    | cons b bs =>
      have hs : state = [] := h1
      subst hs
      exfalso; exact h2.1 rfl
  | cons a as =>
    cases t2 with
    | nil =>
      have hs : state = [] := h2
      subst hs
      exfalso; exact h1.1 rfl
    | cons b bs =>
      have ha : a = step.tile := (h1.2.2.2 step h_exec).1
      have hb : b = step.tile := (h2.2.2.2 step h_exec).1
      subst ha; subst hb
      have h_as_valid : IsValidTiling as step.nextState := (h1.2.2.2 step h_exec).2
      have h_bs_valid : IsValidTiling bs step.nextState := (h2.2.2.2 step h_exec).2
      have h_tail_eq : as = bs := h_next_rigid as bs h_as_valid h_bs_valid
      rw [h_tail_eq]

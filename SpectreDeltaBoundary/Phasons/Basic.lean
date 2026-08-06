import SpectreDeltaBoundary.Bedrock
import SpectreDeltaBoundary.Paths
import SpectreDeltaBoundary.Monotile
import SpectreDeltaBoundary.Certificate

def IsValidTiling (tiles : List PlacedTile) (state : PeelingState) : Prop :=
  match tiles with
  | [] => state = []
  | a::as =>
      state ≠ [] ∧
      (stateToAllEdges state).length = (a::as).length * 14 ∧
      (∃ step, executePeelingStep state step = step.nextState) ∧
      (∀ step, executePeelingStep state step = step.nextState →
               a = step.tile ∧ IsValidTiling as step.nextState)

def IsPhasonFree (state : PeelingState) : Prop :=
  ∀ (t1 t2 : List PlacedTile), IsValidTiling t1 state → IsValidTiling t2 state → t1 = t2

def IsMinimalPhasonState (state : PeelingState) (t1 t2 : List PlacedTile) : Prop :=
  IsValidTiling t1 state ∧ IsValidTiling t2 state ∧ t1 ≠ t2 ∧
  (∀ tile, tile ∈ t1 → tile ∉ t2)

lemma no_empty_tiling_for_nonempty_state {α : Type} {a : α} {as : List α}
    (h : 0 = (a :: as).length * 14) : False := by
  have hlen : (a :: as).length > 0 := by simp
  have h14 : (a :: as).length * 14 > 0 := by omega
  omega

theorem empty_state_phason_free : IsPhasonFree [] := by
  intro t1 t2 h1 h2
  cases t1 with
  | nil =>
    cases t2 with
    | nil => rfl
    | cons b bs => exfalso; exact h2.1 rfl
  | cons a as =>
    exfalso; exact h1.1 rfl

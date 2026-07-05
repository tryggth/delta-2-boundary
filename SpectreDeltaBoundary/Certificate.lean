import SpectreDeltaBoundary.Bedrock
import SpectreDeltaBoundary.Paths
import SpectreDeltaBoundary.Monotile

/-- Represents a single atomic step in our verified peeling certificate.
    Identifies which unprovable search was resolved by a short-path lock,
    and details the rigid tile coordinate forced into existence. -/
structure PeelingStep where
  lockId : Nat       -- Matches the specific verified short-path lock lemma
  tile : PlacedTile  -- The unique tile location and orientation forced by the lock
deriving DecidableEq, Repr

/-- The certificate object containing the complete ordered sequence of tile removals. -/
structure PeelingCertificate where
  steps : List PeelingStep
deriving DecidableEq, Repr

/-- Tracks the remaining active open boundaries during the peeling sequence.
    Represented as a list of vertex sequences to naturally accommodate cases
    where removing a tile pinches or splits a patch into multiple components. -/
def PeelingState := List (List LatticePoint)

/-- A simple baseline evaluation definition to anchor the module audit. -/
def certificate_baseline_marker : Nat := 0

#print axioms PeelingStep
#print axioms PeelingCertificate

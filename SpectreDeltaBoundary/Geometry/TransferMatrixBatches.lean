import SpectreDeltaBoundary.Paths
import Mathlib.Data.List.Perm.Subperm

set_option linter.style.header false
set_option linter.style.longLine false
set_option linter.unusedVariables false
set_option linter.style.whitespace false
set_option linter.style.setOption false

set_option maxHeartbeats 3000000

open AllowedStep

abbrev State := AllowedStep × AllowedStep × AllowedStep

def stepToDegrees (s : AllowedStep) : Int :=
  match s with
  | .m90 => -90
  | .m60 => -60
  | .z0   => 0
  | .p60 => 60
  | .p90 => 90

def isLockedState (s : State) : Bool :=
  match s with
  | (.z0, .p60, .z0) => true
  | (.p60, .p90, .p60) => true
  | _ => false

def completesLongLock (t1 t2 t3 t4 : AllowedStep) : Bool :=
  (t1 == .z0 ∧ t2 == .m60 ∧ t3 == .p90 ∧ t4 == .p60) ∨
  (t1 == .p60 ∧ t2 == .p90 ∧ t3 == .m60 ∧ t4 == .p90) ∨
  (t1 == .p90 ∧ t2 == .m60 ∧ t3 == .p90 ∧ t4 == .p60)

def isPuncturedState (s : State) : Bool :=
  match s with
  | (.m90, .m60, .m90) => true
  | (.m90, .m60, .z0)   => true
  | (.m90, .m60, .p90) => true
  | (.m90, .p60, .m90) => true
  | (.m90, .p60, .z0)   => true
  | (.m90, .p60, .p90) => true
  | (.m60, .m90, .m60) => true
  | (.m60, .m90, .p60) => true
  | (.m60, .z0,   .m60) => true
  | (.m60, .z0,   .p60) => true
  | (.m60, .p90, .m60) => true
  | (.m60, .p90, .p60) => true
  | (.z0,   .m60, .m90) => true
  | (.z0,   .m60, .z0)   => true
  | (.z0,   .m60, .p90) => true
  | (.z0,   .p60, .m90) => true
  | (.p60, .m90, .m60) => true
  | (.p60, .m90, .p60) => true
  | (.p60, .z0,   .m60) => true
  | (.p60, .z0,   .p60) => true
  | (.p60, .p90, .m60) => true
  | (.p90, .m60, .m90) => true
  | (.p90, .m60, .z0)   => true
  | (.p90, .m60, .p90) => true
  | (.p90, .p60, .m90) => true
  | (.p90, .p60, .z0)   => true
  | _ => false

def isValidTransition (u v : State) : Bool :=
  let (t1, t2, t3) := u
  let (v1, v2, v3) := v
  (t2 == v1) ∧ (t3 == v2) ∧ isPuncturedState u ∧ isPuncturedState v ∧ ¬completesLongLock t1 t2 t3 v3

abbrev Walk := List State

def Walk.curvature (w : Walk) : Int :=
  match w with
  | [] => 0
  | [_] => 0
  | _ :: v :: w' => stepToDegrees v.2.2 + Walk.curvature (v :: w')

def IsValidWalk (w : Walk) : Prop :=
  match w with
  | [] => True
  | [u] => isPuncturedState u = true
  | u :: v :: w' => isValidTransition u v = true ∧ IsValidWalk (v :: w')

def getLastState (w : Walk) (default : State) : State :=
  match w with
  | [] => default
  | [x] => x
  | _ :: xs => getLastState xs default

def Walk.isCycle (w : Walk) : Bool :=
  match w with
  | [] => false
  | [_] => false
  | u :: v :: vs => isValidTransition (getLastState (v :: vs) u) u

def allAllowedSteps : List AllowedStep := [.m90, .m60, .z0, .p60, .p90]

def allStates : List State :=
  allAllowedSteps.flatMap (fun s1 =>
    allAllowedSteps.flatMap (fun s2 =>
      allAllowedSteps.map (fun s3 => (s1, s2, s3))
    )
  )

def puncturedStateList : List State :=
  allStates.filter isPuncturedState

def puncturedBatch1 : List State := puncturedStateList.take 7
def puncturedBatch2 : List State := (puncturedStateList.drop 7).take 7
def puncturedBatch3 : List State := (puncturedStateList.drop 14).take 6
def puncturedBatch4 : List State := puncturedStateList.drop 20

lemma puncturedStateList_eq_batches :
    puncturedStateList = puncturedBatch1 ++ puncturedBatch2 ++ puncturedBatch3 ++ puncturedBatch4 := by rfl

def stepToNat (s : AllowedStep) : Nat :=
  match s with
  | .m90 => 0
  | .m60 => 1
  | .z0   => 2
  | .p60 => 3
  | .p90 => 4

def stepLessThan (s1 s2 : AllowedStep) : Bool :=
  stepToNat s1 < stepToNat s2

def stateLessThan (u v : State) : Bool :=
  let (u1, u2, u3) := u
  let (v1, v2, v3) := v
  if stepLessThan u1 v1 then true
  else if stepLessThan v1 u1 then false
  else if stepLessThan u2 v2 then true
  else if stepLessThan v2 u2 then false
  else stepLessThan u3 v3

def stateCurvatureContribution (s : State) : Int :=
  stepToDegrees s.2.2

def computeCycleCurvature (visited : List State) (target : State) : Int :=
  match visited with
  | [] => 0
  | s :: ss =>
    if s == target then stateCurvatureContribution s
    else stateCurvatureContribution s + computeCycleCurvature ss target

inductive StepResult where
  | done (val : Bool)
  | recurse (nextState : State) (nextVisited : List State)

def checkStep_m90 (start : State) (visited : List State) (origin : State) : StepResult :=
  let nextState : State := (start.2.1, start.2.2, .m90)
  if isValidTransition start nextState then
    if nextState == origin then .done (computeCycleCurvature visited origin <= 60)
    else if stateLessThan nextState origin then .done true
    else if visited.contains nextState then .done true
    else .recurse nextState (nextState :: visited)
  else .done true

def checkStep_m60 (start : State) (visited : List State) (origin : State) : StepResult :=
  let nextState : State := (start.2.1, start.2.2, .m60)
  if isValidTransition start nextState then
    if nextState == origin then .done (computeCycleCurvature visited origin <= 60)
    else if stateLessThan nextState origin then .done true
    else if visited.contains nextState then .done true
    else .recurse nextState (nextState :: visited)
  else .done true

def checkStep_z0 (start : State) (visited : List State) (origin : State) : StepResult :=
  let nextState : State := (start.2.1, start.2.2, .z0)
  if isValidTransition start nextState then
    if nextState == origin then .done (computeCycleCurvature visited origin <= 60)
    else if stateLessThan nextState origin then .done true
    else if visited.contains nextState then .done true
    else .recurse nextState (nextState :: visited)
  else .done true

def checkStep_p60 (start : State) (visited : List State) (origin : State) : StepResult :=
  let nextState : State := (start.2.1, start.2.2, .p60)
  if isValidTransition start nextState then
    if nextState == origin then .done (computeCycleCurvature visited origin <= 60)
    else if stateLessThan nextState origin then .done true
    else if visited.contains nextState then .done true
    else .recurse nextState (nextState :: visited)
  else .done true

def checkStep_p90 (start : State) (visited : List State) (origin : State) : StepResult :=
  let nextState : State := (start.2.1, start.2.2, .p90)
  if isValidTransition start nextState then
    if nextState == origin then .done (computeCycleCurvature visited origin <= 60)
    else if stateLessThan nextState origin then .done true
    else if visited.contains nextState then .done true
    else .recurse nextState (nextState :: visited)
  else .done true

def checkFrom (start : State) (visited : List State) (fuel : Nat) (origin : State) : Bool :=
  match fuel with
  | 0 => true
  | f + 1 =>
    (match checkStep_m90 start visited origin with
     | .done b => b
     | .recurse nextState nextVisited => checkFrom nextState nextVisited f origin) &&
    (match checkStep_m60 start visited origin with
     | .done b => b
     | .recurse nextState nextVisited => checkFrom nextState nextVisited f origin) &&
    (match checkStep_z0 start visited origin with
     | .done b => b
     | .recurse nextState nextVisited => checkFrom nextState nextVisited f origin) &&
    (match checkStep_p60 start visited origin with
     | .done b => b
     | .recurse nextState nextVisited => checkFrom nextState nextVisited f origin) &&
    (match checkStep_p90 start visited origin with
     | .done b => b
     | .recurse nextState nextVisited => checkFrom nextState nextVisited f origin)

def verifyAllCyclesCeiling (maxDepth : Nat) : Bool :=
  puncturedStateList.all (fun s => checkFrom s [s] maxDepth s)

theorem verify_batch1 : puncturedBatch1.all (fun s => checkFrom s [s] 26 s) = true := by decide
theorem verify_batch2 : puncturedBatch2.all (fun s => checkFrom s [s] 26 s) = true := by decide
theorem verify_batch3 : puncturedBatch3.all (fun s => checkFrom s [s] 26 s) = true := by decide
theorem verify_batch4 : puncturedBatch4.all (fun s => checkFrom s [s] 26 s) = true := by decide
import Lean
import Lean.Util.FoldConsts

open Lean

structure DeclNode where
  name : String
  kind : String
  module : String
deriving ToJson

structure DeclEdge where
  src : String
  dst : String
  type : String
deriving ToJson

def moduleFromDeclName (declName : String) : String :=
  let parts := declName.splitOn "."
  match parts.reverse with
  | [] => declName
  | [_] => declName
  | _ :: tailRev =>
      String.intercalate "." tailRev.reverse

def isUserFacingMLTheoryDeclName (s : String) : Bool :=
  s.startsWith "MLTheory." && !s.contains "._"

def isMLTheoryDecl (n : Name) : Bool :=
  isUserFacingMLTheoryDeclName (toString n)

def isGraphRefDecl (n : Name) : Bool :=
  let s := toString n
  isUserFacingMLTheoryDeclName s || s = "Mathlib" || s.startsWith "Mathlib."

def constKind (ci : ConstantInfo) : String :=
  match ci with
  | .axiomInfo _ => "axiom"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .defnInfo _ => "def"
  | .quotInfo _ => "quot"
  | .inductInfo _ => "inductive"
  | .ctorInfo _ => "ctor"
  | .recInfo _ => "recursor"

def sortedNames (s : NameSet) : List Name :=
  (s.toList.toArray.qsort fun a b => toString a < toString b).toList

def addEdge
    (seen : Std.HashSet (String × String × String))
    (edges : Array DeclEdge)
    (src dst edgeType : String)
    : Std.HashSet (String × String × String) × Array DeclEdge :=
  let key := (src, edgeType, dst)
  if seen.contains key then
    (seen, edges)
  else
    (seen.insert key, edges.push { src := src, dst := dst, type := edgeType })

def collectDeclGraph (env : Environment) : Array DeclNode × Array DeclEdge :=
  Id.run do
    let mut nodes : Array DeclNode := #[]
    let mut edges : Array DeclEdge := #[]
    let mut seen : Std.HashSet (String × String × String) := {}

    for (declName, ci) in env.constants do
      if !isMLTheoryDecl declName then
        continue

      let src := toString declName
      nodes := nodes.push {
        name := src
        kind := constKind ci
        module := moduleFromDeclName src
      }

      for dstName in sortedNames ci.type.getUsedConstantsAsSet do
        if isGraphRefDecl dstName && dstName != declName then
          let dst := toString dstName
          let (seen', edges') := addEdge seen edges src dst "uses_type"
          seen := seen'
          edges := edges'

      match ci.value? with
      | some v =>
          for dstName in sortedNames v.getUsedConstantsAsSet do
            if isGraphRefDecl dstName && dstName != declName then
              let dst := toString dstName
              let (seen', edges') := addEdge seen edges src dst "uses_value"
              seen := seen'
              edges := edges'
      | none =>
          pure ()

    let sortedNodes := nodes.qsort fun a b => a.name < b.name
    let sortedEdges := edges.qsort fun a b =>
      if a.src = b.src then
        if a.type = b.type then
          a.dst < b.dst
        else
          a.type < b.type
      else
        a.src < b.src
    return (sortedNodes, sortedEdges)

def outputPathOfArgs (args : List String) : System.FilePath :=
  let filtered := args.filter fun s => s != "--"
  match filtered with
  | [] => "artifacts/graphs/decl_graph.json"
  | outPath :: _ => outPath

def main (args : List String) : IO UInt32 := do
  let imports : Array Import := #[{ module := `MLTheory }]
  let env ← importModules imports {} 1024
  let (nodes, edges) := collectDeclGraph env

  let outPath := outputPathOfArgs args
  let outFile : System.FilePath := outPath
  match outFile.parent with
  | some parent => IO.FS.createDirAll parent
  | none => pure ()

  let payload : Json := Json.mkObj [
    ("generated_by", toJson "tools/index/ExtractDeclDeps.lean"),
    ("module_prefix", toJson "MLTheory."),
    ("edge_types", toJson (["uses_type", "uses_value"] : List String)),
    ("node_count", toJson nodes.size),
    ("edge_count", toJson edges.size),
    ("nodes", toJson nodes),
    ("edges", toJson edges)
  ]
  IO.FS.writeFile outFile payload.pretty
  IO.println s!"[ExtractDeclDeps] wrote {outFile} (nodes={nodes.size}, edges={edges.size})"
  pure 0

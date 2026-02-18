import Lean
import Lean.Util.FoldConsts

open Lean

structure DeclNode where
  name : String
  kind : String
  module : String
  decl_kind : String
  generated : Bool
  generated_reason : Option String := none
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

def isTrackedDeclName (s : String) : Bool :=
  (s.startsWith "MLTheory." || s.startsWith "Incubator.") && !s.contains "._"

def isMLTheoryDecl (n : Name) : Bool :=
  isTrackedDeclName (toString n)

def isGraphRefDecl (n : Name) : Bool :=
  let s := toString n
  isTrackedDeclName s || s = "Mathlib" || s.startsWith "Mathlib."

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

def isGeneratedByKind (declKind : String) : Bool :=
  declKind = "ctor" || declKind = "recursor"

def isGeneratedByName (declName : String) : Bool :=
  let suffixes : List String := [
    ".noConfusion",
    ".noConfusionType",
    ".casesOn",
    ".recOn",
    ".brecOn",
    ".below",
    ".ibelow",
    ".mk",
    ".mk.inj",
    ".mk.injEq",
    ".mk.sizeOf_spec"
  ]
  suffixes.any (fun suffix => declName.endsWith suffix)
    || declName.contains "match_"
    || declName.contains "_match"
    || declName.contains "._"

def moduleFromEnv? (env : Environment) (declName : Name) : Option String := do
  let moduleIdx ← env.getModuleIdxFor? declName
  let moduleName ← env.header.moduleNames[moduleIdx.toNat]?
  some (toString moduleName)

def generatedReason
    (generatedByKind generatedByName usedFallbackModule : Bool)
    : Option String :=
  let reasons :=
    (if generatedByKind then ["kind"] else [])
    ++ (if generatedByName then ["name_pattern"] else [])
    ++ (if usedFallbackModule then ["fallback_module_guess"] else [])
  match reasons with
  | [] => none
  | _ => some (String.intercalate "," reasons)

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

def collectDeclGraph (env : Environment) : Array DeclNode × Array DeclEdge × Nat :=
  Id.run do
    let mut nodes : Array DeclNode := #[]
    let mut edges : Array DeclEdge := #[]
    let mut seen : Std.HashSet (String × String × String) := {}
    let mut fallbackModuleCount := 0

    for (declName, ci) in env.constants do
      if !isMLTheoryDecl declName then
        continue

      let src := toString declName
      let declKind := constKind ci
      let generatedByKind := isGeneratedByKind declKind
      let generatedByName := isGeneratedByName src
      let moduleFromEnv := moduleFromEnv? env declName
      let usedFallbackModule := moduleFromEnv.isNone
      let moduleId := moduleFromEnv.getD (moduleFromDeclName src)
      if usedFallbackModule then
        fallbackModuleCount := fallbackModuleCount + 1
      nodes := nodes.push {
        name := src
        kind := "decl"
        module := moduleId
        decl_kind := declKind
        generated := generatedByKind || generatedByName || usedFallbackModule
        generated_reason := generatedReason generatedByKind generatedByName usedFallbackModule
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
    return (sortedNodes, sortedEdges, fallbackModuleCount)

def outputPathOfArgs (args : List String) : System.FilePath :=
  let filtered := args.filter fun s => s != "--"
  match filtered with
  | [] => "artifacts/graphs/decl_graph.json"
  | outPath :: _ => outPath

def dottedName (s : String) : Name :=
  let parts := s.splitOn "." |>.filter (fun p => !p.isEmpty)
  parts.foldl (fun acc part => Name.str acc part) Name.anonymous

def importModulesOfArgs (args : List String) : Array Import :=
  let filtered := args.filter fun s => s != "--"
  let moduleNames :=
    match filtered with
    | [] => ["MLTheory"]
    | _ :: mods =>
        if mods.isEmpty then ["MLTheory"] else mods
  moduleNames.toArray.map (fun moduleName => { module := dottedName moduleName })

def main (args : List String) : IO UInt32 := do
  let imports := importModulesOfArgs args
  let env ← importModules imports {} 1024
  let (nodes, edges, fallbackModuleCount) := collectDeclGraph env

  let outPath := outputPathOfArgs args
  let outFile : System.FilePath := outPath
  match outFile.parent with
  | some parent => IO.FS.createDirAll parent
  | none => pure ()

  let payload : Json := Json.mkObj [
    ("generated_by", toJson "tools/index/ExtractDeclDeps.lean"),
    ("schema_version", toJson (2 : Nat)),
    ("module_prefixes", toJson (["MLTheory.", "Incubator."] : List String)),
    ("imports", toJson (imports.toList.map fun i => toString i.module)),
    ("edge_types", toJson (["uses_type", "uses_value"] : List String)),
    ("fallback_module_count", toJson fallbackModuleCount),
    ("node_count", toJson nodes.size),
    ("edge_count", toJson edges.size),
    ("nodes", toJson nodes),
    ("edges", toJson edges)
  ]
  IO.FS.writeFile outFile payload.pretty
  IO.println s!"[ExtractDeclDeps] wrote {outFile} (nodes={nodes.size}, edges={edges.size}, fallback_module_count={fallbackModuleCount})"
  pure 0

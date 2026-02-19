    const EDGE_COLORS = {
      imports: "var(--imports)",
      contains: "var(--contains)",
      uses_type: "var(--uses-type)",
      uses_value: "var(--uses-value)",
      decl_in_module: "var(--decl-in-module)",
      binds: "var(--binds)",
      alias_of: "var(--alias-of)",
      used_recently: "var(--used-recently)",
    };

    const MATHLIB_SLICE_ID = "MathlibSlice";
    const NODE_DRAG_THRESHOLD_PX = 6;
    const CANVAS_PAN_THRESHOLD_PX = 4;
    const MODULE_DECL_PAGE_SIZE = 20;
    const LAYOUT_STORAGE_KEY = "mltheory.graph.layout.v1";
    const PANEL_UI_STORAGE_KEY = "mltheory.graph.panels.v1";
    const dataCandidates = ["./_auto/subgraph.json", "../artifacts/graphs/subgraph.json"];
    const proofMapIndexCandidates = ["./_auto/proof_maps.json", "../docs/_auto/proof_maps.json"];
    const svg = document.getElementById("graph");

    const state = {
      graph: null,
      nodesById: new Map(),
      edges: [],
      outgoing: new Map(),
      incoming: new Map(),
      degree: new Map(),
      displayDegree: new Map(),
      visible: new Set(),
      selected: null,
      selectedEdge: null,
      pinned: new Map(),
      moduleDeclCursor: new Map(),
      freePos: new Map(),
      basePos: new Map(),
      lastPos: new Map(),
      lastDisplay: { nodes: [], edges: [] },
      world: { w: 3200, h: 1900 },
      view: { x: 0, y: 0, w: 3200, h: 1900 },
      drag: null,
      suppressClickUntil: 0,
      rafPending: false,
      searchMatches: [],
      domainProfiles: new Map(),
      domainAxes: { math: [], applied: [] },
      selectedMathTags: new Set(),
      selectedAppliedTags: new Set(),
      dataSource: "source: loading...",
      edgeCapApplied: false,
      panelUI: {
        overlayCollapsed: false,
        statsCollapsed: false,
      },
      proofMapEntries: [],
      activeProofMapId: "",
      proofMapNodeIds: null,
      proofMapEdgeKeys: null,
      datasetEntries: [],
      activeDatasetId: "latest",
      groupNodeMap: new Map(),
      groupMembers: new Map(),
      namespaceTree: {
        roots: [],
        children: new Map(),
        moduleSet: new Set(),
      },
      treeExpanded: new Set(),
      treeFocusRoot: "",
      importLens: {
        rootId: "",
        mode: "off",
        nodes: new Set(),
        edges: new Set(),
        depth: 0,
        truncated: false,
      },
      collectMeta: {
        mode: "module-map",
        maxNodes: 500,
        maxEdges: 5000,
        rankedNodeCount: 0,
        hiddenByNodeCap: 0,
        rawEdgeCount: 0,
        hiddenByEdgeCap: 0,
        collapsedMathlibModules: 0,
        groupDepth: 0,
        groupedModuleCount: 0,
        groupNodeCount: 0,
      },
    };

    const byId = (id) => document.getElementById(id);

    function activeViewMode() {
      const el = byId("viewMode");
      return el && typeof el.value === "string" ? el.value : "module-map";
    }

    function modeTitle(mode) {
      if (mode === "decl-neighborhood") return "Decl Neighborhood";
      if (mode === "concept-browser") return "Concept Browser";
      if (mode === "mathlib-lens") return "Mathlib Lens";
      return "Module Map";
    }

    function setSourceHint(extra = "") {
      const base = state.dataSource || "source: unknown";
      byId("sourceHint").textContent = extra ? `${base} | ${extra}` : base;
    }

    function edgeColor(type) {
      return EDGE_COLORS[type] || "#9aa8a0";
    }

    function degreeOf(id) {
      return state.degree.get(id) || 0;
    }

    function labelDegreeOf(id) {
      return state.displayDegree.get(id) || degreeOf(id);
    }

    function currentZoom() {
      return state.world.w / Math.max(state.view.w, 1);
    }

    function layerKey(node) {
      const layer = String((node && node.layer) || "other");
      if (layer === "core") return "core";
      if (layer === "methods") return "methods";
      if (layer === "applications") return "applications";
      if (layer === "books") return "books";
      if (layer === "mathlib") return "mathlib";
      return "other";
    }

    function nodeColor(node) {
      if (state.pinned.has(node.id)) return "var(--pin)";
      if (node && node.group === true) return "var(--contains)";
      if (node.spine) return "var(--spine)";
      if (node.kind === "concept") return "var(--concept)";
      if (node.kind === "module") return "var(--module)";
      return "var(--decl)";
    }

    function compactModuleLabel(id) {
      const normalized = String(id || "").replace(/^MLTheory\./, "");
      if (normalized.length <= 36) return normalized;
      const parts = normalized.split(".");
      if (parts.length >= 3) {
        const candidate = `${parts[0]}.…${parts.slice(-2).join(".")}`;
        if (candidate.length <= 40) return candidate;
      }
      return `${normalized.slice(0, 16)}…${normalized.slice(-18)}`;
    }

    function nodeLabelText(node) {
      if (!node) return "";
      if (node.id === MATHLIB_SLICE_ID) return "MathlibSlice";
      if (node.group === true && typeof node.title === "string" && node.title) {
        return `${compactModuleLabel(node.title)} [grp]`;
      }
      if (node.kind === "module") return compactModuleLabel(node.id);
      return node.title || node.id.split(".").pop() || node.id;
    }

    function hashInt(s) {
      let h = 2166136261;
      for (let i = 0; i < s.length; i++) {
        h ^= s.charCodeAt(i);
        h = (h * 16777619) >>> 0;
      }
      return h >>> 0;
    }

    function clamp(v, lo, hi) {
      return Math.max(lo, Math.min(hi, v));
    }

    function estimateLabelWidth(node) {
      const text = nodeLabelText(node);
      return Math.max(18, Math.min(320, text.length * 6.6 + 10));
    }

    function labelSpacingForRows(rows, options = {}) {
      const floor = Number.isFinite(options.floor) ? options.floor : 40;
      const ceil = Number.isFinite(options.ceil) ? options.ceil : 200;
      const factor = Number.isFinite(options.factor) ? options.factor : 0.5;
      if (!Array.isArray(rows) || rows.length === 0) return floor;

      let maxWidth = 0;
      let sumWidth = 0;
      for (const node of rows) {
        const w = estimateLabelWidth(node);
        maxWidth = Math.max(maxWidth, w);
        sumWidth += w;
      }
      const avgWidth = sumWidth / rows.length;
      const blended = Math.max(maxWidth * 0.6, avgWidth * 0.85) * factor;
      return clamp(blended, floor, ceil);
    }

    function sortNodesForDisplay(rows) {
      rows.sort((a, b) =>
        (b.spine ? 1 : 0) - (a.spine ? 1 : 0) ||
        (a.kind === "module" ? 0 : 1) - (b.kind === "module" ? 0 : 1) ||
        degreeOf(b.id) - degreeOf(a.id) ||
        a.id.localeCompare(b.id)
      );
      return rows;
    }

    function edgePriority(edgeType) {
      if (edgeType === "imports") return 0;
      if (edgeType === "contains") return 1;
      if (edgeType === "decl_in_module") return 2;
      if (edgeType === "binds") return 3;
      if (edgeType === "uses_value") return 4;
      if (edgeType === "uses_type") return 5;
      if (edgeType === "used_recently") return 6;
      if (edgeType === "alias_of") return 7;
      return 9;
    }

    function isEdgeTypeEnabled(type) {
      const el = byId(`edge_${type}`);
      if (!el) return true;
      return el.checked;
    }

    function isNodeKindEnabled(node) {
      if (node.kind === "module") return byId("kindModule").checked;
      if (node.kind === "decl") return byId("kindDecl").checked;
      if (node.kind === "concept") return byId("kindConcept").checked;
      return true;
    }

    function lensModules(rows, limit = 20) {
      const out = [];
      if (!Array.isArray(rows)) return out;
      for (const row of rows) {
        const module = row && typeof row === "object" ? row.module : row;
        if (!module || typeof module !== "string") continue;
        if (!state.nodesById.has(module)) continue;
        out.push(module);
        if (out.length >= limit) break;
      }
      return out;
    }

    function activeMathlibLensConfig() {
      const lens = state.graph && typeof state.graph === "object" && state.graph.mathlib_lens
        ? state.graph.mathlib_lens
        : {};
      const activeDomain = byId("domainFilter") ? byId("domainFilter").value : "all";
      const profile = activeDomain !== "all" ? state.domainProfiles.get(activeDomain) : null;
      const roots = profile && Array.isArray(profile.mathlib_slice_roots)
        ? profile.mathlib_slice_roots.filter((m) => typeof m === "string")
        : lensModules(lens.slice_roots || [], 40);
      const bridges = profile && Array.isArray(profile.bridge_modules)
        ? profile.bridge_modules.filter((m) => typeof m === "string")
        : [];
      const moduleRoots = profile && Array.isArray(profile.module_roots)
        ? profile.module_roots.filter((m) => typeof m === "string")
        : [];
      const hubs = lensModules(lens.top_hubs || [], 24);
      const aggregators = lensModules(lens.aggregators || [], 24);
      return { activeDomain, roots, bridges, hubs, aggregators, moduleRoots };
    }

    function shortestImportPath(srcId, dstId, maxDepth = 10) {
      if (!srcId || !dstId) return null;
      if (srcId === dstId) return [srcId];
      if (!state.nodesById.has(srcId) || !state.nodesById.has(dstId)) return null;

      const queue = [srcId];
      const depthBy = new Map([[srcId, 0]]);
      const prev = new Map();

      while (queue.length > 0) {
        const cur = queue.shift();
        const depth = depthBy.get(cur) || 0;
        if (depth >= maxDepth) continue;
        for (const edge of state.outgoing.get(cur) || []) {
          if (edge.type !== "imports") continue;
          const nxt = edge.dst;
          if (!nxt || depthBy.has(nxt)) continue;
          depthBy.set(nxt, depth + 1);
          prev.set(nxt, cur);
          if (nxt === dstId) {
            const path = [dstId];
            let p = dstId;
            while (prev.has(p)) {
              p = prev.get(p);
              path.push(p);
            }
            path.reverse();
            return path[0] === srcId ? path : null;
          }
          queue.push(nxt);
        }
      }
      return null;
    }

    function importLensEdgeKey(src, dst) {
      return `${src}__imports__${dst}`;
    }

    function collectImportTraversal(rootId, direction, maxDepth = 6, maxNodes = 900) {
      const nodes = new Set();
      const edges = new Set();
      if (!rootId || !state.nodesById.has(rootId)) {
        return { nodes, edges, truncated: false };
      }
      const root = state.nodesById.get(rootId);
      if (!root || root.kind !== "module") {
        return { nodes, edges, truncated: false };
      }

      const normalizedDirection = direction === "in" ? "in" : "out";
      const queue = [{ id: rootId, depth: 0 }];
      nodes.add(rootId);
      let truncated = false;

      while (queue.length > 0) {
        const row = queue.shift();
        if (!row || row.depth >= maxDepth) continue;
        const around = normalizedDirection === "out"
          ? (state.outgoing.get(row.id) || [])
          : (state.incoming.get(row.id) || []);
        for (const edge of around) {
          if (!edge || edge.type !== "imports") continue;
          const src = normalizedDirection === "out" ? row.id : edge.src;
          const dst = normalizedDirection === "out" ? edge.dst : row.id;
          const nextId = normalizedDirection === "out" ? edge.dst : edge.src;
          if (!nextId || !state.nodesById.has(nextId)) continue;
          const nextNode = state.nodesById.get(nextId);
          if (!nextNode || nextNode.kind !== "module") continue;
          edges.add(importLensEdgeKey(src, dst));
          if (!nodes.has(nextId)) {
            nodes.add(nextId);
            if (nodes.size >= maxNodes) {
              truncated = true;
              queue.length = 0;
              break;
            }
            queue.push({ id: nextId, depth: row.depth + 1 });
          }
        }
      }

      return { nodes, edges, truncated };
    }

    function setImportLens(rootId, mode = "deps", options = {}) {
      if (!rootId || !state.nodesById.has(rootId)) {
        clearImportLens();
        return;
      }
      const root = state.nodesById.get(rootId);
      if (!root || root.kind !== "module") {
        clearImportLens();
        return;
      }

      const depth = clamp(Number(options.depth || 6), 1, 12);
      const limit = clamp(Number(options.limit || 900), 80, 2400);
      const normalizedMode = mode === "dependees" || mode === "both" ? mode : "deps";

      const allNodes = new Set([rootId]);
      const allEdges = new Set();
      let truncated = false;

      if (normalizedMode === "deps" || normalizedMode === "both") {
        const out = collectImportTraversal(rootId, "out", depth, limit);
        for (const id of out.nodes) allNodes.add(id);
        for (const key of out.edges) allEdges.add(key);
        truncated = truncated || out.truncated;
      }
      if (normalizedMode === "dependees" || normalizedMode === "both") {
        const incoming = collectImportTraversal(rootId, "in", depth, limit);
        for (const id of incoming.nodes) allNodes.add(id);
        for (const key of incoming.edges) allEdges.add(key);
        truncated = truncated || incoming.truncated;
      }

      state.importLens = {
        rootId,
        mode: normalizedMode,
        nodes: allNodes,
        edges: allEdges,
        depth,
        truncated,
      };

      for (const moduleId of allNodes) {
        materializeNode(moduleId);
      }
    }

    function clearImportLens() {
      state.importLens = {
        rootId: "",
        mode: "off",
        nodes: new Set(),
        edges: new Set(),
        depth: 0,
        truncated: false,
      };
    }

    function isInScope(node) {
      const scope = byId("scope").value;
      if (scope === "all") return true;
      if (scope === "mltheory") return node.package !== "mathlib";
      return node.package === "mathlib";
    }

    function selectedAxisTags(axis) {
      if (axis === "math") return state.selectedMathTags instanceof Set ? state.selectedMathTags : new Set();
      return state.selectedAppliedTags instanceof Set ? state.selectedAppliedTags : new Set();
    }

    function axisTagSelectValue(axis) {
      const id = axis === "math" ? "mathTagFilter" : "appliedTagFilter";
      const el = byId(id);
      return el && typeof el.value === "string" ? el.value : "all";
    }

    function activeAxisTagToken(axis) {
      const selected = selectedAxisTags(axis);
      if (selected.size > 0) {
        return `multi:${Array.from(selected).sort().join("|")}`;
      }
      return axisTagSelectValue(axis);
    }

    function nodeMatchesAxisTags(node, axis) {
      const tags = axis === "math"
        ? (Array.isArray(node.math_tags) ? node.math_tags : [])
        : (Array.isArray(node.applied_tags) ? node.applied_tags : []);
      const selected = selectedAxisTags(axis);
      if (selected.size > 0) {
        for (const tag of tags) {
          if (selected.has(tag)) return true;
        }
        return false;
      }
      const active = axisTagSelectValue(axis);
      if (active === "all") return true;
      return tags.includes(active);
    }

    function nodePassesFilters(node) {
      if (!node || !node.id) return false;
      if (!isNodeKindEnabled(node)) return false;
      if (!isInScope(node)) return false;
      const layer = byId("layerFilter").value;
      if (layer !== "all" && String(node.layer || "") !== layer) return false;
      const activeProfile = byId("domainFilter").value;
      if (activeProfile !== "all") {
        const profiles = Array.isArray(node.profiles)
          ? node.profiles
          : (Array.isArray(node.domains) ? node.domains : []);
        if (!profiles.includes(activeProfile)) return false;
      }
      if (!nodeMatchesAxisTags(node, "math")) return false;
      if (!nodeMatchesAxisTags(node, "applied")) return false;
      if (node.kind === "decl" && !byId("showGenerated").checked && node.generated === true) return false;
      if (byId("spineOnly").checked) {
        // Keep module-map readable by default: do not hide non-spine modules.
        if (!(activeViewMode() === "module-map" && node.kind === "module") && !node.spine) return false;
      }
      return true;
    }

    function virtualMathlibNode(domains = []) {
      return {
        id: MATHLIB_SLICE_ID,
        kind: "module",
        title: "MathlibSlice",
        layer: "mathlib",
        package: "mathlib",
        spine: true,
        virtual: true,
        path: "",
        domains: Array.isArray(domains) ? domains : [],
      };
    }

    function datasetBundleRows() {
      const bundle = globalThis.__MLTHEORY_DATASETS__;
      if (!bundle || !Array.isArray(bundle.datasets)) return null;
      const rows = [];
      for (const row of bundle.datasets) {
        if (!row || typeof row.id !== "string" || !row.id) continue;
        const graph = row.subgraph;
        if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) continue;
        rows.push({
          id: row.id,
          label: typeof row.label === "string" && row.label ? row.label : row.id,
          graph,
        });
      }
      if (rows.length === 0) return null;
      return rows;
    }

    function datasetDefaultId(rows) {
      if (!rows || rows.length === 0) return "latest";
      const bundle = globalThis.__MLTHEORY_DATASETS__;
      const raw = bundle && typeof bundle.default_dataset === "string" ? bundle.default_dataset : "latest";
      if (rows.some((row) => row.id === raw)) return raw;
      return rows[0].id;
    }

    function refreshDatasetOptions() {
      const rows = datasetBundleRows();
      state.datasetEntries = rows || [];
      const select = byId("datasetSelect");
      if (!select) return;
      if (!rows || rows.length === 0) {
        select.innerHTML = '<option value="latest">latest</option>';
        select.value = "latest";
        select.disabled = true;
        return;
      }
      const options = rows.map((row) => `<option value="${row.id}">${row.label}</option>`);
      select.innerHTML = options.join("");
      const desired = rows.some((row) => row.id === state.activeDatasetId)
        ? state.activeDatasetId
        : datasetDefaultId(rows);
      state.activeDatasetId = desired;
      select.value = desired;
      select.disabled = rows.length <= 1;
    }

    async function loadData(datasetId = "latest") {
      const rows = datasetBundleRows();
      if (rows && rows.length > 0) {
        const desired = rows.some((row) => row.id === datasetId)
          ? datasetId
          : datasetDefaultId(rows);
        const row = rows.find((item) => item.id === desired) || rows[0];
        state.activeDatasetId = row.id;
        state.dataSource = `source: dataset ${row.id} (embedded snapshots)`;
        setSourceHint("");
        return row.graph;
      }
      const embedded = globalThis.__MLTHEORY_SUBGRAPH__;
      if (embedded && Array.isArray(embedded.nodes) && Array.isArray(embedded.edges)) {
        state.activeDatasetId = "latest";
        state.dataSource = "source: ./_auto/subgraph.js";
        setSourceHint("");
        return embedded;
      }
      for (const path of dataCandidates) {
        try {
          const res = await fetch(path, { cache: "no-store" });
          if (!res.ok) continue;
          const graph = await res.json();
          state.activeDatasetId = "latest";
          state.dataSource = `source: ${path}`;
          setSourceHint("");
          return graph;
        } catch (_) {}
      }
      if (window.location.protocol === "file:") {
        throw new Error("No graph data in file:// mode. Run `tools/index/gen_graph_artifacts.sh` and reopen this page.");
      }
      throw new Error("No graph data available.");
    }

    async function loadProofMapIndex() {
      const embedded = globalThis.__MLTHEORY_PROOF_MAP_INDEX__;
      if (embedded && Array.isArray(embedded.problems)) {
        return embedded;
      }
      for (const path of proofMapIndexCandidates) {
        try {
          const res = await fetch(path, { cache: "no-store" });
          if (!res.ok) continue;
          const data = await res.json();
          if (!data || !Array.isArray(data.problems)) continue;
          return data;
        } catch (_) {}
      }
      return { problems: [] };
    }

    async function loadProofMapData(path) {
      const embeddedMaps = globalThis.__MLTHEORY_PROOF_MAPS__;
      if (embeddedMaps && typeof embeddedMaps === "object" && typeof path === "string" && path) {
        const row = embeddedMaps[path];
        if (row && Array.isArray(row.nodes) && Array.isArray(row.edges)) {
          return row;
        }
      }
      const candidates = [];
      if (typeof path === "string" && path) {
        candidates.push(path);
        if (path.startsWith("./_auto/")) {
          candidates.push(`../docs/_auto/${path.slice("./_auto/".length)}`);
        }
      }
      for (const candidate of candidates) {
        try {
          const res = await fetch(candidate, { cache: "no-store" });
          if (!res.ok) continue;
          const data = await res.json();
          if (data && Array.isArray(data.nodes) && Array.isArray(data.edges)) {
            return data;
          }
        } catch (_) {}
      }
      return null;
    }

    function buildIndex() {
      state.nodesById.clear();
      state.outgoing.clear();
      state.incoming.clear();
      state.degree.clear();
      state.edges = [];

      for (const node of state.graph.nodes || []) {
        if (!node || !node.id) continue;
        state.nodesById.set(node.id, node);
        state.degree.set(node.id, 0);
      }

      for (const edge of state.graph.edges || []) {
        if (!edge || !edge.src || !edge.dst) continue;
        if (!state.nodesById.has(edge.src) || !state.nodesById.has(edge.dst)) continue;
        state.edges.push(edge);
        if (!state.outgoing.has(edge.src)) state.outgoing.set(edge.src, []);
        if (!state.incoming.has(edge.dst)) state.incoming.set(edge.dst, []);
        state.outgoing.get(edge.src).push(edge);
        state.incoming.get(edge.dst).push(edge);
        state.degree.set(edge.src, degreeOf(edge.src) + 1);
        state.degree.set(edge.dst, degreeOf(edge.dst) + 1);
      }
    }

    function moduleChildModules(moduleId) {
      const out = [];
      for (const edge of state.outgoing.get(moduleId) || []) {
        if (!edge || edge.type !== "contains") continue;
        const childId = edge.dst;
        if (!childId || !state.nodesById.has(childId)) continue;
        const child = state.nodesById.get(childId);
        if (!child || child.kind !== "module") continue;
        out.push(childId);
      }
      return out;
    }

    function moduleSubtreeIds(rootId, limit = 3000) {
      if (!rootId || !state.nodesById.has(rootId)) return [];
      const root = state.nodesById.get(rootId);
      if (!root || root.kind !== "module") return [];
      const seen = new Set([rootId]);
      const out = [rootId];
      const queue = [rootId];
      while (queue.length > 0 && out.length < limit) {
        const cur = queue.shift();
        for (const childId of moduleChildModules(cur)) {
          if (seen.has(childId)) continue;
          seen.add(childId);
          out.push(childId);
          queue.push(childId);
          if (out.length >= limit) break;
        }
      }
      return out;
    }

    function rebuildNamespaceTree() {
      const moduleSet = new Set();
      for (const node of state.nodesById.values()) {
        if (!node || node.kind !== "module") continue;
        if (node.id === MATHLIB_SLICE_ID) continue;
        moduleSet.add(node.id);
      }

      const children = new Map();
      const parentCount = new Map();
      for (const id of moduleSet) {
        children.set(id, []);
        parentCount.set(id, 0);
      }

      for (const edge of state.edges) {
        if (!edge || edge.type !== "contains") continue;
        const src = edge.src;
        const dst = edge.dst;
        if (!moduleSet.has(src) || !moduleSet.has(dst) || src === dst) continue;
        const arr = children.get(src);
        if (arr && !arr.includes(dst)) arr.push(dst);
        parentCount.set(dst, (parentCount.get(dst) || 0) + 1);
      }

      for (const id of moduleSet) {
        if ((parentCount.get(id) || 0) > 0) continue;
        const parts = id.split(".").filter((p) => p);
        for (let i = parts.length - 1; i >= 1; i -= 1) {
          const parentId = parts.slice(0, i).join(".");
          if (!moduleSet.has(parentId) || parentId === id) continue;
          const arr = children.get(parentId);
          if (arr && !arr.includes(id)) {
            arr.push(id);
            parentCount.set(id, (parentCount.get(id) || 0) + 1);
          }
          break;
        }
      }

      for (const arr of children.values()) {
        arr.sort((a, b) => a.localeCompare(b));
      }
      const roots = Array.from(moduleSet)
        .filter((id) => (parentCount.get(id) || 0) === 0)
        .sort((a, b) => a.localeCompare(b));

      state.namespaceTree = { roots, children, moduleSet };
      if (!(state.treeExpanded instanceof Set)) {
        state.treeExpanded = new Set();
      }
      if (state.treeExpanded.size === 0) {
        for (const rootId of roots.slice(0, 8)) state.treeExpanded.add(rootId);
        for (const id of moduleSet) {
          if (id.split(".").length <= 2) state.treeExpanded.add(id);
        }
      }
      if (state.treeFocusRoot && !moduleSet.has(state.treeFocusRoot)) {
        state.treeFocusRoot = "";
      }
    }

    function initDomainFilter() {
      const select = byId("domainFilter");
      const mathSelect = byId("mathTagFilter");
      const appliedSelect = byId("appliedTagFilter");
      if (!select) return;
      const domains = state.graph && state.graph.domains && Array.isArray(state.graph.domains.profiles)
        ? state.graph.domains
        : { default_domain: "all", profiles: [] };

      state.domainProfiles = new Map();
      const options = ['<option value="all">all domains</option>'];
      for (const profile of domains.profiles) {
        if (!profile || typeof profile.id !== "string" || !profile.id) continue;
        state.domainProfiles.set(profile.id, profile);
        const title = typeof profile.title === "string" && profile.title ? profile.title : profile.id;
        options.push(`<option value="${profile.id}">${profile.id} (${title})</option>`);
      }
      select.innerHTML = options.join("");
      const defaultProfile = typeof domains.default_profile === "string" && state.domainProfiles.has(domains.default_profile)
        ? domains.default_profile
        : (
          typeof domains.default_domain === "string" && state.domainProfiles.has(domains.default_domain)
            ? domains.default_domain
            : "all"
        );
      select.value = defaultProfile;

      if (mathSelect) {
        const rows = domains.axes && domains.axes.math && Array.isArray(domains.axes.math.tags)
          ? domains.axes.math.tags
          : [];
        const normalizedRows = [];
        const tags = ['<option value="all">all math tags</option>'];
        for (const row of rows) {
          if (!row || typeof row.id !== "string" || !row.id) continue;
          const title = typeof row.title === "string" && row.title ? row.title : row.id;
          normalizedRows.push({ id: row.id, title });
          tags.push(`<option value="${row.id}">${row.id} (${title})</option>`);
        }
        mathSelect.innerHTML = tags.join("");
        mathSelect.value = "all";
        state.domainAxes.math = normalizedRows;
      }

      if (appliedSelect) {
        const rows = domains.axes && domains.axes.applied && Array.isArray(domains.axes.applied.tags)
          ? domains.axes.applied.tags
          : [];
        const normalizedRows = [];
        const tags = ['<option value="all">all applied tags</option>'];
        for (const row of rows) {
          if (!row || typeof row.id !== "string" || !row.id) continue;
          const title = typeof row.title === "string" && row.title ? row.title : row.id;
          normalizedRows.push({ id: row.id, title });
          tags.push(`<option value="${row.id}">${row.id} (${title})</option>`);
        }
        appliedSelect.innerHTML = tags.join("");
        appliedSelect.value = "all";
        state.domainAxes.applied = normalizedRows;
      }

      const mathIds = new Set((state.domainAxes.math || []).map((row) => row.id));
      for (const tag of Array.from(selectedAxisTags("math"))) {
        if (!mathIds.has(tag)) state.selectedMathTags.delete(tag);
      }
      const appliedIds = new Set((state.domainAxes.applied || []).map((row) => row.id));
      for (const tag of Array.from(selectedAxisTags("applied"))) {
        if (!appliedIds.has(tag)) state.selectedAppliedTags.delete(tag);
      }
    }

    function resetToModuleMap() {
      state.visible.clear();
      state.moduleDeclCursor.clear();
      for (const node of state.nodesById.values()) {
        if (node.kind === "module") state.visible.add(node.id);
      }
      state.selected = null;
      state.selectedEdge = null;
      state.view = { x: 0, y: 0, w: state.world.w, h: state.world.h };
    }

    function materializeNode(id) {
      if (!id || !state.nodesById.has(id)) return;
      state.visible.add(id);
      const node = state.nodesById.get(id);
      if (node.kind === "decl" && typeof node.module === "string" && node.module) {
        state.visible.add(node.module);
      }
    }

    function sortedVisibleNodes() {
      const rows = [];
      for (const id of state.visible) {
        const node = state.nodesById.get(id);
        if (!node) continue;
        if (!nodePassesFilters(node)) continue;
        rows.push(node);
      }
      return sortNodesForDisplay(rows);
    }

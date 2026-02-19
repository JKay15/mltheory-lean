    const EDGE_COLORS = {
      imports: "var(--imports)",
      uses_type: "var(--uses-type)",
      uses_value: "var(--uses-value)",
      decl_in_module: "var(--decl-in-module)",
      binds: "var(--binds)",
      alias_of: "var(--alias-of)",
      used_recently: "var(--used-recently)",
    };

    const MATHLIB_SLICE_ID = "MathlibSlice";
    const NODE_DOUBLE_CLICK_MS = 320;
    const LAYOUT_STORAGE_KEY = "mltheory.graph.layout.v1";
    const dataCandidates = ["./_auto/subgraph.json", "../artifacts/graphs/subgraph.json"];
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
      freePos: new Map(),
      basePos: new Map(),
      lastPos: new Map(),
      lastDisplay: { nodes: [], edges: [] },
      world: { w: 3200, h: 1900 },
      view: { x: 0, y: 0, w: 3200, h: 1900 },
      drag: null,
      suppressClickUntil: 0,
      lastNodeClick: { id: "", at: 0 },
      rafPending: false,
      searchMatches: [],
      domainProfiles: new Map(),
      dataSource: "source: loading...",
      edgeCapApplied: false,
    };

    const byId = (id) => document.getElementById(id);

    function activeViewMode() {
      const el = byId("viewMode");
      return el && typeof el.value === "string" ? el.value : "module-map";
    }

    function modeTitle(mode) {
      if (mode === "decl-neighborhood") return "Decl Neighborhood";
      if (mode === "concept-browser") return "Concept Browser";
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
      if (edgeType === "decl_in_module") return 1;
      if (edgeType === "binds") return 2;
      if (edgeType === "uses_value") return 3;
      if (edgeType === "uses_type") return 4;
      if (edgeType === "used_recently") return 5;
      if (edgeType === "alias_of") return 6;
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

    function isInScope(node) {
      const scope = byId("scope").value;
      if (scope === "all") return true;
      if (scope === "mltheory") return node.package !== "mathlib";
      return node.package === "mathlib";
    }

    function nodePassesFilters(node) {
      if (!node || !node.id) return false;
      if (!isNodeKindEnabled(node)) return false;
      if (!isInScope(node)) return false;
      const layer = byId("layerFilter").value;
      if (layer !== "all" && String(node.layer || "") !== layer) return false;
      const activeDomain = byId("domainFilter").value;
      if (activeDomain !== "all") {
        const domains = Array.isArray(node.domains) ? node.domains : [];
        if (!domains.includes(activeDomain)) return false;
      }
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

    async function loadData() {
      const embedded = globalThis.__MLTHEORY_SUBGRAPH__;
      if (embedded && Array.isArray(embedded.nodes) && Array.isArray(embedded.edges)) {
        state.dataSource = "source: ./_auto/subgraph.js";
        setSourceHint("");
        return embedded;
      }
      for (const path of dataCandidates) {
        try {
          const res = await fetch(path, { cache: "no-store" });
          if (!res.ok) continue;
          const graph = await res.json();
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

    function initDomainFilter() {
      const select = byId("domainFilter");
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
      select.value = "all";
    }

    function resetToModuleMap() {
      state.visible.clear();
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

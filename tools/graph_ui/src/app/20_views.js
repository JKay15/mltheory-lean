    function collapseMathlib(nodes, edges) {
      if (byId("expandMathlib").checked) {
        return { nodes, edges, collapsedMathlibModules: 0 };
      }

      const hiddenMathlib = new Set(
        nodes
          .filter((n) => n.kind === "module" && n.package === "mathlib")
          .map((n) => n.id)
      );
      const virtualDomains = new Set();
      for (const n of nodes) {
        if (!hiddenMathlib.has(n.id)) continue;
        if (!Array.isArray(n.domains)) continue;
        for (const d of n.domains) {
          if (typeof d === "string" && d) virtualDomains.add(d);
        }
      }

      if (hiddenMathlib.size === 0) {
        return { nodes, edges, collapsedMathlibModules: 0 };
      }

      const keptNodes = nodes.filter((n) => !hiddenMathlib.has(n.id));
      const aggregated = new Map();
      const keptEdges = [];

      function bump(src, dst, type) {
        const key = `${src}__${type}__${dst}`;
        const prev = aggregated.get(key);
        if (prev) {
          prev.weight += 1;
        } else {
          aggregated.set(key, { src, dst, type, weight: 1, aggregated: true });
        }
      }

      for (const e of edges) {
        const srcHidden = hiddenMathlib.has(e.src);
        const dstHidden = hiddenMathlib.has(e.dst);

        if (!srcHidden && !dstHidden) {
          keptEdges.push(e);
          continue;
        }

        if (e.type !== "imports") continue;
        if (srcHidden && dstHidden) continue;

        const src = srcHidden ? MATHLIB_SLICE_ID : e.src;
        const dst = dstHidden ? MATHLIB_SLICE_ID : e.dst;
        if (src === dst) continue;
        bump(src, dst, "imports");
      }

      keptNodes.push(virtualMathlibNode(Array.from(virtualDomains).sort()));
      const allEdges = keptEdges.concat(Array.from(aggregated.values()));
      return { nodes: keptNodes, edges: allEdges, collapsedMathlibModules: hiddenMathlib.size };
    }

    function groupCollapseDepth() {
      const el = byId("groupCollapseDepth");
      if (!el) return 0;
      const raw = Number(el.value || "0");
      if (!Number.isFinite(raw) || raw < 0) return 0;
      return Math.floor(raw);
    }

    function moduleGroupPrefix(moduleId, depth) {
      if (depth <= 0 || typeof moduleId !== "string" || !moduleId || moduleId === MATHLIB_SLICE_ID) {
        return "";
      }
      const parts = moduleId.split(".").filter((p) => p);
      if (parts.length <= depth) return "";
      return parts.slice(0, depth).join(".");
    }

    function collapseNamespaceGroups(nodes, edges) {
      state.groupNodeMap = new Map();
      state.groupMembers = new Map();

      if (activeViewMode() !== "module-map") {
        return { nodes, edges, groupDepth: 0, groupedModules: 0, groupNodes: 0 };
      }

      const depth = groupCollapseDepth();
      if (depth <= 0) {
        return { nodes, edges, groupDepth: 0, groupedModules: 0, groupNodes: 0 };
      }

      const moduleToGroup = new Map();
      for (const node of nodes) {
        if (!node || node.kind !== "module") continue;
        const prefix = moduleGroupPrefix(node.id, depth);
        if (!prefix) continue;
        moduleToGroup.set(node.id, `@group:${prefix}`);
      }

      if (moduleToGroup.size === 0) {
        return { nodes, edges, groupDepth: depth, groupedModules: 0, groupNodes: 0 };
      }

      const groupAgg = new Map();
      const keptNodes = [];
      for (const node of nodes) {
        const gid = moduleToGroup.get(node.id);
        if (!gid) {
          keptNodes.push(node);
          continue;
        }
        const prefix = gid.slice("@group:".length);
        if (!groupAgg.has(gid)) {
          groupAgg.set(gid, {
            id: gid,
            prefix,
            members: [],
            spine: false,
            layerCount: new Map(),
            packageCount: new Map(),
            domains: new Set(),
            profiles: new Set(),
            mathTags: new Set(),
            appliedTags: new Set(),
          });
        }
        const row = groupAgg.get(gid);
        row.members.push(node.id);
        if (node.spine) row.spine = true;
        row.layerCount.set(String(node.layer || "other"), (row.layerCount.get(String(node.layer || "other")) || 0) + 1);
        row.packageCount.set(String(node.package || "local"), (row.packageCount.get(String(node.package || "local")) || 0) + 1);
        for (const d of Array.isArray(node.domains) ? node.domains : []) {
          if (typeof d === "string" && d) row.domains.add(d);
        }
        for (const d of Array.isArray(node.profiles) ? node.profiles : []) {
          if (typeof d === "string" && d) row.profiles.add(d);
        }
        for (const d of Array.isArray(node.math_tags) ? node.math_tags : []) {
          if (typeof d === "string" && d) row.mathTags.add(d);
        }
        for (const d of Array.isArray(node.applied_tags) ? node.applied_tags : []) {
          if (typeof d === "string" && d) row.appliedTags.add(d);
        }
      }

      const topKey = (counter, fallback) => {
        if (!(counter instanceof Map) || counter.size === 0) return fallback;
        let bestK = fallback;
        let bestV = -1;
        for (const [k, v] of counter.entries()) {
          if (v > bestV) {
            bestK = k;
            bestV = v;
          }
        }
        return bestK;
      };

      for (const agg of groupAgg.values()) {
        state.groupMembers.set(agg.id, agg.members.slice());
        const groupNode = {
          id: agg.id,
          kind: "module",
          title: agg.prefix,
          layer: topKey(agg.layerCount, "other"),
          package: topKey(agg.packageCount, "local"),
          spine: agg.spine,
          group: true,
          group_prefix: agg.prefix,
          group_member_count: agg.members.length,
          group_members: agg.members.slice(0, 12),
          domains: Array.from(agg.domains).sort(),
          profiles: Array.from(agg.profiles).sort(),
          math_tags: Array.from(agg.mathTags).sort(),
          applied_tags: Array.from(agg.appliedTags).sort(),
          path: `group:${agg.prefix}`,
        };
        keptNodes.push(groupNode);
      }

      const groupedEdges = new Map();
      const arrFrom = (val) => (Array.isArray(val) ? val.filter((x) => typeof x === "string" && x) : []);
      const edgeWeight = (edge) => {
        const w = Number(edge && edge.weight);
        return Number.isFinite(w) && w > 0 ? w : 1;
      };
      for (const edge of edges) {
        if (!edge || typeof edge.src !== "string" || typeof edge.dst !== "string") continue;
        const src = moduleToGroup.get(edge.src) || edge.src;
        const dst = moduleToGroup.get(edge.dst) || edge.dst;
        if (!src || !dst || src === dst) continue;
        const type = typeof edge.type === "string" && edge.type ? edge.type : "imports";
        const key = `${src}__${type}__${dst}`;
        if (!groupedEdges.has(key)) {
          groupedEdges.set(key, {
            src,
            dst,
            type,
            weight: edgeWeight(edge),
            aggregated: src !== edge.src || dst !== edge.dst || edge.aggregated === true,
            domains: new Set(arrFrom(edge.domains)),
            math_tags: new Set(arrFrom(edge.math_tags)),
            applied_tags: new Set(arrFrom(edge.applied_tags)),
          });
        } else {
          const row = groupedEdges.get(key);
          row.weight += edgeWeight(edge);
          for (const d of arrFrom(edge.domains)) row.domains.add(d);
          for (const d of arrFrom(edge.math_tags)) row.math_tags.add(d);
          for (const d of arrFrom(edge.applied_tags)) row.applied_tags.add(d);
          if (src !== edge.src || dst !== edge.dst || edge.aggregated === true) {
            row.aggregated = true;
          }
        }
      }

      const outEdges = Array.from(groupedEdges.values()).map((row) => ({
        src: row.src,
        dst: row.dst,
        type: row.type,
        weight: row.weight,
        aggregated: row.aggregated === true,
        domains: Array.from(row.domains).sort(),
        math_tags: Array.from(row.math_tags).sort(),
        applied_tags: Array.from(row.applied_tags).sort(),
      }));
      outEdges.sort((a, b) =>
        edgePriority(a.type) - edgePriority(b.type) ||
        b.weight - a.weight ||
        a.src.localeCompare(b.src) ||
        a.dst.localeCompare(b.dst)
      );

      state.groupNodeMap = moduleToGroup;
      return {
        nodes: keptNodes,
        edges: outEdges,
        groupDepth: depth,
        groupedModules: moduleToGroup.size,
        groupNodes: groupAgg.size,
      };
    }

    function forceNodeInList(rows, node, maxNodes) {
      if (!node || !node.id) return rows;
      if (rows.some((n) => n.id === node.id)) return rows;
      const out = rows.slice(0, Math.max(0, maxNodes - 1));
      out.unshift(node);
      return out;
    }

    function collectModuleMapGraph(maxNodes) {
      if (typeof syncExpandedModuleDecls === "function") {
        syncExpandedModuleDecls();
      }

      const focusRoot = state.treeFocusRoot;
      const focusModules = focusRoot ? new Set(moduleSubtreeIds(focusRoot, 3500)) : null;
      const inFocusedSubtree = (node) => {
        if (!focusModules) return true;
        if (!node) return false;
        if (node.kind === "module") return focusModules.has(node.id);
        if (node.kind === "decl") {
          const mod = typeof node.module === "string" ? node.module : "";
          return !!mod && focusModules.has(mod);
        }
        if (node.kind === "concept") return false;
        return true;
      };

      const include = new Map();
      const pushNode = (node) => {
        if (!node || !node.id) return;
        if (!nodePassesFilters(node)) return;
        if (!inFocusedSubtree(node)) return;
        include.set(node.id, node);
      };

      for (const id of state.visible) {
        pushNode(state.nodesById.get(id));
      }

      if (byId("kindConcept").checked) {
        for (const node of state.nodesById.values()) {
          if (node.kind !== "concept") continue;
          pushNode(node);
        }
      }

      if (state.selected && state.nodesById.has(state.selected)) {
        const selectedNode = state.nodesById.get(state.selected);
        if (selectedNode && inFocusedSubtree(selectedNode)) {
          pushNode(selectedNode);
        } else if (selectedNode && selectedNode.kind === "module" && state.groupMembers.has(selectedNode.id)) {
          const members = state.groupMembers.get(selectedNode.id) || [];
          for (const mid of members.slice(0, 24)) {
            if (!state.nodesById.has(mid)) continue;
            pushNode(state.nodesById.get(mid));
          }
        }
      }

      const ranked = sortNodesForDisplay(Array.from(include.values()));
      return collectWithNodeList(ranked, maxNodes);
    }

    function defaultNeighborhoodCenterId() {
      if (state.selected && state.nodesById.has(state.selected)) {
        return state.selected;
      }
      if (state.searchMatches.length > 0 && state.nodesById.has(state.searchMatches[0].id)) {
        return state.searchMatches[0].id;
      }
      const decls = [];
      for (const node of state.nodesById.values()) {
        if (node.kind !== "decl") continue;
        if (!nodePassesFilters(node)) continue;
        decls.push(node);
      }
      if (!decls.length) return "";
      sortNodesForDisplay(decls);
      return decls[0].id;
    }

    function collectDeclNeighborhoodGraph(maxNodes) {
      const depth = clamp(Number(byId("neighborhoodDepth").value || "1"), 1, 3);
      const centerId = defaultNeighborhoodCenterId();
      if (!centerId || !state.nodesById.has(centerId)) {
        return { nodes: [], edges: [] };
      }

      const seen = new Set([centerId]);
      const queue = [{ id: centerId, depth: 0 }];

      while (queue.length > 0) {
        const row = queue.shift();
        if (!row || row.depth >= depth) continue;
        const around = (state.outgoing.get(row.id) || []).concat(state.incoming.get(row.id) || []);
        for (const e of around) {
          if (!isEdgeTypeEnabled(e.type)) continue;
          const nextId = e.src === row.id ? e.dst : e.src;
          if (!state.nodesById.has(nextId)) continue;
          if (!seen.has(nextId)) {
            seen.add(nextId);
            queue.push({ id: nextId, depth: row.depth + 1 });
          }
          const nextNode = state.nodesById.get(nextId);
          if (nextNode && nextNode.kind === "decl" && typeof nextNode.module === "string" && nextNode.module) {
            seen.add(nextNode.module);
          }
        }
      }

      const centerNode = state.nodesById.get(centerId);
      if (centerNode && centerNode.kind === "decl" && typeof centerNode.module === "string" && centerNode.module) {
        seen.add(centerNode.module);
      }

      const nodes = [];
      for (const id of seen) {
        const node = state.nodesById.get(id);
        if (!node) continue;
        if (id !== centerId && !nodePassesFilters(node)) continue;
        nodes.push(node);
      }

      sortNodesForDisplay(nodes);
      const ranked = forceNodeInList(nodes, centerNode, maxNodes);
      return collectWithNodeList(ranked, maxNodes);
    }

    function collectConceptBrowserGraph(maxNodes) {
      const ids = new Set();
      for (const node of state.nodesById.values()) {
        if (node.kind !== "concept") continue;
        if (!nodePassesFilters(node)) continue;
        ids.add(node.id);
      }

      for (const e of state.edges) {
        if (e.type !== "binds" || !isEdgeTypeEnabled(e.type)) continue;
        if (ids.has(e.src) && state.nodesById.has(e.dst)) ids.add(e.dst);
      }

      for (const id of Array.from(ids)) {
        const node = state.nodesById.get(id);
        if (!node || node.kind !== "decl") continue;
        if (typeof node.module === "string" && node.module) ids.add(node.module);
      }

      const nodes = [];
      for (const id of ids) {
        const node = state.nodesById.get(id);
        if (!node) continue;
        if (node.kind !== "concept" && !nodePassesFilters(node)) continue;
        nodes.push(node);
      }
      sortNodesForDisplay(nodes);
      return collectWithNodeList(nodes, maxNodes);
    }

    function collectMathlibLensGraph(maxNodes) {
      const lens = activeMathlibLensConfig();
      const include = new Set();

      const targets = [];
      for (const id of lens.roots || []) {
        if (typeof id === "string" && state.nodesById.has(id)) targets.push(id);
      }
      for (const id of lens.hubs || []) {
        if (typeof id === "string" && state.nodesById.has(id)) targets.push(id);
      }
      for (const id of lens.aggregators || []) {
        if (typeof id === "string" && state.nodesById.has(id)) targets.push(id);
      }
      for (const id of lens.bridges || []) {
        if (typeof id === "string" && state.nodesById.has(id)) include.add(id);
      }

      const localSources = new Set();
      const selected = state.selected ? state.nodesById.get(state.selected) : null;
      if (selected) {
        if (selected.kind === "module" && selected.package !== "mathlib") {
          localSources.add(selected.id);
        } else if (selected.kind === "decl" && typeof selected.module === "string") {
          localSources.add(selected.module);
        }
      }
      if (localSources.size === 0) {
        for (const root of lens.moduleRoots || []) {
          if (typeof root !== "string") continue;
          if (state.nodesById.has(root)) {
            localSources.add(root);
          }
          for (const node of state.nodesById.values()) {
            if (node.kind !== "module" || node.package === "mathlib") continue;
            if (node.id === root || node.id.startsWith(`${root}.`)) {
              localSources.add(node.id);
              break;
            }
          }
        }
      }
      if (localSources.size === 0) {
        for (const node of state.nodesById.values()) {
          if (node.kind !== "module" || node.package === "mathlib") continue;
          if (!node.spine) continue;
          localSources.add(node.id);
          if (localSources.size >= 3) break;
        }
      }

      for (const src of localSources) include.add(src);
      for (const t of targets) include.add(t);

      const targetLimit = 20;
      const limitedTargets = targets.slice(0, targetLimit);
      for (const src of localSources) {
        for (const dst of limitedTargets) {
          const path = shortestImportPath(src, dst, 10);
          if (!path || path.length === 0) continue;
          for (const id of path) include.add(id);
        }
      }

      const nodes = [];
      for (const id of include) {
        const node = state.nodesById.get(id);
        if (!node || node.kind !== "module") continue;
        if (!nodePassesFilters(node)) continue;
        nodes.push(node);
      }
      if (!nodes.length) {
        return collectModuleMapGraph(maxNodes);
      }
      sortNodesForDisplay(nodes);
      return collectWithNodeList(nodes, maxNodes);
    }

    function collectWithNodeList(rankedNodes, maxNodes) {
      const rankedNodeCount = rankedNodes.length;
      const nodes = rankedNodes.slice(0, maxNodes);
      const hiddenByNodeCap = Math.max(0, rankedNodeCount - nodes.length);
      const nodeSet = new Set(nodes.map((n) => n.id));
      const edges = [];
      for (const e of state.edges) {
        if (!isEdgeTypeEnabled(e.type)) continue;
        if (!nodeSet.has(e.src) || !nodeSet.has(e.dst)) continue;
        edges.push(e);
      }
      const rawEdgeCount = edges.length;
      const maxEdges = Number(byId("maxEdges").value || "5000");
      let limitedEdges = edges;
      state.edgeCapApplied = false;
      if (Number.isFinite(maxEdges) && maxEdges > 0 && edges.length > maxEdges) {
        limitedEdges = edges
          .slice()
          .sort((a, b) =>
            edgePriority(a.type) - edgePriority(b.type) ||
            ((b.weight || 1) - (a.weight || 1)) ||
            a.src.localeCompare(b.src) ||
            a.dst.localeCompare(b.dst)
          )
          .slice(0, maxEdges);
        state.edgeCapApplied = true;
      }
      const hiddenByEdgeCap = Math.max(0, rawEdgeCount - limitedEdges.length);
      const collapsed = collapseMathlib(nodes, limitedEdges);
      const grouped = collapseNamespaceGroups(collapsed.nodes, collapsed.edges);
      state.collectMeta = {
        ...state.collectMeta,
        rankedNodeCount,
        hiddenByNodeCap,
        rawEdgeCount,
        hiddenByEdgeCap,
        collapsedMathlibModules: collapsed.collapsedMathlibModules || 0,
        groupDepth: grouped.groupDepth || 0,
        groupedModuleCount: grouped.groupedModules || 0,
        groupNodeCount: grouped.groupNodes || 0,
      };
      if (state.selected && state.groupNodeMap.has(state.selected)) {
        state.selected = state.groupNodeMap.get(state.selected) || state.selected;
      }
      return { nodes: grouped.nodes, edges: grouped.edges };
    }

    function applyProofMapFilter(display) {
      if (!(state.proofMapNodeIds instanceof Set) || state.proofMapNodeIds.size === 0) {
        return display;
      }
      const nodes = (display.nodes || []).filter((n) => state.proofMapNodeIds.has(n.id));
      const nodeSet = new Set(nodes.map((n) => n.id));
      let edges = (display.edges || []).filter((e) => nodeSet.has(e.src) && nodeSet.has(e.dst));
      if (state.proofMapEdgeKeys instanceof Set && state.proofMapEdgeKeys.size > 0) {
        edges = edges.filter((e) => state.proofMapEdgeKeys.has(`${e.src}__${e.type}__${e.dst}`));
      }
      return { nodes, edges };
    }

    function collectDisplayGraph() {
      const maxNodes = Number(byId("maxNodes").value || "500");
      const mode = activeViewMode();
      const maxEdges = Number(byId("maxEdges").value || "5000");
      state.collectMeta = {
        mode,
        maxNodes,
        maxEdges,
        rankedNodeCount: 0,
        hiddenByNodeCap: 0,
        rawEdgeCount: 0,
        hiddenByEdgeCap: 0,
        collapsedMathlibModules: 0,
        groupDepth: 0,
        groupedModuleCount: 0,
        groupNodeCount: 0,
      };
      let display;
      if (mode === "decl-neighborhood") {
        display = collectDeclNeighborhoodGraph(maxNodes);
      } else if (mode === "concept-browser") {
        display = collectConceptBrowserGraph(maxNodes);
      } else if (mode === "mathlib-lens") {
        display = collectMathlibLensGraph(maxNodes);
      } else {
        display = collectModuleMapGraph(maxNodes);
      }
      const filtered = applyProofMapFilter(display);
      if (state.selected && !filtered.nodes.some((n) => n && n.id === state.selected)) {
        if (state.groupMembers instanceof Map && state.groupMembers.has(state.selected)) {
          const members = state.groupMembers.get(state.selected) || [];
          const fallback = members.find((id) => filtered.nodes.some((n) => n && n.id === id));
          state.selected = fallback || null;
        } else if (state.groupNodeMap instanceof Map && state.groupNodeMap.has(state.selected)) {
          const gid = state.groupNodeMap.get(state.selected);
          state.selected = filtered.nodes.some((n) => n && n.id === gid) ? gid : null;
        } else {
          state.selected = null;
        }
      }
      return filtered;
    }

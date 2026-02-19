    function collapseMathlib(nodes, edges) {
      if (byId("expandMathlib").checked) {
        return { nodes, edges };
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
        return { nodes, edges };
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
      return { nodes: keptNodes, edges: allEdges };
    }

    function forceNodeInList(rows, node, maxNodes) {
      if (!node || !node.id) return rows;
      if (rows.some((n) => n.id === node.id)) return rows;
      const out = rows.slice(0, Math.max(0, maxNodes - 1));
      out.unshift(node);
      return out;
    }

    function collectModuleMapGraph(maxNodes) {
      const ranked = sortedVisibleNodes();

      if (state.selected && state.nodesById.has(state.selected)) {
        const selectedNode = state.nodesById.get(state.selected);
        if (selectedNode && nodePassesFilters(selectedNode)) {
          return collectWithNodeList(forceNodeInList(ranked, selectedNode, maxNodes), maxNodes);
        }
      }
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

    function collectWithNodeList(rankedNodes, maxNodes) {
      const nodes = rankedNodes.slice(0, maxNodes);
      const nodeSet = new Set(nodes.map((n) => n.id));
      const edges = [];
      for (const e of state.edges) {
        if (!isEdgeTypeEnabled(e.type)) continue;
        if (!nodeSet.has(e.src) || !nodeSet.has(e.dst)) continue;
        edges.push(e);
      }
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
      return collapseMathlib(nodes, limitedEdges);
    }

    function collectDisplayGraph() {
      const maxNodes = Number(byId("maxNodes").value || "500");
      const mode = activeViewMode();
      if (mode === "decl-neighborhood") {
        return collectDeclNeighborhoodGraph(maxNodes);
      }
      if (mode === "concept-browser") {
        return collectConceptBrowserGraph(maxNodes);
      }
      return collectModuleMapGraph(maxNodes);
    }


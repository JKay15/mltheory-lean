    function applyViewBox() {
      const v = state.view;
      svg.setAttribute("viewBox", `${v.x} ${v.y} ${v.w} ${v.h}`);
    }

    function viewportAspect() {
      const rect = svg.getBoundingClientRect();
      const w = Math.max(rect.width, 1);
      const h = Math.max(rect.height, 1);
      return w / h;
    }

    function clampView() {
      const v = state.view;
      const maxX = state.world.w - v.w;
      const maxY = state.world.h - v.h;
      const marginX = Math.max(0.12 * state.world.w, 0.65 * v.w);
      const marginY = Math.max(0.12 * state.world.h, 0.65 * v.h);
      v.x = clamp(v.x, -marginX, Math.max(maxX, 0) + marginX);
      v.y = clamp(v.y, -marginY, Math.max(maxY, 0) + marginY);
    }

    function normalizeViewToViewport(anchorX, anchorY, px = 0.5, py = 0.5) {
      const aspect = viewportAspect();
      if (!Number.isFinite(aspect) || aspect <= 0) return;

      const safePx = clamp(Number(px), 0, 1);
      const safePy = clamp(Number(py), 0, 1);
      const currentAnchorX = Number.isFinite(anchorX) ? anchorX : (state.view.x + state.view.w * safePx);
      const currentAnchorY = Number.isFinite(anchorY) ? anchorY : (state.view.y + state.view.h * safePy);

      let w = state.view.w;
      let h = state.view.h;
      const currentAspect = w / Math.max(h, 1e-6);
      if (Math.abs(currentAspect - aspect) > 1e-3) {
        if (currentAspect > aspect) {
          h = w / aspect;
        } else {
          w = h * aspect;
        }
      }
      state.view.w = clamp(w, 220, state.world.w * 4.2);
      state.view.h = clamp(h, 160, state.world.h * 4.2);
      state.view.x = currentAnchorX - safePx * state.view.w;
      state.view.y = currentAnchorY - safePy * state.view.h;
      clampView();
    }

    function handleNodePrimaryClick(nodeId) {
      if (!nodeId) return;
      if (Date.now() < state.suppressClickUntil) return;
      state.selected = nodeId;
      state.selectedEdge = null;
      materializeNode(nodeId);
      refreshNodeVisualState();
      renderInspector(state.lastDisplay);
      renderOverlay(state.lastDisplay);
      renderSearchResults();
    }

    function handleNodeDoubleClick(nodeId) {
      if (!nodeId) return;
      state.selected = nodeId;
      state.selectedEdge = null;
      materializeNode(nodeId);
      togglePin(nodeId);
      renderAll();
    }

    function refreshNodeVisualState() {
      const lens = state.importLens && state.importLens.rootId
        ? state.importLens
        : null;
      const lensNodes = lens && lens.nodes instanceof Set ? lens.nodes : null;
      const lensRootId = lens ? lens.rootId : "";
      svg.querySelectorAll("g[data-node-id]").forEach((group) => {
        const id = group.getAttribute("data-node-id");
        if (!id) return;
        const circle = group.querySelector("circle");
        if (!circle) return;
        const isSelected = state.selected === id;
        const inLensNode = !!(lensNodes && lensNodes.has(id));
        const isLensRoot = lensRootId === id;
        const fillOpacity = isSelected
          ? "1"
          : (
            lens
              ? (isLensRoot || inLensNode ? "0.98" : "0.24")
              : "0.92"
          );
        circle.setAttribute("fill-opacity", fillOpacity);
        if (isSelected) {
          circle.setAttribute("stroke", "#0f271d");
          circle.setAttribute("stroke-width", "2.4");
        } else if (isLensRoot) {
          circle.setAttribute("stroke", "#8b3d00");
          circle.setAttribute("stroke-width", "2.6");
        } else if (inLensNode) {
          circle.setAttribute("stroke", "#2f6955");
          circle.setAttribute("stroke-width", "1.8");
        } else if (state.pinned.has(id)) {
          circle.setAttribute("stroke", "#2a0d2a");
          circle.setAttribute("stroke-width", "1.7");
        } else {
          circle.removeAttribute("stroke");
          circle.removeAttribute("stroke-width");
        }
      });
    }

    function renderGraph(display, skipInspector = false) {
      state.lastDisplay = display;
      computeLayout(display.nodes);
      state.lastPos = new Map();

      svg.innerHTML = "";
      normalizeViewToViewport(state.view.x + state.view.w / 2, state.view.y + state.view.h / 2, 0.5, 0.5);
      applyViewBox();

      const displayed = new Set(display.nodes.map((n) => n.id));
      const edges = display.edges.filter((e) => displayed.has(e.src) && displayed.has(e.dst));
      const lens = state.importLens && state.importLens.rootId
        ? state.importLens
        : null;
      const lensNodes = lens && lens.nodes instanceof Set ? lens.nodes : null;
      const lensEdges = lens && lens.edges instanceof Set ? lens.edges : null;
      const lensRootId = lens ? lens.rootId : "";
      state.displayDegree = new Map();
      for (const n of display.nodes) {
        state.displayDegree.set(n.id, 0);
      }
      for (const e of edges) {
        state.displayDegree.set(e.src, (state.displayDegree.get(e.src) || 0) + 1);
        state.displayDegree.set(e.dst, (state.displayDegree.get(e.dst) || 0) + 1);
      }

      const edgeG = document.createElementNS("http://www.w3.org/2000/svg", "g");
      for (const e of edges) {
        const a = nodePos(e.src);
        const b = nodePos(e.dst);
        const containsNearSelected = (
          e.type === "contains" &&
          !!state.selected &&
          (e.src === state.selected || e.dst === state.selected)
        );
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", String(a[0]));
        line.setAttribute("y1", String(a[1]));
        line.setAttribute("x2", String(b[0]));
        line.setAttribute("y2", String(b[1]));
        line.setAttribute("class", "edge");
        line.setAttribute("stroke", edgeColor(e.type));
        const isLensEdge = !!(lensEdges && e.type === "imports" && lensEdges.has(importLensEdgeKey(e.src, e.dst)));
        const edgeOpacity = state.selectedEdge === e
          ? "0.96"
          : (
            isLensEdge
              ? "0.88"
              : (lensEdges && e.type === "imports" ? "0.10" : (containsNearSelected ? "0.78" : "0.38"))
          );
        line.setAttribute("stroke-opacity", edgeOpacity);
        line.setAttribute("stroke-width", state.selectedEdge === e
          ? "2.8"
          : (
            isLensEdge
              ? "2.6"
              : (containsNearSelected ? "2.3" : String(1 + Math.log2((e.weight || 1) + 1) * 0.65))
          ));
        if (e.type === "contains") {
          line.setAttribute("stroke-dasharray", containsNearSelected ? "8 4" : "6 5");
        }
        line.addEventListener("click", (ev) => {
          ev.stopPropagation();
          state.selectedEdge = e;
          state.selected = null;
          refreshNodeVisualState();
          renderInspector(display);
          renderOverlay(display);
        });
        edgeG.appendChild(line);
      }
      svg.appendChild(edgeG);

      const mode = activeViewMode();
      const nodeG = document.createElementNS("http://www.w3.org/2000/svg", "g");
      const placedLabelBoxes = [];
      const drawNodes = sortNodesForDisplay(display.nodes.slice());
      for (const n of drawNodes) {
        const [x, y] = nodePos(n.id);
        state.lastPos.set(n.id, [x, y]);

        const deg = degreeOf(n.id);
        const base = n.kind === "module" ? 7 : (n.kind === "concept" ? 8 : 4.5);
        const r = Math.min(15, base + Math.log2(deg + 1) * 1.15);

        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("data-node-id", n.id);

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", String(x));
        circle.setAttribute("cy", String(y));
        circle.setAttribute("r", String(r));
        circle.setAttribute("fill", nodeColor(n));
        const inLensNode = !!(lensNodes && lensNodes.has(n.id));
        const isLensRoot = lensRootId === n.id;
        const fillOpacity = state.selected === n.id
          ? "1"
          : (
            lens
              ? (isLensRoot || inLensNode ? "0.98" : "0.24")
              : "0.92"
          );
        circle.setAttribute("fill-opacity", fillOpacity);
        circle.style.cursor = "pointer";

        if (state.selected === n.id) {
          circle.setAttribute("stroke", "#0f271d");
          circle.setAttribute("stroke-width", "2.4");
        } else if (isLensRoot) {
          circle.setAttribute("stroke", "#8b3d00");
          circle.setAttribute("stroke-width", "2.6");
        } else if (inLensNode) {
          circle.setAttribute("stroke", "#2f6955");
          circle.setAttribute("stroke-width", "1.8");
        } else if (state.pinned.has(n.id)) {
          circle.setAttribute("stroke", "#2a0d2a");
          circle.setAttribute("stroke-width", "1.7");
        }

        circle.addEventListener("pointerdown", (ev) => startNodeDrag(ev, n.id));
        circle.addEventListener("click", (ev) => {
          ev.stopPropagation();
          handleNodePrimaryClick(n.id);
        });
        circle.addEventListener("dblclick", (ev) => {
          ev.stopPropagation();
          ev.preventDefault();
          handleNodeDoubleClick(n.id);
        });

        const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
        title.textContent = `${n.id}\nkind=${n.kind} layer=${n.layer || "-"} degree=${deg}`;
        g.appendChild(circle);
        g.appendChild(title);
        nodeG.appendChild(g);

        if (shouldLabel(n, display.nodes)) {
          const text = nodeLabelText(n);
          const textWidth = estimateLabelWidth(n) * 1.12;
          const placement = pickLabelPlacement(n, x, y, textWidth, placedLabelBoxes, mode);
          if (placement) {
            placedLabelBoxes.push(placement.box);
            const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
            t.setAttribute("x", String(placement.x));
            t.setAttribute("y", String(placement.y));
            t.setAttribute("class", "node-label");
            t.setAttribute("text-anchor", placement.anchor);
            t.textContent = text;
            nodeG.appendChild(t);
          }
        }
      }
      svg.appendChild(nodeG);

      if (!skipInspector) {
        renderInspector(display);
        renderOverlay(display);
      }
    }

    function expandOneHop(nodeId, dir) {
      if (!nodeId) return;
      const edges = dir === "out" ? (state.outgoing.get(nodeId) || []) : (state.incoming.get(nodeId) || []);
      for (const e of edges) {
        if (!isEdgeTypeEnabled(e.type)) continue;
        materializeNode(dir === "out" ? e.dst : e.src);
      }
      renderAll();
    }

    function moduleDeclPassesBaseFilters(node, includeGenerated = byId("showGenerated").checked) {
      if (!node || node.kind !== "decl") return false;
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
      if (!includeGenerated && node.generated === true) return false;
      if (byId("spineOnly").checked && !node.spine) return false;
      return true;
    }

    function moduleDescendantModules(moduleId, limit = 220) {
      const out = [];
      const seen = new Set([moduleId]);
      const queue = [moduleId];
      while (queue.length > 0 && out.length < limit) {
        const cur = queue.shift();
        for (const e of state.outgoing.get(cur) || []) {
          if (e.type !== "contains") continue;
          const childId = e.dst;
          if (!childId || seen.has(childId)) continue;
          const child = state.nodesById.get(childId);
          if (!child || child.kind !== "module") continue;
          seen.add(childId);
          out.push(childId);
          queue.push(childId);
          if (out.length >= limit) break;
        }
      }
      return out;
    }

    function moduleDeclCandidates(moduleId) {
      const rows = [];
      const seenDecl = new Set();
      const collectFromModule = (ownerModuleId) => {
        for (const e of state.incoming.get(ownerModuleId) || []) {
          if (e.type !== "decl_in_module") continue;
          const node = state.nodesById.get(e.src);
          if (!node || node.kind !== "decl") continue;
          if (seenDecl.has(node.id)) continue;
          if (!moduleDeclPassesBaseFilters(node)) continue;
          seenDecl.add(node.id);
          rows.push(node);
        }
      };

      collectFromModule(moduleId);
      if (rows.length === 0) {
        for (const childModuleId of moduleDescendantModules(moduleId)) {
          collectFromModule(childModuleId);
          if (rows.length >= 400) break;
        }
      }
      rows.sort((a, b) =>
        (b.spine ? 1 : 0) - (a.spine ? 1 : 0) ||
        degreeOf(b.id) - degreeOf(a.id) ||
        a.id.localeCompare(b.id)
      );
      return rows;
    }

    function syncExpandedModuleDecls() {
      for (const [moduleId, cursorRaw] of Array.from(state.moduleDeclCursor.entries())) {
        const requested = Math.max(0, Number(cursorRaw) || 0);
        if (!requested) continue;
        const candidates = moduleDeclCandidates(moduleId);
        const end = Math.min(requested, candidates.length);
        for (let i = 0; i < end; i += 1) {
          materializeNode(candidates[i].id);
        }
        state.moduleDeclCursor.set(moduleId, end);
      }
    }

    function moduleDeclProgress(moduleId) {
      const candidates = moduleDeclCandidates(moduleId);
      const candidateIds = new Set(candidates.map((n) => n.id));
      let visible = 0;
      for (const id of state.visible) {
        const node = state.nodesById.get(id);
        if (!node || node.kind !== "decl") continue;
        if (candidateIds.has(node.id)) visible += 1;
      }
      const cursor = Math.min(state.moduleDeclCursor.get(moduleId) || 0, candidates.length);
      return { total: candidates.length, visible, cursor };
    }

    function expandModuleDecls(moduleId, action = "reset") {
      if (!moduleId) return;
      if (byId("kindDecl") && !byId("kindDecl").checked) byId("kindDecl").checked = true;
      if (byId("edge_decl_in_module") && !byId("edge_decl_in_module").checked) {
        byId("edge_decl_in_module").checked = true;
      }
      const candidates = moduleDeclCandidates(moduleId);
      const previousCursor = Math.min(state.moduleDeclCursor.get(moduleId) || 0, candidates.length);
      const start = action === "more" ? previousCursor : 0;
      const end = Math.min(start + MODULE_DECL_PAGE_SIZE, candidates.length);
      if (action !== "more") {
        const candidateIds = new Set(candidates.map((n) => n.id));
        for (const id of Array.from(state.visible)) {
          const n = state.nodesById.get(id);
          if (!n || n.kind !== "decl") continue;
          if (candidateIds.has(id)) state.visible.delete(id);
        }
      }
      for (let i = start; i < end; i += 1) {
        materializeNode(candidates[i].id);
      }
      state.moduleDeclCursor.set(moduleId, end);
      if (end <= start) {
        setSourceHint(`module decl expansion exhausted for ${moduleId}`);
      } else {
        setSourceHint(`module decls loaded ${end}/${candidates.length} for ${moduleId}`);
      }
      renderAll();
    }

    function collapseModuleDecls(moduleId) {
      if (!moduleId) return;
      const candidates = moduleDeclCandidates(moduleId);
      const candidateIds = new Set(candidates.map((n) => n.id));
      for (const id of Array.from(state.visible)) {
        const n = state.nodesById.get(id);
        if (!n || n.kind !== "decl") continue;
        if (candidateIds.has(id)) {
          state.visible.delete(id);
        }
      }
      state.moduleDeclCursor.delete(moduleId);
      renderAll();
    }

    function togglePin(nodeId) {
      if (!nodeId) return;
      if (state.pinned.has(nodeId)) {
        const p = state.pinned.get(nodeId);
        state.pinned.delete(nodeId);
        if (p) state.freePos.set(nodeId, [p[0], p[1]]);
      } else {
        const p = state.lastPos.get(nodeId) || state.freePos.get(nodeId) || state.basePos.get(nodeId);
        if (p) {
          state.pinned.set(nodeId, [p[0], p[1]]);
          state.freePos.delete(nodeId);
        }
      }
    }

    function edgeTypeSummary(edges) {
      const m = new Map();
      for (const e of edges) {
        m.set(e.type, (m.get(e.type) || 0) + 1);
      }
      if (m.size === 0) return "none";
      return Array.from(m.entries()).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}:${v}`).join(" | ");
    }

    function renderNeighborBlock(title, rows) {
      if (!rows.length) {
        return `<div class="neighbors"><h3>${title}</h3><div class="neighbor-row">No neighbors under current filters.</div></div>`;
      }
      return `
        <div class="neighbors">
          <h3>${title}</h3>
          ${rows.map((r) => `
            <div class="neighbor-row" data-jump="${r.node.id}">
              <div><strong>${r.node.title || r.node.id}</strong></div>
              <div class="line2">
                <span class="badge">${r.edge.type}</span>
                <span class="badge">${r.node.kind}</span>
                <span class="badge">deg ${degreeOf(r.node.id)}</span>
              </div>
              <div><code>${r.node.id}</code></div>
            </div>
          `).join("")}
        </div>
      `;
    }

    function mathlibLensPathRows(node) {
      if (activeViewMode() !== "mathlib-lens") return [];
      if (!node || node.kind !== "module" || node.package === "mathlib") return [];
      const lens = activeMathlibLensConfig();
      const targets = [];
      const pushTarget = (id) => {
        if (typeof id !== "string" || !id) return;
        if (!state.nodesById.has(id)) return;
        const tNode = state.nodesById.get(id);
        if (!tNode || tNode.kind !== "module" || tNode.package !== "mathlib") return;
        if (targets.includes(id)) return;
        targets.push(id);
      };
      for (const id of lens.roots || []) pushTarget(id);
      for (const id of lens.hubs || []) pushTarget(id);
      for (const id of lens.aggregators || []) pushTarget(id);

      const rows = [];
      for (const target of targets.slice(0, 20)) {
        const path = shortestImportPath(node.id, target, 10);
        if (!path || path.length < 2) continue;
        rows.push({ target, path });
      }
      rows.sort((a, b) => a.path.length - b.path.length || a.target.localeCompare(b.target));
      return rows.slice(0, 6);
    }

    function mathlibDependencySummary(node) {
      if (!node || node.kind !== "module" || node.package === "mathlib") return null;
      const directMathlib = [];
      for (const edge of state.outgoing.get(node.id) || []) {
        if (!edge || edge.type !== "imports") continue;
        const dst = state.nodesById.get(edge.dst);
        if (!dst || dst.kind !== "module" || dst.package !== "mathlib") continue;
        directMathlib.push(dst.id);
      }
      directMathlib.sort((a, b) => degreeOf(b) - degreeOf(a) || a.localeCompare(b));

      const lens = activeMathlibLensConfig();
      const targets = [];
      const pushTarget = (id, kind) => {
        if (typeof id !== "string" || !id) return;
        if (!state.nodesById.has(id)) return;
        const dst = state.nodesById.get(id);
        if (!dst || dst.kind !== "module" || dst.package !== "mathlib") return;
        if (targets.some((row) => row.id === id)) return;
        targets.push({ id, kind });
      };
      for (const id of lens.hubs || []) pushTarget(id, "hub");
      for (const id of lens.aggregators || []) pushTarget(id, "agg");
      for (const id of lens.roots || []) pushTarget(id, "root");

      const reached = [];
      for (const row of targets.slice(0, 32)) {
        const path = shortestImportPath(node.id, row.id, 10);
        if (!path || path.length < 2) continue;
        reached.push({ id: row.id, kind: row.kind, hops: path.length - 1 });
      }
      reached.sort((a, b) => a.hops - b.hops || a.id.localeCompare(b.id));

      return {
        directMathlib: directMathlib.slice(0, 8),
        reachedTargets: reached.slice(0, 8),
      };
    }

    function renderInspector(display) {
      const box = byId("details");

      if (state.selectedEdge) {
        const e = state.selectedEdge;
        const edgeDomains = Array.isArray(e.domains) ? e.domains.join(", ") : "-";
        const crossDomain = e.cross_domain === true ? "true" : "false";
        box.innerHTML = `
          <div><strong>Selected edge</strong></div>
          <div>type: <code>${e.type}</code></div>
          <div>src: <code>${e.src}</code></div>
          <div>dst: <code>${e.dst}</code></div>
          <div>weight: <code>${e.weight || 1}</code></div>
          <div>domains: <code>${edgeDomains || "-"}</code></div>
          <div>cross_domain: <code>${crossDomain}</code></div>
        `;
        return;
      }

      let node = state.selected ? state.nodesById.get(state.selected) : null;
      if (!node && state.selected) {
        node = (display.nodes || []).find((n) => n.id === state.selected) || null;
      }
      if (!node) {
        box.innerHTML = [
          "<div>Please select a node or use search locate.</div>",
          "<div class='tiny'>Single click: inspect node. Double click: pin/unpin. Pinned nodes are locked and cannot be dragged.</div>",
        ].join("");
        return;
      }

      const outAll = (state.outgoing.get(node.id) || []).filter((e) => isEdgeTypeEnabled(e.type));
      const inAll = (state.incoming.get(node.id) || []).filter((e) => isEdgeTypeEnabled(e.type));
      const outRows = outAll
        .map((e) => ({ edge: e, node: state.nodesById.get(e.dst) }))
        .filter((x) => x.node)
        .slice(0, 18);
      const inRows = inAll
        .map((e) => ({ edge: e, node: state.nodesById.get(e.src) }))
        .filter((x) => x.node)
        .slice(0, 18);

      const pinText = state.pinned.has(node.id) ? "true" : "false";
      const declKind = node.decl_kind || "-";
      const generated = node.generated === true ? "true" : "false";
      const nodeDomains = Array.isArray(node.domains) ? node.domains : [];
      const domainText = nodeDomains.length ? nodeDomains.join(", ") : "-";
      const nodeMathTags = Array.isArray(node.math_tags) ? node.math_tags : [];
      const nodeAppliedTags = Array.isArray(node.applied_tags) ? node.applied_tags : [];
      const mathTagText = nodeMathTags.length ? nodeMathTags.join(", ") : "-";
      const appliedTagText = nodeAppliedTags.length ? nodeAppliedTags.join(", ") : "-";
      const usageCount = Number(node.usage_count || 0);
      const usageSuccessCount = Number(node.usage_success_count || 0);
      const usageLastUsed = typeof node.usage_last_used === "string" && node.usage_last_used
        ? node.usage_last_used
        : "-";
      const retrievalHitCount = Number(node.retrieval_hit_count || 0);
      const retrievalFinalHitCount = Number(node.retrieval_final_hit_count || 0);
      const retrievalLastQuery = typeof node.retrieval_last_query === "string" && node.retrieval_last_query
        ? node.retrieval_last_query
        : "-";
      const retrievalLastStage = typeof node.retrieval_last_stage === "string" && node.retrieval_last_stage
        ? node.retrieval_last_stage
        : "-";
      const retrievalLastSource = typeof node.retrieval_last_source === "string" && node.retrieval_last_source
        ? node.retrieval_last_source
        : "-";
      const retrievalLastSeen = typeof node.retrieval_last_seen === "string" && node.retrieval_last_seen
        ? node.retrieval_last_seen
        : "-";
      const activeDomain = byId("domainFilter").value;
      const activeProfile = activeDomain !== "all" ? state.domainProfiles.get(activeDomain) : null;
      const bridges = activeProfile && Array.isArray(activeProfile.bridge_modules)
        ? activeProfile.bridge_modules
        : [];
      const isBridge = bridges.includes(node.id) || (typeof node.module === "string" && bridges.includes(node.module));
      const otherDomains = activeDomain === "all"
        ? []
        : nodeDomains.filter((d) => d !== activeDomain);
      const bridgeHint = activeDomain === "all"
        ? "-"
        : (isBridge ? `bridge module for ${activeDomain}` : "not a bridge module");
      const crossHint = activeDomain === "all"
        ? "-"
        : (otherDomains.length ? `cross-domain -> ${otherDomains.join(", ")}` : "domain-local");
      const sourcePath = typeof node.path === "string" ? node.path : "";
      const isGroupNode = node && node.group === true;
      const moduleDeclInfo = (node.kind === "module" && !isGroupNode && state.nodesById.has(node.id))
        ? moduleDeclProgress(node.id)
        : null;
      const moduleParents = (node.kind === "module" && !isGroupNode)
        ? inAll
          .filter((e) => e.type === "contains")
          .map((e) => e.src)
          .filter((id, idx, arr) => typeof id === "string" && arr.indexOf(id) === idx)
          .slice(0, 6)
        : [];
      const moduleChildren = (node.kind === "module" && !isGroupNode)
        ? outAll
          .filter((e) => e.type === "contains")
          .map((e) => e.dst)
          .filter((id, idx, arr) => typeof id === "string" && arr.indexOf(id) === idx)
        : [];
      const groupMembers = Array.isArray(node.group_members) ? node.group_members : [];
      const lensState = state.importLens && typeof state.importLens === "object"
        ? state.importLens
        : {};
      const lensModeText = lensState.rootId ? String(lensState.mode || "deps") : "off";
      const lensRootText = lensState.rootId ? String(lensState.rootId) : "-";
      const lensNodeCount = lensState.nodes instanceof Set ? lensState.nodes.size : 0;
      const lensEdgeCount = lensState.edges instanceof Set ? lensState.edges.size : 0;
      const lensDepth = Number(lensState.depth || 0);
      const lensTruncated = lensState.truncated === true ? "true" : "false";
      const groupInfoLine = isGroupNode
        ? `<div>group summary: prefix <code>${node.group_prefix || node.title || "-"}</code> | members <code>${Number(node.group_member_count || groupMembers.length)}</code>${groupMembers.length ? ` (<code>${groupMembers.slice(0, 6).join(", ")}</code>${groupMembers.length > 6 ? " ..." : ""})` : ""}</div>`
        : "";
      const moduleHierarchyLine = (node.kind === "module" && !isGroupNode)
        ? `<div>contains hierarchy: parent <code>${moduleParents.length ? moduleParents.join(", ") : "-"}</code> | children <code>${moduleChildren.length}</code>${moduleChildren.length ? ` (<code>${moduleChildren.slice(0, 6).join(", ")}</code>${moduleChildren.length > 6 ? " ..." : ""})` : ""}</div>`
        : "";
      const moduleInfoLine = moduleDeclInfo
        ? `<div>module decls: visible <code>${moduleDeclInfo.visible}</code> | loaded <code>${moduleDeclInfo.cursor}</code>/<code>${moduleDeclInfo.total}</code></div>`
        : "";
      const moduleButtons = moduleDeclInfo
        ? `<button id="detailExpandModule">expand module decls (top ${MODULE_DECL_PAGE_SIZE})</button><button id="detailMoreModule" ${moduleDeclInfo.cursor < moduleDeclInfo.total ? "" : "disabled"}>more decls (+${MODULE_DECL_PAGE_SIZE})</button><button id="detailCollapseModule">collapse module decls</button>`
        : "";
      const lensButtons = (node.kind === "module" && !isGroupNode)
        ? `<button id="detailLensDeps">lens deps</button><button id="detailLensDependees">lens dependees</button><button id="detailLensBoth">lens both</button><button id="detailLensClear">clear lens</button>`
        : "";
      const lensPaths = mathlibLensPathRows(node);
      const mathlibSummary = mathlibDependencySummary(node);
      const mathlibSummaryBlock = mathlibSummary
        ? `<div><strong>Mathlib dependency summary</strong></div>
           <div>direct imports: <code>${mathlibSummary.directMathlib.length ? mathlibSummary.directMathlib.map((x) => compactModuleLabel(x)).join(", ") : "-"}</code></div>
           <div>reachable hubs/roots: <code>${mathlibSummary.reachedTargets.length ? mathlibSummary.reachedTargets.map((x) => `${compactModuleLabel(x.id)}(${x.kind},${x.hops}h)`).join(" | ") : "-"}</code></div>`
        : "";
      const lensPathBlock = lensPaths.length
        ? `<div><strong>Mathlib lens shortest paths</strong></div>
           <div class="tiny">Selected MLTheory module to active domain roots/hubs.</div>
           ${lensPaths.map((row) => `<div><code>${row.path.map((x) => compactModuleLabel(x)).join(" -> ")}</code></div>`).join("")}`
        : (activeViewMode() === "mathlib-lens" && node.kind === "module" && node.package !== "mathlib"
          ? `<div>Mathlib lens shortest paths: <code>none found under current lens targets</code></div>`
          : "");

      box.innerHTML = `
        <div><strong>${node.title || node.id}</strong></div>
        <div>id: <code>${node.id}</code></div>
        <div>kind: <code>${node.kind}</code> | layer: <code>${node.layer || "-"}</code> | package: <code>${node.package || "-"}</code></div>
        <div>group node: <code>${isGroupNode ? "true" : "false"}</code></div>
        <div>module: <code>${node.module || "-"}</code></div>
        <div>decl_kind: <code>${declKind}</code> | generated: <code>${generated}</code> | pinned: <code>${pinText}</code></div>
        <div>profiles: <code>${domainText}</code></div>
        <div>math tags: <code>${mathTagText}</code></div>
        <div>applied tags: <code>${appliedTagText}</code></div>
        <div>bridge hint: <code>${bridgeHint}</code></div>
        <div>cross-domain hint: <code>${crossHint}</code></div>
        <div>path: <code>${node.path || "-"}</code></div>
        <div>usage telemetry: count <code>${usageCount}</code> | success <code>${usageSuccessCount}</code> | last <code>${usageLastUsed}</code></div>
        <div>retrieval telemetry: hits <code>${retrievalHitCount}</code> | final_hits <code>${retrievalFinalHitCount}</code> | last <code>${retrievalLastSeen}</code></div>
        <div>retrieval source: <code>${retrievalLastSource}</code> | stage: <code>${retrievalLastStage}</code></div>
        <div>retrieval last query: <code>${retrievalLastQuery}</code></div>
        <div class="tiny">retrieval meaning: source=backend(local_index/rg_local/loogle_json/leanexplore/retrieval.query), stage=progressive widening stage.</div>
        <div>import lens: mode <code>${lensModeText}</code> | root <code>${lensRootText}</code> | nodes <code>${lensNodeCount}</code> | edges <code>${lensEdgeCount}</code> | depth <code>${lensDepth}</code> | truncated <code>${lensTruncated}</code></div>
        <div>degree: <code>${degreeOf(node.id)}</code></div>
        <div>outgoing: <code>${outAll.length}</code> (${edgeTypeSummary(outAll)})</div>
        <div>incoming: <code>${inAll.length}</code> (${edgeTypeSummary(inAll)})</div>
        ${groupInfoLine}
        ${moduleHierarchyLine}
        ${moduleInfoLine}
        ${mathlibSummaryBlock}
        ${lensPathBlock}
        <div style="margin-top:8px;">
          <button id="detailExpandOut">expand outgoing 1-hop</button>
          <button id="detailExpandIn">expand incoming 1-hop</button>
          <button id="detailTogglePin">toggle pin</button>
          <button id="detailUnpin">unpin selected</button>
          ${sourcePath ? '<button id="detailCopyPath">copy source path</button><button id="detailOpenSource">open source</button>' : ""}
          ${moduleButtons}
          ${lensButtons}
        </div>
        ${renderNeighborBlock("Outgoing neighbors", outRows)}
        ${renderNeighborBlock("Incoming neighbors", inRows)}
      `;

      byId("detailExpandOut").onclick = () => expandOneHop(node.id, "out");
      byId("detailExpandIn").onclick = () => expandOneHop(node.id, "in");
      byId("detailTogglePin").onclick = () => {
        togglePin(node.id);
        renderAll();
      };
      byId("detailUnpin").onclick = () => {
        state.pinned.delete(node.id);
        renderAll();
      };

      const copyPathBtn = byId("detailCopyPath");
      if (copyPathBtn) {
        copyPathBtn.onclick = async () => {
          const ok = await copyTextToClipboard(sourcePath);
          setSourceHint(ok ? `path copied: ${sourcePath}` : "path copy failed");
        };
      }
      const openPathBtn = byId("detailOpenSource");
      if (openPathBtn) {
        openPathBtn.onclick = () => {
          const target = sourcePath.startsWith("/")
            ? `file://${sourcePath}`
            : sourcePath;
          window.open(target, "_blank", "noopener");
          setSourceHint(`open requested: ${sourcePath}`);
        };
      }

      const expandModule = byId("detailExpandModule");
      if (expandModule) expandModule.onclick = () => expandModuleDecls(node.id, "reset");

      const moreModule = byId("detailMoreModule");
      if (moreModule) moreModule.onclick = () => expandModuleDecls(node.id, "more");

      const collapseModule = byId("detailCollapseModule");
      if (collapseModule) collapseModule.onclick = () => collapseModuleDecls(node.id);

      const lensDeps = byId("detailLensDeps");
      if (lensDeps) {
        lensDeps.onclick = () => {
          setImportLens(node.id, "deps");
          setSourceHint(`import lens deps: ${node.id}`);
          renderAll();
        };
      }
      const lensDependees = byId("detailLensDependees");
      if (lensDependees) {
        lensDependees.onclick = () => {
          setImportLens(node.id, "dependees");
          setSourceHint(`import lens dependees: ${node.id}`);
          renderAll();
        };
      }
      const lensBoth = byId("detailLensBoth");
      if (lensBoth) {
        lensBoth.onclick = () => {
          setImportLens(node.id, "both");
          setSourceHint(`import lens both: ${node.id}`);
          renderAll();
        };
      }
      const lensClear = byId("detailLensClear");
      if (lensClear) {
        lensClear.onclick = () => {
          clearImportLens();
          setSourceHint("import lens cleared");
          renderAll();
        };
      }

      box.querySelectorAll("[data-jump]").forEach((el) => {
        el.onclick = () => {
          const id = el.getAttribute("data-jump");
          if (!id) return;
          selectAndFocus(id);
        };
      });
    }

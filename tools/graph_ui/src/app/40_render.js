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

    function renderGraph(display, skipInspector = false) {
      state.lastDisplay = display;
      computeLayout(display.nodes);
      state.lastPos = new Map();

      svg.innerHTML = "";
      normalizeViewToViewport(state.view.x + state.view.w / 2, state.view.y + state.view.h / 2, 0.5, 0.5);
      applyViewBox();

      const displayed = new Set(display.nodes.map((n) => n.id));
      const edges = display.edges.filter((e) => displayed.has(e.src) && displayed.has(e.dst));
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
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", String(a[0]));
        line.setAttribute("y1", String(a[1]));
        line.setAttribute("x2", String(b[0]));
        line.setAttribute("y2", String(b[1]));
        line.setAttribute("class", "edge");
        line.setAttribute("stroke", edgeColor(e.type));
        line.setAttribute("stroke-opacity", state.selectedEdge === e ? "0.96" : "0.38");
        line.setAttribute("stroke-width", state.selectedEdge === e ? "2.8" : String(1 + Math.log2((e.weight || 1) + 1) * 0.65));
        line.addEventListener("click", (ev) => {
          ev.stopPropagation();
          state.selectedEdge = e;
          state.selected = null;
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
        circle.setAttribute("fill-opacity", state.selected === n.id ? "1" : "0.92");
        circle.style.cursor = "pointer";

        if (state.selected === n.id) {
          circle.setAttribute("stroke", "#0f271d");
          circle.setAttribute("stroke-width", "2.4");
        } else if (state.pinned.has(n.id)) {
          circle.setAttribute("stroke", "#2a0d2a");
          circle.setAttribute("stroke-width", "1.7");
        }

        circle.addEventListener("pointerdown", (ev) => startNodeDrag(ev, n.id));
        circle.addEventListener("click", (ev) => {
          ev.stopPropagation();
          if (Date.now() < state.suppressClickUntil) return;
          state.selected = n.id;
          state.selectedEdge = null;
          materializeNode(n.id);
          renderAll();
        });

        circle.addEventListener("dblclick", (ev) => {
          ev.preventDefault();
          ev.stopPropagation();
          if (Date.now() < state.suppressClickUntil) return;
          togglePin(n.id);
          state.selected = n.id;
          state.selectedEdge = null;
          materializeNode(n.id);
          renderAll();
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

    function expandModuleDecls(moduleId) {
      if (!moduleId) return;
      for (const e of state.incoming.get(moduleId) || []) {
        if (e.type === "decl_in_module") {
          materializeNode(e.src);
        }
      }
      renderAll();
    }

    function collapseModuleDecls(moduleId) {
      if (!moduleId) return;
      for (const id of Array.from(state.visible)) {
        const n = state.nodesById.get(id);
        if (!n || n.kind !== "decl") continue;
        if (n.module === moduleId) {
          state.visible.delete(id);
        }
      }
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

      box.innerHTML = `
        <div><strong>${node.title || node.id}</strong></div>
        <div>id: <code>${node.id}</code></div>
        <div>kind: <code>${node.kind}</code> | layer: <code>${node.layer || "-"}</code> | package: <code>${node.package || "-"}</code></div>
        <div>module: <code>${node.module || "-"}</code></div>
        <div>decl_kind: <code>${declKind}</code> | generated: <code>${generated}</code> | pinned: <code>${pinText}</code></div>
        <div>domains: <code>${domainText}</code></div>
        <div>bridge hint: <code>${bridgeHint}</code></div>
        <div>cross-domain hint: <code>${crossHint}</code></div>
        <div>path: <code>${node.path || "-"}</code></div>
        <div>degree: <code>${degreeOf(node.id)}</code></div>
        <div>outgoing: <code>${outAll.length}</code> (${edgeTypeSummary(outAll)})</div>
        <div>incoming: <code>${inAll.length}</code> (${edgeTypeSummary(inAll)})</div>
        <div style="margin-top:8px;">
          <button id="detailExpandOut">expand outgoing 1-hop</button>
          <button id="detailExpandIn">expand incoming 1-hop</button>
          <button id="detailTogglePin">toggle pin</button>
          <button id="detailUnpin">unpin selected</button>
          ${sourcePath ? '<button id="detailCopyPath">copy source path</button><button id="detailOpenSource">open source</button>' : ""}
          ${node.kind === "module" ? '<button id="detailExpandModule">expand module decls</button><button id="detailCollapseModule">collapse module decls</button>' : ""}
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
      if (expandModule) expandModule.onclick = () => expandModuleDecls(node.id);

      const collapseModule = byId("detailCollapseModule");
      if (collapseModule) collapseModule.onclick = () => collapseModuleDecls(node.id);

      box.querySelectorAll("[data-jump]").forEach((el) => {
        el.onclick = () => {
          const id = el.getAttribute("data-jump");
          if (!id) return;
          selectAndFocus(id);
        };
      });
    }


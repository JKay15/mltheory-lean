    function renderOverlay(display) {
      const edgeType = state.selectedEdge ? state.selectedEdge.type : "-";
      const activeDomain = byId("domainFilter").value;
      const mode = activeViewMode();
      const layout = byId("layoutMode").value || "layered";
      const maxEdges = Number(byId("maxEdges").value || "5000");
      byId("overlay").innerHTML = [
        `<div><strong>visible</strong> nodes: <code>${display.nodes.length}</code>, edges: <code>${display.edges.length}</code></div>`,
        `<div>selected node: <code>${state.selected || "(none)"}</code></div>`,
        `<div>selected edge type: <code>${edgeType}</code></div>`,
        `<div>active domain: <code>${activeDomain}</code></div>`,
        `<div>zoom: <code>${(state.world.w / state.view.w).toFixed(2)}x</code> | pin count: <code>${state.pinned.size}</code></div>`,
        `<div>layout: <code>${layout}</code> | maxEdges: <code>${maxEdges}</code>${state.edgeCapApplied ? " (capped)" : ""}</div>`,
      ].join("");

      byId("statsBox").innerHTML = [
        `<div>Total graph: nodes <code>${state.nodesById.size}</code>, edges <code>${state.edges.length}</code></div>`,
        `<div>Visible window: nodes <code>${display.nodes.length}</code>, edges <code>${display.edges.length}</code></div>`,
        `<div>Mode: <code>${modeTitle(mode)}</code></div>`,
        mode === "decl-neighborhood"
          ? `<div>Neighborhood center: <code>${state.selected || defaultNeighborhoodCenterId() || "(none)"}</code> | depth: <code>${byId("neighborhoodDepth").value}</code></div>`
          : "",
      ].join("");
    }

    function renderSearchResults() {
      const query = byId("search").value.trim().toLowerCase();
      const box = byId("searchResults");

      if (!query) {
        box.innerHTML = "<div class='tiny'>Type in search box to see locate candidates.</div>";
        state.searchMatches = [];
        return;
      }

      const rows = [];
      for (const node of state.nodesById.values()) {
        const hay = [node.id, node.title || "", node.module || "", node.path || ""].join(" ").toLowerCase();
        const idx = hay.indexOf(query);
        if (idx < 0) continue;
        const titleMatch = (node.title || "").toLowerCase().startsWith(query);
        rows.push({
          node,
          score: idx + (node.id.toLowerCase().startsWith(query) ? -10 : 0) + (titleMatch ? -5 : 0),
        });
      }

      rows.sort((a, b) => a.score - b.score || degreeOf(b.node.id) - degreeOf(a.node.id) || a.node.id.localeCompare(b.node.id));
      state.searchMatches = rows.slice(0, 60).map((r) => r.node);

      if (!state.searchMatches.length) {
        box.innerHTML = "<div class='tiny'>No matches.</div>";
        return;
      }

      box.innerHTML = state.searchMatches.slice(0, 24).map((node) => {
        const active = state.selected === node.id ? " active" : "";
        return `
          <div class="node-item${active}" data-match="${node.id}">
            <div><strong>${node.title || node.id}</strong></div>
            <div class="line2"><span class="badge">${node.kind}</span><span class="badge">deg ${degreeOf(node.id)}</span></div>
            <div class="line2"><code>${node.id}</code></div>
          </div>
        `;
      }).join("");

      box.querySelectorAll("[data-match]").forEach((el) => {
        el.onclick = () => {
          const id = el.getAttribute("data-match");
          if (!id) return;
          selectAndFocus(id);
        };
      });
    }

    function selectAndFocus(id) {
      materializeNode(id);
      state.selected = id;
      state.selectedEdge = null;
      renderAll();
      centerOnNode(id);
    }

    function locateFirstMatch() {
      if (!state.searchMatches.length) {
        renderSearchResults();
      }
      if (!state.searchMatches.length) return;
      selectAndFocus(state.searchMatches[0].id);
    }

    function fitViewToDisplay() {
      const ids = state.lastDisplay.nodes.map((n) => n.id).filter((id) => state.lastPos.has(id));
      if (!ids.length) return;

      let minX = Infinity;
      let minY = Infinity;
      let maxX = -Infinity;
      let maxY = -Infinity;

      for (const id of ids) {
        const node = state.nodesById.get(id);
        const [x, y] = state.lastPos.get(id);
        const deg = degreeOf(id);
        const base = !node ? 6 : (node.kind === "module" ? 7 : (node.kind === "concept" ? 8 : 4.5));
        const r = Math.min(15, base + Math.log2(deg + 1) * 1.15);
        const labelW = node ? estimateLabelWidth(node) : 0;
        const labelPadX = node && (node.kind === "module" || node.kind === "concept")
          ? labelW * 0.62
          : labelW * 0.3;
        const labelPadY = node && shouldLabel(node, state.lastDisplay.nodes) ? 20 : 8;
        minX = Math.min(minX, x - r - labelPadX - 6);
        minY = Math.min(minY, y - r - labelPadY - 6);
        maxX = Math.max(maxX, x + r + labelPadX + 6);
        maxY = Math.max(maxY, y + r + labelPadY + 6);
      }

      const pad = 90;
      const w = clamp(maxX - minX + pad * 2, 240, state.world.w * 3.2);
      const h = clamp(maxY - minY + pad * 2, 180, state.world.h * 3.2);
      state.view.w = w;
      state.view.h = h;
      normalizeViewToViewport((minX + maxX) / 2, (minY + maxY) / 2, 0.5, 0.5);
      applyViewBox();
      renderOverlay(state.lastDisplay);
    }

    function centerOnNode(nodeId) {
      const p = state.lastPos.get(nodeId);
      if (!p) return;
      normalizeViewToViewport(p[0], p[1], 0.5, 0.5);
      applyViewBox();
      renderOverlay(state.lastDisplay);
    }

    async function copyTextToClipboard(text) {
      if (!text) return false;
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(text);
          return true;
        }
      } catch (_) {}
      try {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        const ok = document.execCommand("copy");
        document.body.removeChild(ta);
        return ok;
      } catch (_) {
        return false;
      }
    }

    function saveLayoutToStorage() {
      try {
        const positions = {};
        for (const [id, p] of state.lastPos.entries()) {
          positions[id] = [Number(p[0]), Number(p[1])];
        }
        const payload = {
          version: 1,
          saved_at: new Date().toISOString(),
          mode: activeViewMode(),
          selected: state.selected,
          view: {
            x: Number(state.view.x),
            y: Number(state.view.y),
            w: Number(state.view.w),
            h: Number(state.view.h),
          },
          positions,
        };
        localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(payload));
        setSourceHint(`layout saved (${Object.keys(positions).length} nodes)`);
      } catch (err) {
        setSourceHint(`layout save failed: ${String(err)}`);
      }
    }

    function loadLayoutFromStorage() {
      try {
        const raw = localStorage.getItem(LAYOUT_STORAGE_KEY);
        if (!raw) {
          setSourceHint("no saved layout");
          return;
        }
        const payload = JSON.parse(raw);
        if (!payload || typeof payload !== "object") {
          setSourceHint("saved layout is invalid");
          return;
        }

        if (typeof payload.mode === "string" && byId("viewMode")) {
          byId("viewMode").value = payload.mode;
        }
        if (payload.view && typeof payload.view === "object") {
          const v = payload.view;
          if ([v.x, v.y, v.w, v.h].every((n) => typeof n === "number" && Number.isFinite(n))) {
            state.view = { x: v.x, y: v.y, w: v.w, h: v.h };
            clampView();
          }
        }

        state.pinned.clear();
        const positions = payload.positions && typeof payload.positions === "object"
          ? payload.positions
          : {};
        for (const [id, p] of Object.entries(positions)) {
          if (!Array.isArray(p) || p.length !== 2) continue;
          if (!state.nodesById.has(id)) continue;
          const x = Number(p[0]);
          const y = Number(p[1]);
          if (!Number.isFinite(x) || !Number.isFinite(y)) continue;
          state.pinned.set(id, [x, y]);
        }

        if (typeof payload.selected === "string" && state.nodesById.has(payload.selected)) {
          state.selected = payload.selected;
          materializeNode(payload.selected);
        }

        renderAll();
        applyViewBox();
        setSourceHint(`layout loaded (${state.pinned.size} pinned)`);
      } catch (err) {
        setSourceHint(`layout load failed: ${String(err)}`);
      }
    }

    function clearSavedLayout() {
      localStorage.removeItem(LAYOUT_STORAGE_KEY);
      setSourceHint("saved layout cleared");
    }

    function screenToSvgDelta(dxPx, dyPx) {
      const rect = svg.getBoundingClientRect();
      return {
        dx: (dxPx * state.view.w) / Math.max(rect.width, 1),
        dy: (dyPx * state.view.h) / Math.max(rect.height, 1),
      };
    }

    function startNodeDrag(ev, nodeId) {
      ev.stopPropagation();
      if (state.pinned.has(nodeId)) return;
      const p = nodePos(nodeId);
      state.drag = {
        type: "node",
        nodeId,
        pointerId: ev.pointerId,
        startClientX: ev.clientX,
        startClientY: ev.clientY,
        startNodeX: p[0],
        startNodeY: p[1],
        moved: false,
      };
      svg.classList.add("panning");
      svg.setPointerCapture(ev.pointerId);
      ev.preventDefault();
    }

    function startPan(ev) {
      state.drag = {
        type: "pan",
        pointerId: ev.pointerId,
        startClientX: ev.clientX,
        startClientY: ev.clientY,
        startViewX: state.view.x,
        startViewY: state.view.y,
      };
      svg.classList.add("panning");
      svg.setPointerCapture(ev.pointerId);
      ev.preventDefault();
    }

    function scheduleGraphRender() {
      if (state.rafPending) return;
      state.rafPending = true;
      requestAnimationFrame(() => {
        state.rafPending = false;
        renderGraph(state.lastDisplay, true);
      });
    }

    function onPointerMove(ev) {
      if (!state.drag) return;
      if (state.drag.pointerId !== ev.pointerId) return;

      const delta = screenToSvgDelta(ev.clientX - state.drag.startClientX, ev.clientY - state.drag.startClientY);

      if (state.drag.type === "pan") {
        state.view.x = state.drag.startViewX - delta.dx;
        state.view.y = state.drag.startViewY - delta.dy;
        clampView();
        applyViewBox();
        renderOverlay(state.lastDisplay);
        return;
      }

      if (state.drag.type === "node") {
        if (Math.abs(delta.dx) <= 0.8 && Math.abs(delta.dy) <= 0.8 && !state.drag.moved) return;
        const nx = state.drag.startNodeX + delta.dx;
        const ny = state.drag.startNodeY + delta.dy;
        state.drag.moved = true;
        state.freePos.set(state.drag.nodeId, [nx, ny]);
        state.suppressClickUntil = Date.now() + 180;
        scheduleGraphRender();
      }
    }

    function onPointerUp(ev) {
      if (!state.drag || state.drag.pointerId !== ev.pointerId) return;
      svg.classList.remove("panning");
      svg.releasePointerCapture(ev.pointerId);
      const dragState = state.drag;
      const wasNodeDrag = dragState.type === "node";
      state.drag = null;
      if (wasNodeDrag) {
        if (dragState.moved) renderAll();
      }
    }

    function onWheel(ev) {
      ev.preventDefault();
      const rect = svg.getBoundingClientRect();
      const px = (ev.clientX - rect.left) / Math.max(rect.width, 1);
      const py = (ev.clientY - rect.top) / Math.max(rect.height, 1);
      const anchorX = state.view.x + px * state.view.w;
      const anchorY = state.view.y + py * state.view.h;

      const factor = Math.exp(ev.deltaY * 0.0012);
      const newW = clamp(state.view.w * factor, 220, state.world.w * 4.2);
      const newH = clamp(state.view.h * factor, 160, state.world.h * 4.2);

      state.view.w = newW;
      state.view.h = newH;
      normalizeViewToViewport(anchorX, anchorY, px, py);
      applyViewBox();
      renderOverlay(state.lastDisplay);
    }

    function renderAll() {
      const display = collectDisplayGraph();
      renderGraph(display, false);
      renderSearchResults();
    }

    function wireControls() {
      const rerenderIds = [
        "scope", "layerFilter", "domainFilter", "kindModule", "kindDecl", "kindConcept", "spineOnly",
        "edge_imports", "edge_uses_type", "edge_uses_value", "edge_decl_in_module", "edge_binds",
        "edge_alias_of", "edge_used_recently",
        "showGenerated", "expandMathlib", "maxNodes", "maxEdges", "neighborhoodDepth", "layoutMode",
      ];
      for (const id of rerenderIds) {
        const el = byId(id);
        if (!el) continue;
        el.addEventListener("change", () => renderAll());
      }

      byId("viewMode").addEventListener("change", () => {
        const mode = activeViewMode();
        if (mode === "decl-neighborhood") {
          byId("kindDecl").checked = true;
          byId("kindModule").checked = true;
          byId("edge_uses_value").checked = true;
        }
        if (mode === "concept-browser") {
          byId("kindConcept").checked = true;
          byId("edge_binds").checked = true;
        }
        if (mode === "module-map" && state.visible.size === 0) {
          resetToModuleMap();
        }
        renderAll();
        fitViewToDisplay();
      });

      byId("search").addEventListener("input", () => renderSearchResults());
      byId("search").addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") {
          ev.preventDefault();
          locateFirstMatch();
        }
      });

      byId("locateBtn").onclick = () => locateFirstMatch();
      byId("clearSearch").onclick = () => {
        byId("search").value = "";
        renderSearchResults();
      };

      byId("resetMap").onclick = () => {
        byId("viewMode").value = "module-map";
        resetToModuleMap();
        renderAll();
        fitViewToDisplay();
      };

      byId("fitView").onclick = () => fitViewToDisplay();

      byId("clearPins").onclick = () => {
        state.pinned.clear();
        renderAll();
      };
      byId("saveLayout").onclick = () => saveLayoutToStorage();
      byId("loadLayout").onclick = () => loadLayoutFromStorage();
      byId("clearLayout").onclick = () => clearSavedLayout();

      svg.addEventListener("pointerdown", (ev) => {
        if (ev.button !== 0) return;
        state.selectedEdge = null;
        startPan(ev);
      });
      svg.addEventListener("pointermove", onPointerMove);
      svg.addEventListener("pointerup", onPointerUp);
      svg.addEventListener("pointercancel", onPointerUp);
      svg.addEventListener("wheel", onWheel, { passive: false });
      window.addEventListener("resize", () => {
        if (!state.lastDisplay || !Array.isArray(state.lastDisplay.nodes) || state.lastDisplay.nodes.length === 0) return;
        normalizeViewToViewport(state.view.x + state.view.w / 2, state.view.y + state.view.h / 2, 0.5, 0.5);
        applyViewBox();
        renderOverlay(state.lastDisplay);
      });

      svg.addEventListener("click", (ev) => {
        if (ev.target === svg && Date.now() >= state.suppressClickUntil) {
          state.selected = null;
          state.selectedEdge = null;
          renderInspector(state.lastDisplay);
          renderOverlay(state.lastDisplay);
        }
      });
    }

    async function boot() {
      try {
        state.graph = await loadData();
        buildIndex();
        initDomainFilter();
        resetToModuleMap();
        wireControls();
        renderAll();
        fitViewToDisplay();
      } catch (err) {
        byId("statsBox").textContent = String(err);
        byId("overlay").textContent = "failed to load graph";
        byId("details").textContent = String(err);
      }
    }

    boot();

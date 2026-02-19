    function savePanelUIState() {
      try {
        localStorage.setItem(PANEL_UI_STORAGE_KEY, JSON.stringify(state.panelUI));
      } catch (_) {}
    }

    function loadPanelUIState() {
      try {
        const raw = localStorage.getItem(PANEL_UI_STORAGE_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (!parsed || typeof parsed !== "object") return;
        if (typeof parsed.overlayCollapsed === "boolean") {
          state.panelUI.overlayCollapsed = parsed.overlayCollapsed;
        }
        if (typeof parsed.statsCollapsed === "boolean") {
          state.panelUI.statsCollapsed = parsed.statsCollapsed;
        }
      } catch (_) {}
    }

    function applyPanelUIState() {
      const overlay = byId("overlay");
      const stats = byId("statsBox");
      if (overlay) overlay.classList.toggle("is-hidden", state.panelUI.overlayCollapsed);
      if (stats) stats.classList.toggle("is-hidden", state.panelUI.statsCollapsed);

      const toggleOverlay = byId("toggleOverlay");
      if (toggleOverlay) {
        toggleOverlay.textContent = state.panelUI.overlayCollapsed ? "show visible panel" : "hide visible panel";
      }
      const toggleStats = byId("toggleStats");
      if (toggleStats) {
        toggleStats.textContent = state.panelUI.statsCollapsed ? "show stats" : "hide stats";
      }
    }

    function renderOverlay(display) {
      const countKinds = (nodes) => {
        let modules = 0;
        let decls = 0;
        let concepts = 0;
        for (const node of nodes) {
          if (node.kind === "module") modules += 1;
          else if (node.kind === "decl") decls += 1;
          else if (node.kind === "concept") concepts += 1;
        }
        return { modules, decls, concepts };
      };
      const nodePassesIgnoring = (node, opts = {}) => {
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
        if (!opts.ignoreGenerated && node.kind === "decl" && !byId("showGenerated").checked && node.generated === true) {
          return false;
        }
        if (!opts.ignoreSpine && byId("spineOnly").checked) {
          if (!(activeViewMode() === "module-map" && node.kind === "module") && !node.spine) return false;
        }
        return true;
      };

      const edgeType = state.selectedEdge ? state.selectedEdge.type : "-";
      const activeProfile = byId("domainFilter").value;
      const activeMathTag = activeAxisTagToken("math");
      const activeAppliedTag = activeAxisTagToken("applied");
      const activeProofMap = state.activeProofMapId || "off";
      const activeDataset = state.activeDatasetId || "latest";
      const activeTreeFocus = state.treeFocusRoot || "off";
      const mode = activeViewMode();
      const layout = byId("layoutMode").value || "layered";
      const maxNodes = Number(byId("maxNodes").value || "500");
      const maxEdges = Number(byId("maxEdges").value || "5000");
      const meta = state.collectMeta || {};
      const groupDepth = Number(meta.groupDepth || 0);
      const groupedModules = Number(meta.groupedModuleCount || 0);
      const groupNodeCount = Number(meta.groupNodeCount || 0);
      const groupToken = groupDepth > 0 ? `L${groupDepth}` : "off";
      const scope = byId("scope").value;
      const spineOnly = byId("spineOnly").checked;
      const showGenerated = byId("showGenerated").checked;
      const expandMathlib = byId("expandMathlib").checked;
      const wheelMode = byId("wheelMode") ? byId("wheelMode").value : "smart";
      const visibleKinds = countKinds(display.nodes);
      const lensState = state.importLens && typeof state.importLens === "object"
        ? state.importLens
        : {};
      const lensMode = lensState.rootId ? String(lensState.mode || "deps") : "off";
      const lensRoot = lensState.rootId ? String(lensState.rootId) : "-";
      const lensToken = lensMode === "off" ? "off" : `${lensMode}@${lensRoot}`;

      let suppressedBySpine = 0;
      if (spineOnly) {
        for (const node of state.nodesById.values()) {
          if (nodePassesIgnoring(node, { ignoreSpine: true }) && !nodePassesIgnoring(node)) {
            suppressedBySpine += 1;
          }
        }
      }

      let hiddenGeneratedDecls = 0;
      if (!showGenerated && byId("kindDecl").checked) {
        for (const node of state.nodesById.values()) {
          if (node.kind !== "decl" || node.generated !== true) continue;
          if (nodePassesIgnoring(node, { ignoreGenerated: true })) {
            hiddenGeneratedDecls += 1;
          }
        }
      }

      let hiddenByExpansion = 0;
      if (mode === "module-map" && byId("kindDecl").checked && (meta.hiddenByNodeCap || 0) === 0) {
        for (const node of state.nodesById.values()) {
          if (node.kind !== "decl") continue;
          if (!nodePassesFilters(node)) continue;
          if (!state.visible.has(node.id)) hiddenByExpansion += 1;
        }
      }

      const reasons = [];
      if (suppressedBySpine > 0) {
        reasons.push(`${suppressedBySpine} nodes hidden by spineOnly.`);
      }
      if (hiddenGeneratedDecls > 0) {
        reasons.push(`${hiddenGeneratedDecls} generated decls hidden because showGenerated=false.`);
      }
      if ((meta.hiddenByNodeCap || 0) > 0) {
        reasons.push(`${meta.hiddenByNodeCap} nodes omitted by maxNodes=${maxNodes}.`);
      }
      if ((meta.hiddenByEdgeCap || 0) > 0) {
        reasons.push(`${meta.hiddenByEdgeCap} edges omitted by maxEdges=${maxEdges}.`);
      }
      if ((meta.collapsedMathlibModules || 0) > 0) {
        reasons.push(`${meta.collapsedMathlibModules} mathlib modules collapsed (expandMathlib=false).`);
      }
      if (groupDepth > 0 && groupNodeCount > 0) {
        reasons.push(`${groupedModules} modules aggregated into ${groupNodeCount} group nodes (namespace L${groupDepth}).`);
      }
      if (hiddenByExpansion > 0) {
        reasons.push(`${hiddenByExpansion} decl nodes not materialized yet; use \"expand module decls\".`);
      }
      if (display.nodes.length === 0) {
        reasons.push("No visible nodes under current scope/profile/math/applied/kind filters.");
      }
      if (state.activeProofMapId && display.nodes.length === 0) {
        reasons.push(`proof map ${state.activeProofMapId} is active and filtered everything out.`);
      }
      if (state.treeFocusRoot && display.nodes.length === 0) {
        reasons.push(`subtree focus ${state.treeFocusRoot} filtered everything out.`);
      }
      if (lensMode !== "off" && lensState.truncated === true) {
        reasons.push(`import lens traversal truncated at depth=${Number(lensState.depth || 0)}.`);
      }

      const usageMeta = state.graph && typeof state.graph === "object" && state.graph.usage
        ? state.graph.usage
        : {};
      const retrievalMeta = state.graph && typeof state.graph === "object" && state.graph.retrieval
        ? state.graph.retrieval
        : {};
      const usageEventCount = Number(usageMeta.event_count || 0);
      const retrievalEventCount = Number(retrievalMeta.event_count || 0);
      const formatTopNodes = (rows, countKey) => {
        if (!Array.isArray(rows) || rows.length === 0) return "none";
        return rows.slice(0, 4).map((row) => {
          const id = typeof row.id === "string" ? row.id : "(unknown)";
          const count = Number(row[countKey] || 0);
          const label = nodeLabelText({ id, kind: "decl", title: id.split(".").pop() || id });
          return `${label}:${count}`;
        }).join(" | ");
      };
      const topUsedText = formatTopNodes(usageMeta.top_used || [], "usage_count");
      const topRetrievalText = formatTopNodes(retrievalMeta.top_hits || [], "retrieval_hit_count");

      byId("overlay").innerHTML = [
        `<div><strong>visible</strong> nodes: <code>${display.nodes.length}</code>, edges: <code>${display.edges.length}</code></div>`,
        `<div>visible by kind: module <code>${visibleKinds.modules}</code> | decl <code>${visibleKinds.decls}</code> | concept <code>${visibleKinds.concepts}</code></div>`,
        `<div>filters: dataset=<code>${activeDataset}</code> scope=<code>${scope}</code> profile=<code>${activeProfile}</code> math=<code>${activeMathTag}</code> applied=<code>${activeAppliedTag}</code> proofMap=<code>${activeProofMap}</code> tree=<code>${activeTreeFocus}</code> group=<code>${groupToken}</code> importLens=<code>${lensToken}</code> spineOnly=<code>${spineOnly}</code> generated=<code>${showGenerated}</code> expandMathlib=<code>${expandMathlib}</code> wheelMode=<code>${wheelMode}</code></div>`,
        `<div>caps: maxNodes=<code>${maxNodes}</code> maxEdges=<code>${maxEdges}</code></div>`,
        `<div>selected node: <code>${state.selected || "(none)"}</code></div>`,
        `<div>selected edge type: <code>${edgeType}</code></div>`,
        `<div>zoom: <code>${(state.world.w / state.view.w).toFixed(2)}x</code> | pin count: <code>${state.pinned.size}</code></div>`,
        `<div>layout: <code>${layout}</code>${state.edgeCapApplied ? " | edge cap active" : ""}</div>`,
        `<div>recent used: events <code>${usageEventCount}</code> | top <code>${topUsedText}</code></div>`,
        `<div>recent retrieval: events <code>${retrievalEventCount}</code> | top <code>${topRetrievalText}</code></div>`,
        `<div>why missing: ${reasons.length ? reasons.map((r) => `<code>${r}</code>`).join(" ") : "<code>none</code>"}</div>`,
      ].join("");

      byId("statsBox").innerHTML = [
        `<div>Total graph: nodes <code>${state.nodesById.size}</code>, edges <code>${state.edges.length}</code></div>`,
        `<div>Visible window: nodes <code>${display.nodes.length}</code>, edges <code>${display.edges.length}</code></div>`,
        `<div>Collection stats: ranked <code>${meta.rankedNodeCount || 0}</code>, raw edges <code>${meta.rawEdgeCount || 0}</code>, mode <code>${mode}</code>, grouped modules <code>${groupedModules}</code> -> groups <code>${groupNodeCount}</code></div>`,
        `<div>Telemetry: usage events <code>${usageEventCount}</code> | retrieval events <code>${retrievalEventCount}</code></div>`,
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

    function namespaceTreeRows(maxRows = 700) {
      const tree = state.namespaceTree || {};
      const roots = Array.isArray(tree.roots) ? tree.roots : [];
      const children = tree.children instanceof Map ? tree.children : new Map();
      if (roots.length === 0) return [];

      const rows = [];
      const walk = (moduleId, depth) => {
        if (!moduleId || rows.length >= maxRows) return;
        const kids = children.get(moduleId) || [];
        const expanded = state.treeExpanded instanceof Set && state.treeExpanded.has(moduleId);
        rows.push({ moduleId, depth, hasChildren: kids.length > 0, expanded });
        if (!expanded) return;
        for (const childId of kids) {
          walk(childId, depth + 1);
          if (rows.length >= maxRows) break;
        }
      };
      for (const rootId of roots) {
        walk(rootId, 0);
        if (rows.length >= maxRows) break;
      }
      return rows;
    }

    function focusNamespaceSubtree(moduleId) {
      if (!moduleId || !state.nodesById.has(moduleId)) return;
      const node = state.nodesById.get(moduleId);
      if (!node || node.kind !== "module") return;
      state.treeFocusRoot = moduleId;
      if (byId("viewMode") && byId("viewMode").value !== "module-map") {
        byId("viewMode").value = "module-map";
      }
      state.selected = moduleId;
      state.selectedEdge = null;
      materializeNode(moduleId);
      renderAll();
      fitViewToDisplay();
      setSourceHint(`subtree focus: ${moduleId}`);
    }

    function clearNamespaceSubtreeFocus() {
      if (!state.treeFocusRoot) return;
      state.treeFocusRoot = "";
      setSourceHint("subtree focus cleared");
      renderAll();
    }

    function renderNamespaceTree() {
      const box = byId("treeBox");
      if (!box) return;
      const rows = namespaceTreeRows(700);
      if (!rows.length) {
        box.innerHTML = "<div class='tiny'>No namespace tree available.</div>";
        return;
      }
      const active = state.treeFocusRoot || "";
      const html = rows.map((row) => {
        const indent = row.depth * 14;
        const toggle = row.hasChildren ? (row.expanded ? "▾" : "▸") : "·";
        const activeClass = active === row.moduleId ? " tree-active" : "";
        return `
          <div class="tree-row${activeClass}" data-tree-row="${row.moduleId}" style="padding-left:${indent}px">
            <span class="tree-toggle" data-tree-toggle="${row.moduleId}">${toggle}</span>
            <span class="tree-label">${compactModuleLabel(row.moduleId)}</span>
          </div>
        `;
      }).join("");
      box.innerHTML = html;

      box.querySelectorAll("[data-tree-toggle]").forEach((el) => {
        el.onclick = (ev) => {
          ev.stopPropagation();
          const id = el.getAttribute("data-tree-toggle");
          if (!id) return;
          if (!(state.treeExpanded instanceof Set)) state.treeExpanded = new Set();
          if (state.treeExpanded.has(id)) state.treeExpanded.delete(id);
          else state.treeExpanded.add(id);
          renderNamespaceTree();
        };
      });

      box.querySelectorAll("[data-tree-row]").forEach((el) => {
        el.onclick = () => {
          const id = el.getAttribute("data-tree-row");
          if (!id) return;
          focusNamespaceSubtree(id);
        };
      });
    }

    function renderDomainTagPanels() {
      const mathBox = byId("mathTagPanel");
      const appliedBox = byId("appliedTagPanel");
      const hint = byId("tagPanelHint");
      if (!mathBox || !appliedBox || !hint) return;

      const axisRows = (axis) => {
        const axes = state.domainAxes && typeof state.domainAxes === "object"
          ? state.domainAxes
          : {};
        const rows = axes[axis];
        if (!Array.isArray(rows)) return [];
        return rows.filter((row) => row && typeof row.id === "string" && row.id);
      };

      const getSet = (axis) => {
        if (axis === "math") {
          if (!(state.selectedMathTags instanceof Set)) state.selectedMathTags = new Set();
          return state.selectedMathTags;
        }
        if (!(state.selectedAppliedTags instanceof Set)) state.selectedAppliedTags = new Set();
        return state.selectedAppliedTags;
      };

      const renderAxis = (axis, box) => {
        const rows = axisRows(axis);
        const selected = getSet(axis);
        if (!rows.length) {
          box.innerHTML = "<div class='tiny'>none</div>";
          return;
        }
        box.innerHTML = rows.map((row) => {
          const active = selected.has(row.id) ? " active" : "";
          const title = typeof row.title === "string" && row.title ? row.title : row.id;
          return `<button class="tag-chip${active}" data-axis="${axis}" data-tag="${row.id}" title="${title}">${row.id}</button>`;
        }).join("");
      };

      renderAxis("math", mathBox);
      renderAxis("applied", appliedBox);

      const selectedMath = selectedAxisTags("math");
      const selectedApplied = selectedAxisTags("applied");
      const modeText = (selectedMath.size > 0 || selectedApplied.size > 0)
        ? "panel tags override dropdown"
        : "using dropdown single-tag filters";
      hint.innerHTML = `math <code>${selectedMath.size}</code> | applied <code>${selectedApplied.size}</code> | ${modeText}`;

      const bindClicks = (box) => {
        box.querySelectorAll("[data-axis][data-tag]").forEach((el) => {
          el.onclick = () => {
            const axis = el.getAttribute("data-axis");
            const tag = el.getAttribute("data-tag");
            if (!axis || !tag) return;
            const selected = getSet(axis);
            if (selected.has(tag)) selected.delete(tag);
            else selected.add(tag);
            const selectId = axis === "math" ? "mathTagFilter" : "appliedTagFilter";
            const select = byId(selectId);
            if (select && select.value !== "all") select.value = "all";
            renderAll();
          };
        });
      };
      bindClicks(mathBox);
      bindClicks(appliedBox);
    }

    function lensScoreMap(rows) {
      const out = new Map();
      if (!Array.isArray(rows)) return out;
      for (const row of rows) {
        if (!row || typeof row !== "object") continue;
        const moduleId = typeof row.module === "string" ? row.module : "";
        if (!moduleId) continue;
        const numericKeys = ["score", "in_degree", "weight", "count"];
        let value = 0;
        for (const key of numericKeys) {
          const raw = Number(row[key]);
          if (Number.isFinite(raw)) {
            value = raw;
            break;
          }
        }
        out.set(moduleId, value);
      }
      return out;
    }

    function renderMathlibLensPanel() {
      const box = byId("mathlibLensBox");
      if (!box) return;
      const mode = activeViewMode();
      const config = activeMathlibLensConfig();
      const lensMeta = state.graph && typeof state.graph === "object" && state.graph.mathlib_lens
        ? state.graph.mathlib_lens
        : {};
      const hubScore = lensScoreMap(lensMeta.top_hubs || []);
      const aggScore = lensScoreMap(lensMeta.aggregators || []);
      const dedupe = (rows, limit = 24) => {
        const out = [];
        const seen = new Set();
        for (const id of Array.isArray(rows) ? rows : []) {
          if (typeof id !== "string" || !id) continue;
          if (!state.nodesById.has(id)) continue;
          if (seen.has(id)) continue;
          seen.add(id);
          out.push(id);
          if (out.length >= limit) break;
        }
        return out;
      };
      const roots = dedupe(config.roots, 20);
      const hubs = dedupe(config.hubs, 20);
      const aggregators = dedupe(config.aggregators, 20);
      const bridges = dedupe(config.bridges, 20);
      const total = roots.length + hubs.length + aggregators.length + bridges.length;
      const selected = state.selected || "";

      if (total === 0) {
        box.innerHTML = "<div class='tiny'>No mathlib lens data in current dataset/profile.</div>";
        return;
      }

      const renderRows = (title, ids, badge, scoreById = null) => {
        if (!ids.length) return "";
        const rows = ids.map((id) => {
          const activeClass = selected === id ? " active" : "";
          const score = scoreById instanceof Map && scoreById.has(id)
            ? `<span class="badge">score ${scoreById.get(id)}</span>`
            : "";
          return `
            <div class="node-item${activeClass}" data-lens-node="${id}">
              <div><strong>${compactModuleLabel(id)}</strong></div>
              <div class="line2"><span class="badge">${badge}</span>${score}</div>
              <div class="line2"><code>${id}</code></div>
            </div>
          `;
        }).join("");
        return `
          <div class="lens-section">
            <div class="lens-section-title">${title} (${ids.length})</div>
            ${rows}
          </div>
        `;
      };

      const modeText = mode === "mathlib-lens" ? "active" : "inactive";
      const summary = `<div class="tiny">profile <code>${config.activeDomain || "all"}</code> | lens mode <code>${modeText}</code></div>`;
      const switchHint = mode === "mathlib-lens"
        ? ""
        : `<div class="tiny">Tip: switch to <code>Mathlib lens</code> mode for default lens graph.</div>`;
      box.innerHTML = [
        summary,
        switchHint,
        renderRows("Slice roots", roots, "root"),
        renderRows("Top hubs", hubs, "hub", hubScore),
        renderRows("Aggregators", aggregators, "agg", aggScore),
        renderRows("Bridge modules", bridges, "bridge"),
      ].join("");

      box.querySelectorAll("[data-lens-node]").forEach((el) => {
        el.onclick = () => {
          const id = el.getAttribute("data-lens-node");
          if (!id || !state.nodesById.has(id)) return;
          const modeSelect = byId("viewMode");
          if (modeSelect && modeSelect.value !== "mathlib-lens") {
            modeSelect.value = "mathlib-lens";
            modeSelect.dispatchEvent(new Event("change"));
          }
          materializeNode(id);
          selectAndFocus(id, false);
          setSourceHint(`mathlib lens node: ${id}`);
        };
      });
    }

    function selectAndFocus(id, focus = false) {
      materializeNode(id);
      state.selected = id;
      state.selectedEdge = null;
      renderAll();
      if (focus) centerOnNode(id);
    }

    function locateFirstMatch() {
      if (!state.searchMatches.length) {
        renderSearchResults();
      }
      if (!state.searchMatches.length) return;
      selectAndFocus(state.searchMatches[0].id, true);
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
      if (state.pinned.has(nodeId)) {
        return;
      }
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
        captured: false,
      };
    }

    function startPan(ev) {
      state.drag = {
        type: "pan",
        pointerId: ev.pointerId,
        startClientX: ev.clientX,
        startClientY: ev.clientY,
        startViewX: state.view.x,
        startViewY: state.view.y,
        moved: false,
        captured: false,
      };
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

      const dxPx = ev.clientX - state.drag.startClientX;
      const dyPx = ev.clientY - state.drag.startClientY;
      const delta = screenToSvgDelta(dxPx, dyPx);

      if (state.drag.type === "pan") {
        if (!state.drag.moved) {
          const movedPx = Math.hypot(dxPx, dyPx);
          if (movedPx < CANVAS_PAN_THRESHOLD_PX) return;
          state.drag.moved = true;
          if (!state.drag.captured) {
            state.drag.captured = true;
            svg.classList.add("panning");
            try {
              svg.setPointerCapture(ev.pointerId);
            } catch (_) {}
          }
        }
        state.view.x = state.drag.startViewX - delta.dx;
        state.view.y = state.drag.startViewY - delta.dy;
        clampView();
        applyViewBox();
        renderOverlay(state.lastDisplay);
        return;
      }

      if (state.drag.type === "node") {
        if (!state.drag.moved) {
          const movedPx = Math.hypot(dxPx, dyPx);
          if (movedPx < NODE_DRAG_THRESHOLD_PX) return;
          state.drag.moved = true;
          state.suppressClickUntil = Date.now() + 180;
          if (!state.drag.captured) {
            state.drag.captured = true;
            svg.classList.add("panning");
            try {
              svg.setPointerCapture(ev.pointerId);
            } catch (_) {}
          }
        }
        const nx = state.drag.startNodeX + delta.dx;
        const ny = state.drag.startNodeY + delta.dy;
        state.freePos.set(state.drag.nodeId, [nx, ny]);
        scheduleGraphRender();
      }
    }

    function onPointerUp(ev) {
      if (!state.drag || state.drag.pointerId !== ev.pointerId) return;
      const dragState = state.drag;
      if (dragState.captured) {
        svg.classList.remove("panning");
        try {
          if (!svg.hasPointerCapture || svg.hasPointerCapture(ev.pointerId)) {
            svg.releasePointerCapture(ev.pointerId);
          }
        } catch (_) {}
      }
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

      const linePx = 16;
      const pagePxX = Math.max(rect.width, 1);
      const pagePxY = Math.max(rect.height, 1);
      const dxPx = ev.deltaMode === 1
        ? ev.deltaX * linePx
        : (ev.deltaMode === 2 ? ev.deltaX * pagePxX : ev.deltaX);
      const dyPx = ev.deltaMode === 1
        ? ev.deltaY * linePx
        : (ev.deltaMode === 2 ? ev.deltaY * pagePxY : ev.deltaY);

      const likelyMouseWheel =
        ev.deltaMode !== 0 ||
        (Math.abs(dxPx) <= 2 && Math.abs(dyPx) >= 90) ||
        (Math.abs(dxPx) <= 2 && Number.isInteger(ev.deltaY) && Math.abs(ev.deltaY) >= 30);
      const wheelMode = byId("wheelMode") ? byId("wheelMode").value : "smart";
      let shouldZoom;
      if (wheelMode === "zoom") {
        shouldZoom = true;
      } else if (wheelMode === "pan") {
        shouldZoom = ev.ctrlKey;
      } else {
        shouldZoom = ev.ctrlKey || likelyMouseWheel;
      }

      if (!shouldZoom) {
        // Trackpad two-finger scroll defaults to pan.
        const panSpeed = 1.15;
        const delta = screenToSvgDelta(dxPx * panSpeed, dyPx * panSpeed);
        state.view.x += delta.dx;
        state.view.y += delta.dy;
        clampView();
        applyViewBox();
        renderOverlay(state.lastDisplay);
        return;
      }

      // Pinch (ctrlKey) and mouse wheel both zoom, with tuned strengths.
      const zoomStrength = ev.ctrlKey ? 0.006 : 0.0026;
      const factor = clamp(Math.exp(dyPx * zoomStrength), 0.25, 4);
      state.view.w = clamp(state.view.w * factor, 220, state.world.w * 4.2);
      state.view.h = clamp(state.view.h * factor, 160, state.world.h * 4.2);
      normalizeViewToViewport(anchorX, anchorY, px, py);
      applyViewBox();
      renderOverlay(state.lastDisplay);
    }

    function renderAll() {
      const display = collectDisplayGraph();
      renderGraph(display, false);
      renderSearchResults();
      renderNamespaceTree();
      renderDomainTagPanels();
      renderMathlibLensPanel();
    }

    async function initProofMapControls() {
      const select = byId("proofMapSelect");
      if (!select) return;
      const index = await loadProofMapIndex();
      const rows = index && Array.isArray(index.problems) ? index.problems : [];
      state.proofMapEntries = rows;
      const options = ['<option value="">(none)</option>'];
      for (const row of rows) {
        if (!row || typeof row.id !== "string" || !row.id) continue;
        const suite = typeof row.suite === "string" ? row.suite : "?";
        const problem = typeof row.problem === "string" ? row.problem : row.id;
        const nodes = Number(row.node_count || 0);
        options.push(`<option value="${row.id}">${suite}/${problem} (${nodes} nodes)</option>`);
      }
      select.innerHTML = options.join("");
      select.value = "";
    }

    function clearActiveProofMap() {
      state.activeProofMapId = "";
      state.proofMapNodeIds = null;
      state.proofMapEdgeKeys = null;
      const select = byId("proofMapSelect");
      if (select) select.value = "";
    }

    async function loadActiveProofMap() {
      const select = byId("proofMapSelect");
      if (!select) return;
      const mapId = select.value;
      if (!mapId) {
        clearActiveProofMap();
        setSourceHint("proof map cleared");
        renderAll();
        return;
      }
      const entry = state.proofMapEntries.find((row) => row && row.id === mapId);
      if (!entry) {
        setSourceHint(`proof map not found: ${mapId}`);
        return;
      }
      const mapPath = typeof entry.proof_map === "string" && entry.proof_map
        ? entry.proof_map
        : "";
      if (!mapPath) {
        setSourceHint(`proof map path missing: ${mapId}`);
        return;
      }
      const mapData = await loadProofMapData(mapPath);
      if (!mapData) {
        setSourceHint(`proof map load failed: ${mapId}`);
        return;
      }
      const nodeIds = new Set();
      const edgeKeys = new Set();
      for (const row of mapData.nodes || []) {
        if (!row || typeof row.id !== "string" || !row.id) continue;
        nodeIds.add(row.id);
      }
      for (const edge of mapData.edges || []) {
        if (!edge || typeof edge.src !== "string" || typeof edge.dst !== "string") continue;
        const edgeType = typeof edge.type === "string" ? edge.type : "";
        edgeKeys.add(`${edge.src}__${edgeType}__${edge.dst}`);
      }
      state.activeProofMapId = mapId;
      state.proofMapNodeIds = nodeIds;
      state.proofMapEdgeKeys = edgeKeys;
      for (const nodeId of nodeIds) {
        materializeNode(nodeId);
      }
      if (state.selected && !nodeIds.has(state.selected)) {
        state.selected = null;
      }
      setSourceHint(`proof map loaded: ${mapId} (${nodeIds.size} nodes)`);
      renderAll();
      fitViewToDisplay();
    }

    function wireControls() {
      const rerenderIds = [
        "scope", "layerFilter", "domainFilter", "mathTagFilter", "appliedTagFilter", "kindModule", "kindDecl", "kindConcept", "spineOnly",
        "edge_imports", "edge_contains", "edge_uses_type", "edge_uses_value", "edge_decl_in_module", "edge_binds",
        "edge_alias_of", "edge_used_recently",
        "showGenerated", "expandMathlib", "maxNodes", "maxEdges", "neighborhoodDepth", "layoutMode", "wheelMode", "groupCollapseDepth",
      ];
      for (const id of rerenderIds) {
        const el = byId(id);
        if (!el) continue;
        el.addEventListener("change", () => renderAll());
      }

      const mathTagSelect = byId("mathTagFilter");
      if (mathTagSelect) {
        mathTagSelect.addEventListener("change", () => {
          if (state.selectedMathTags instanceof Set) state.selectedMathTags.clear();
        });
      }
      const appliedTagSelect = byId("appliedTagFilter");
      if (appliedTagSelect) {
        appliedTagSelect.addEventListener("change", () => {
          if (state.selectedAppliedTags instanceof Set) state.selectedAppliedTags.clear();
        });
      }

      const selectedModuleId = () => {
        if (state.selected && state.nodesById.has(state.selected)) {
          const node = state.nodesById.get(state.selected);
          if (node) {
            if (node.kind === "module") return node.id;
            if (node.kind === "decl" && typeof node.module === "string") return node.module;
          }
        }
        if (state.selected && state.groupMembers instanceof Map && state.groupMembers.has(state.selected)) {
          const members = state.groupMembers.get(state.selected) || [];
          if (Array.isArray(members) && members.length > 0) return members[0];
        }
        let best = "";
        let bestDegree = -1;
        for (const id of state.visible) {
          const row = state.nodesById.get(id);
          if (!row || row.kind !== "module") continue;
          if (!nodePassesFilters(row)) continue;
          const deg = degreeOf(row.id);
          if (deg > bestDegree) {
            bestDegree = deg;
            best = row.id;
          }
        }
        if (best) return best;
        return "";
      };

      const primeSelectedModuleDecls = () => {
        const moduleId = selectedModuleId();
        if (!moduleId) return false;
        if (!state.nodesById.has(moduleId)) return false;
        if (!state.moduleDeclCursor.has(moduleId) || (state.moduleDeclCursor.get(moduleId) || 0) <= 0) {
          state.moduleDeclCursor.set(moduleId, MODULE_DECL_PAGE_SIZE);
        }
        if (typeof syncExpandedModuleDecls === "function") {
          syncExpandedModuleDecls();
        }
        return true;
      };

      const materializeDeclEdgeNeighborhood = (edgeType, limit = 120) => {
        const seeds = [];
        for (const id of state.visible) {
          const node = state.nodesById.get(id);
          if (!node || node.kind !== "decl") continue;
          seeds.push(node.id);
        }
        let added = 0;
        for (const nodeId of seeds) {
          const around = (state.outgoing.get(nodeId) || []).concat(state.incoming.get(nodeId) || []);
          for (const e of around) {
            if (e.type !== edgeType) continue;
            const otherId = e.src === nodeId ? e.dst : e.src;
            if (!otherId || !state.nodesById.has(otherId)) continue;
            const other = state.nodesById.get(otherId);
            if (!other || other.kind !== "decl") continue;
            if (state.visible.has(otherId)) continue;
            materializeNode(otherId);
            added += 1;
            if (added >= limit) return added;
          }
        }
        return added;
      };

      byId("kindDecl").addEventListener("change", () => {
        if (!byId("kindDecl").checked) return;
        if (byId("edge_decl_in_module")) byId("edge_decl_in_module").checked = true;
        if (primeSelectedModuleDecls()) renderAll();
      });

      byId("showGenerated").addEventListener("change", () => {
        if (!byId("kindDecl").checked) return;
        if (activeViewMode() !== "module-map") return;
        if (byId("showGenerated").checked) {
          const moduleId = selectedModuleId();
          if (moduleId && state.nodesById.has(moduleId)) {
            const cursor = Math.max(0, Number(state.moduleDeclCursor.get(moduleId) || 0));
            state.moduleDeclCursor.set(moduleId, cursor + MODULE_DECL_PAGE_SIZE);
            let addedGenerated = 0;
            if (typeof moduleDeclCandidates === "function") {
              const candidates = moduleDeclCandidates(moduleId);
              for (const node of candidates) {
                if (!node || node.kind !== "decl") continue;
                if (node.generated !== true) continue;
                if (state.visible.has(node.id)) continue;
                materializeNode(node.id);
                addedGenerated += 1;
                if (addedGenerated >= MODULE_DECL_PAGE_SIZE) break;
              }
            }
            if (addedGenerated === 0) {
              setSourceHint(`no generated decls added for ${moduleId} under current filters`);
            } else {
              setSourceHint(`added ${addedGenerated} generated decls for ${moduleId}`);
            }
          }
        }
        if (typeof syncExpandedModuleDecls === "function") {
          syncExpandedModuleDecls();
          renderAll();
        }
      });

      for (const edgeId of ["edge_decl_in_module", "edge_uses_type", "edge_uses_value"]) {
        const el = byId(edgeId);
        if (!el) continue;
        el.addEventListener("change", () => {
          if (!el.checked) return;
          byId("kindDecl").checked = true;
          const primed = primeSelectedModuleDecls();
          if (edgeId === "edge_uses_type" || edgeId === "edge_uses_value") {
            materializeDeclEdgeNeighborhood(edgeId === "edge_uses_type" ? "uses_type" : "uses_value");
          }
          if (primed || edgeId !== "edge_decl_in_module") renderAll();
        });
      }

      const binds = byId("edge_binds");
      if (binds) {
        binds.addEventListener("change", () => {
          if (!binds.checked) return;
          byId("kindConcept").checked = true;
          byId("kindDecl").checked = true;
          let bindRows = 0;
          for (const e of state.edges) {
            if (e.type !== "binds") continue;
            materializeNode(e.src);
            materializeNode(e.dst);
            bindRows += 1;
          }
          const primed = primeSelectedModuleDecls();
          if (bindRows > 0 || primed) renderAll();
        });
      }

      byId("viewMode").addEventListener("change", () => {
        const mode = activeViewMode();
        if (mode !== "module-map" && mode !== "mathlib-lens") {
          clearImportLens();
        }
        if (mode === "decl-neighborhood") {
          byId("kindDecl").checked = true;
          byId("kindModule").checked = true;
          byId("edge_uses_value").checked = true;
        }
        if (mode === "concept-browser") {
          byId("kindConcept").checked = true;
          byId("edge_binds").checked = true;
        }
        if (mode === "mathlib-lens") {
          byId("scope").value = "all";
          byId("kindModule").checked = true;
          byId("kindDecl").checked = false;
          byId("kindConcept").checked = false;
          byId("edge_imports").checked = true;
          if (byId("edge_contains")) byId("edge_contains").checked = true;
          byId("edge_uses_type").checked = false;
          byId("edge_uses_value").checked = false;
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

      const datasetSelect = byId("datasetSelect");
      if (datasetSelect) {
        datasetSelect.addEventListener("change", async () => {
          const nextId = datasetSelect.value || "latest";
          try {
            clearActiveProofMap();
            clearImportLens();
            state.graph = await loadData(nextId);
            buildIndex();
            rebuildNamespaceTree();
            refreshDatasetOptions();
            await initProofMapControls();
            initDomainFilter();
            state.pinned.clear();
            state.moduleDeclCursor.clear();
            state.freePos.clear();
            state.basePos.clear();
            state.lastPos.clear();
            resetToModuleMap();
            renderAll();
            fitViewToDisplay();
            setSourceHint(`dataset switched: ${state.activeDatasetId}`);
          } catch (err) {
            setSourceHint(`dataset load failed: ${String(err)}`);
          }
        });
      }

      const loadProofMapBtn = byId("loadProofMap");
      if (loadProofMapBtn) {
        loadProofMapBtn.onclick = () => {
          loadActiveProofMap();
        };
      }
      const clearProofMapBtn = byId("clearProofMap");
      if (clearProofMapBtn) {
        clearProofMapBtn.onclick = () => {
          clearActiveProofMap();
          setSourceHint("proof map cleared");
          renderAll();
        };
      }
      const proofMapSelect = byId("proofMapSelect");
      if (proofMapSelect) {
        proofMapSelect.addEventListener("change", () => {
          if (!proofMapSelect.value) {
            clearActiveProofMap();
            setSourceHint("proof map cleared");
            renderAll();
          }
        });
      }

      byId("resetMap").onclick = () => {
        byId("viewMode").value = "module-map";
        clearImportLens();
        resetToModuleMap();
        renderAll();
        fitViewToDisplay();
      };
      const openMathlibLens = byId("openMathlibLens");
      if (openMathlibLens) {
        openMathlibLens.onclick = () => {
          byId("viewMode").value = "mathlib-lens";
          byId("viewMode").dispatchEvent(new Event("change"));
        };
      }
      const clearTreeFocusBtn = byId("clearTreeFocus");
      if (clearTreeFocusBtn) {
        clearTreeFocusBtn.onclick = () => {
          clearNamespaceSubtreeFocus();
        };
      }
      const clearTagPanelBtn = byId("clearTagPanel");
      if (clearTagPanelBtn) {
        clearTagPanelBtn.onclick = () => {
          if (state.selectedMathTags instanceof Set) state.selectedMathTags.clear();
          if (state.selectedAppliedTags instanceof Set) state.selectedAppliedTags.clear();
          if (byId("mathTagFilter")) byId("mathTagFilter").value = "all";
          if (byId("appliedTagFilter")) byId("appliedTagFilter").value = "all";
          setSourceHint("tag panel filters cleared");
          renderAll();
        };
      }

      byId("fitView").onclick = () => fitViewToDisplay();

      byId("clearPins").onclick = () => {
        state.pinned.clear();
        renderAll();
      };
      byId("saveLayout").onclick = () => saveLayoutToStorage();
      byId("loadLayout").onclick = () => loadLayoutFromStorage();
      byId("clearLayout").onclick = () => clearSavedLayout();
      byId("toggleOverlay").onclick = () => {
        state.panelUI.overlayCollapsed = !state.panelUI.overlayCollapsed;
        applyPanelUIState();
        savePanelUIState();
      };
      byId("toggleStats").onclick = () => {
        state.panelUI.statsCollapsed = !state.panelUI.statsCollapsed;
        applyPanelUIState();
        savePanelUIState();
      };
      byId("resetPanels").onclick = () => {
        state.panelUI.overlayCollapsed = false;
        state.panelUI.statsCollapsed = false;
        applyPanelUIState();
        savePanelUIState();
      };

      svg.addEventListener("pointerdown", (ev) => {
        if (ev.button !== 0) return;
        if (ev.target !== svg) return;
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
          refreshNodeVisualState();
          renderInspector(state.lastDisplay);
          renderOverlay(state.lastDisplay);
        }
      });
    }

    async function boot() {
      try {
        refreshDatasetOptions();
        state.graph = await loadData(state.activeDatasetId || "latest");
        buildIndex();
        rebuildNamespaceTree();
        refreshDatasetOptions();
        await initProofMapControls();
        initDomainFilter();
        resetToModuleMap();
        wireControls();
        loadPanelUIState();
        applyPanelUIState();
        renderAll();
        fitViewToDisplay();
      } catch (err) {
        byId("statsBox").textContent = String(err);
        byId("overlay").textContent = "failed to load graph";
        byId("details").textContent = String(err);
      }
    }

    boot();

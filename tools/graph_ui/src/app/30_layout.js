    function placeCircularCluster(rows, anchor, seed, options, pos, bounds) {
      const W = bounds.w;
      const H = bounds.h;
      const M = bounds.m;
      const baseRadius = options.baseRadius || 42;
      const ringStep = options.ringStep || 22;
      const minChord = Math.max(10, options.minChord || 20);
      const yScale = options.yScale || 1;

      let index = 0;
      let ring = 0;
      while (index < rows.length) {
        const radius = baseRadius + ring * ringStep;
        let slots = Math.floor((2 * Math.PI * Math.max(radius, 1)) / minChord);
        if (!Number.isFinite(slots) || slots < 1) slots = 8;
        slots = clamp(slots, 8, 96);
        const count = Math.min(slots, rows.length - index);
        const start = (((seed + ring * 47) % 360) * Math.PI) / 180;
        for (let slot = 0; slot < count; slot++) {
          const angle = start + ((2 * Math.PI) * slot) / Math.max(count, 1);
          const x = clamp(anchor[0] + Math.cos(angle) * radius, M, W - M);
          const y = clamp(anchor[1] + Math.sin(angle) * radius * yScale, M, H - M);
          pos.set(rows[index + slot].id, [x, y]);
        }
        index += count;
        ring += 1;
      }
    }

    function spacingRadius(node) {
      if (!node) return 10;
      if (node.kind === "module") return clamp(22 + estimateLabelWidth(node) * 0.32, 34, 146);
      if (node.kind === "concept") return clamp(14 + estimateLabelWidth(node) * 0.24, 20, 72);
      return clamp(9 + estimateLabelWidth(node) * 0.08, 9, 26);
    }

    function resolveNodeOverlaps(displayNodes, pos) {
      if (!displayNodes || displayNodes.length < 2) return pos;
      const W = state.world.w;
      const H = state.world.h;
      const M = 72;
      const items = displayNodes.map((n) => {
        const p = pos.get(n.id) || [W / 2, H / 2];
        return {
          node: n,
          x: p[0],
          y: p[1],
          ox: p[0],
          oy: p[1],
        };
      });

      const maxIter = displayNodes.length > 360 ? 5 : 7;
      for (let iter = 0; iter < maxIter; iter++) {
        let moved = false;
        for (let i = 0; i < items.length; i++) {
          const a = items[i];
          for (let j = i + 1; j < items.length; j++) {
            const b = items[j];
            let dx = b.x - a.x;
            let dy = b.y - a.y;
            let dist = Math.hypot(dx, dy);
            const minDist = spacingRadius(a.node) + spacingRadius(b.node) + 2;
            if (dist >= minDist) continue;

            if (dist < 1e-3) {
              const seed = hashInt(`${a.node.id}|${b.node.id}`);
              dx = ((seed & 255) - 128) / 128;
              dy = (((seed >>> 8) & 255) - 128) / 128;
              dist = Math.hypot(dx, dy) || 1;
            }

            const ux = dx / dist;
            const uy = dy / dist;
            const push = (minDist - dist) * 0.5;
            const wa = a.node.kind === "module" ? 0.75 : 1;
            const wb = b.node.kind === "module" ? 0.75 : 1;
            const sum = wa + wb;
            const pa = push * (wa / sum);
            const pb = push * (wb / sum);

            a.x = clamp(a.x - ux * pa, M, W - M);
            a.y = clamp(a.y - uy * pa, M, H - M);
            b.x = clamp(b.x + ux * pb, M, W - M);
            b.y = clamp(b.y + uy * pb, M, H - M);
            moved = true;
          }
        }

        for (const item of items) {
          const spring = item.node.kind === "module" ? 0.09 : 0.05;
          item.x += (item.ox - item.x) * spring;
          item.y += (item.oy - item.y) * spring;
        }
        if (!moved) break;
      }

      const out = new Map(pos);
      for (const item of items) {
        out.set(item.node.id, [item.x, item.y]);
      }
      return out;
    }

    function computeLayeredLayout(displayNodes) {
      const W = state.world.w;
      const H = state.world.h;
      const M = 80;
      const pos = new Map();

      const concepts = displayNodes.filter((n) => n.kind === "concept").sort((a, b) => a.id.localeCompare(b.id));
      for (let i = 0; i < concepts.length; i++) {
        const x = 180 + ((i + 1) * (W - 360)) / (concepts.length + 1);
        const y = 120;
        pos.set(concepts[i].id, [x, y]);
      }

      const modulesByLayer = new Map();
      for (const n of displayNodes) {
        if (n.kind !== "module") continue;
        const layer = layerKey(n);
        if (!modulesByLayer.has(layer)) modulesByLayer.set(layer, []);
        modulesByLayer.get(layer).push(n);
      }

      const layerOrder = ["core", "methods", "applications", "books", "other", "mathlib"];
      const activeLayers = layerOrder.filter((layer) => modulesByLayer.has(layer));
      const layerX = new Map();
      const lanes = activeLayers.length || 1;
      for (let i = 0; i < lanes; i++) {
        const layer = activeLayers[i] || "other";
        const x = M + ((i + 1) * (W - 2 * M)) / (lanes + 1);
        layerX.set(layer, x);
      }

      for (const [layer, mods] of modulesByLayer.entries()) {
        mods.sort((a, b) =>
          (b.id === MATHLIB_SLICE_ID ? 1 : 0) - (a.id === MATHLIB_SLICE_ID ? 1 : 0) ||
          (b.spine ? 1 : 0) - (a.spine ? 1 : 0) ||
          degreeOf(b.id) - degreeOf(a.id) ||
          a.id.localeCompare(b.id)
        );
        const x = layerX.get(layer) || layerX.get("other") || (W * 0.5);
        const spanTop = layer === "mathlib" ? 180 : 220;
        const spanBottom = H - 120;
        const span = Math.max(120, spanBottom - spanTop);
        const rowStep = labelSpacingForRows(mods, { floor: 38, ceil: 120, factor: 0.5 });
        const rowsPerCol = Math.max(3, Math.floor(span / Math.max(rowStep + 6, 1)));
        const cols = Math.max(1, Math.ceil(mods.length / rowsPerCol));
        const colGap = labelSpacingForRows(mods, { floor: 240, ceil: 700, factor: 2.1 });
        for (let i = 0; i < mods.length; i++) {
          const col = Math.floor(i / rowsPerCol);
          const row = i % rowsPerCol;
          const y = spanTop + ((row + 1) * (spanBottom - spanTop)) / (rowsPerCol + 1);
          const xOffset = (col - (cols - 1) / 2) * colGap;
          pos.set(mods[i].id, [clamp(x + xOffset, M, W - M), y]);
        }
      }

      const decls = displayNodes.filter((n) => n.kind === "decl");
      const declByModule = new Map();
      for (const d of decls) {
        const mod = typeof d.module === "string" && d.module ? d.module : "@orphans";
        if (!declByModule.has(mod)) declByModule.set(mod, []);
        declByModule.get(mod).push(d);
      }

      for (const [mod, rows] of declByModule.entries()) {
        rows.sort((a, b) => degreeOf(b.id) - degreeOf(a.id) || a.id.localeCompare(b.id));
        const anchorLayer = rows[0] ? layerKey(rows[0]) : "other";
        const anchor = pos.get(mod) || [layerX.get(anchorLayer) || layerX.get("other") || 1860, 900];
        const declChord = labelSpacingForRows(rows, { floor: 28, ceil: 120, factor: 0.44 });
        placeCircularCluster(
          rows,
          anchor,
          hashInt(mod),
          { baseRadius: 78, ringStep: 32, minChord: declChord, yScale: 0.94 },
          pos,
          { w: W, h: H, m: M }
        );
      }

      for (const n of displayNodes) {
        if (pos.has(n.id)) continue;
        const h = hashInt(n.id);
        const x = 120 + (h % 2000);
        const y = 180 + ((h >>> 10) % 1050);
        pos.set(n.id, [x, y]);
      }

      return pos;
    }

    function computeRadialLayout(displayNodes) {
      const W = state.world.w;
      const H = state.world.h;
      const M = 80;
      const pos = new Map();
      const cx = W / 2;
      const cy = H / 2;

      const layerRadius = {
        core: 230,
        methods: 340,
        applications: 450,
        books: 560,
        other: 640,
        mathlib: 730,
      };

      const concepts = displayNodes.filter((n) => n.kind === "concept").sort((a, b) => a.id.localeCompare(b.id));
      for (let i = 0; i < concepts.length; i++) {
        const a = (-Math.PI / 2) + ((2 * Math.PI) * i) / Math.max(1, concepts.length);
        pos.set(concepts[i].id, [cx + Math.cos(a) * 110, cy + Math.sin(a) * 110]);
      }

      const modulesByLayer = new Map();
      for (const n of displayNodes) {
        if (n.kind !== "module") continue;
        const layer = layerKey(n);
        if (!modulesByLayer.has(layer)) modulesByLayer.set(layer, []);
        modulesByLayer.get(layer).push(n);
      }

      for (const [layer, mods] of modulesByLayer.entries()) {
        mods.sort((a, b) =>
          (b.id === MATHLIB_SLICE_ID ? 1 : 0) - (a.id === MATHLIB_SLICE_ID ? 1 : 0) ||
          (b.spine ? 1 : 0) - (a.spine ? 1 : 0) ||
          degreeOf(b.id) - degreeOf(a.id) ||
          a.id.localeCompare(b.id)
        );
        const moduleChord = labelSpacingForRows(mods, { floor: 90, ceil: 260, factor: 1.0 });
        placeCircularCluster(
          mods,
          [cx, cy],
          hashInt(`layer:${layer}`),
          { baseRadius: layerRadius[layer] || layerRadius.other, ringStep: 34, minChord: moduleChord, yScale: 0.95 },
          pos,
          { w: W, h: H, m: M }
        );
      }

      const decls = displayNodes.filter((n) => n.kind === "decl");
      const declByModule = new Map();
      for (const d of decls) {
        const mod = typeof d.module === "string" && d.module ? d.module : "@orphans";
        if (!declByModule.has(mod)) declByModule.set(mod, []);
        declByModule.get(mod).push(d);
      }

      for (const [mod, rows] of declByModule.entries()) {
        rows.sort((a, b) => degreeOf(b.id) - degreeOf(a.id) || a.id.localeCompare(b.id));
        const anchor = pos.get(mod) || [cx, cy];
        const declChord = labelSpacingForRows(rows, { floor: 18, ceil: 64, factor: 0.22 });
        placeCircularCluster(
          rows,
          anchor,
          hashInt(mod),
          { baseRadius: 42, ringStep: 22, minChord: declChord, yScale: 1 },
          pos,
          { w: W, h: H, m: M }
        );
      }

      for (const n of displayNodes) {
        if (pos.has(n.id)) continue;
        const h = hashInt(n.id);
        const x = 120 + (h % 2000);
        const y = 180 + ((h >>> 10) % 1050);
        pos.set(n.id, [x, y]);
      }

      return pos;
    }

    function computeLayout(displayNodes) {
      const mode = byId("layoutMode").value || "layered";
      const seedPos = mode === "radial"
        ? computeRadialLayout(displayNodes)
        : computeLayeredLayout(displayNodes);
      state.basePos = resolveNodeOverlaps(displayNodes, seedPos);
    }

    function nodePos(id) {
      return state.pinned.get(id) || state.freePos.get(id) || state.basePos.get(id) || [50, 50];
    }

    function shouldLabel(node, displayNodes) {
      const mode = activeViewMode();
      const zoom = currentZoom();
      if (state.selected === node.id) return true;
      if (mode === "module-map") {
        if (node.kind === "module") return true;
        if (node.kind === "concept") return true;
        if (node.kind === "decl") return zoom >= 2.2 && labelDegreeOf(node.id) >= 8;
        return false;
      }
      if (node.kind === "concept") return true;
      if (node.kind === "module") {
        if (zoom < 1.2) return node.spine || node.id === MATHLIB_SLICE_ID || labelDegreeOf(node.id) >= 5;
        if (displayNodes.length <= 70) return true;
        if (zoom < 1.6) return node.spine || node.id === MATHLIB_SLICE_ID || labelDegreeOf(node.id) >= 4;
        return node.spine || node.id === MATHLIB_SLICE_ID || labelDegreeOf(node.id) >= 3;
      }
      if (zoom < 1.3) return node.spine || labelDegreeOf(node.id) >= 10;
      if (displayNodes.length <= 90) return true;
      return node.spine || labelDegreeOf(node.id) >= 8;
    }

    function makeLabelPlacement(node, x, y, textWidth, side, offsetY) {
      const yLine = y + offsetY - 7;
      if (side === "right") {
        const labelX = x + 10;
        return {
          x: labelX,
          y: yLine,
          anchor: "start",
          box: { x1: labelX - 3, y1: yLine - 13, x2: labelX + textWidth + 3, y2: yLine + 4 },
        };
      }
      if (side === "left") {
        const labelX = x - 10;
        return {
          x: labelX,
          y: yLine,
          anchor: "end",
          box: { x1: labelX - textWidth - 3, y1: yLine - 13, x2: labelX + 3, y2: yLine + 4 },
        };
      }
      if (side === "top") {
        const labelX = x;
        const yy = y + offsetY - 7;
        return {
          x: labelX,
          y: yy,
          anchor: "middle",
          box: { x1: labelX - textWidth * 0.5 - 3, y1: yy - 13, x2: labelX + textWidth * 0.5 + 3, y2: yy + 4 },
        };
      }
      const labelX = x;
      const yy = y + offsetY + 7;
      return {
        x: labelX,
        y: yy,
        anchor: "middle",
        box: { x1: labelX - textWidth * 0.5 - 3, y1: yy - 13, x2: labelX + textWidth * 0.5 + 3, y2: yy + 4 },
      };
    }

    function pickLabelPlacement(node, x, y, textWidth, placedLabelBoxes, mode) {
      const preferRight = x < state.world.w * 0.5;
      const sideA = preferRight ? "right" : "left";
      const sideB = preferRight ? "left" : "right";
      const candidates = [];
      if (node.kind === "module" || node.kind === "concept") {
        const offsets = [0, -16, 16, -30, 30, -44, 44];
        for (const off of offsets) {
          candidates.push(makeLabelPlacement(node, x, y, textWidth, sideA, off));
          candidates.push(makeLabelPlacement(node, x, y, textWidth, sideB, off));
        }
        candidates.push(makeLabelPlacement(node, x, y, textWidth, "top", -40));
        candidates.push(makeLabelPlacement(node, x, y, textWidth, "bottom", 26));
      } else {
        const offsets = [0, -12, 12];
        for (const off of offsets) {
          candidates.push(makeLabelPlacement(node, x, y, textWidth, sideA, off));
          candidates.push(makeLabelPlacement(node, x, y, textWidth, sideB, off));
        }
      }

      const overlaps = (box) => placedLabelBoxes.some((b) =>
        !(box.x2 < b.x1 || box.x1 > b.x2 || box.y2 < b.y1 || box.y1 > b.y2)
      );

      for (const c of candidates) {
        if (!overlaps(c.box)) return c;
      }
      if (mode === "module-map" && node.kind === "module") {
        return candidates[0] || null;
      }
      return null;
    }


const state = {
  originalSymbols: new Map(),
  workingSymbols: new Map(),
  symbolOrder: [],
  previewOnlyNodes: [],
  previews: [],
  anchorOrder: [],
  anchorTails: {},
  grid: null,
  currentSymbolId: null,
  dragAnchor: null,
  svg: null,
};

const tabButtons = document.querySelectorAll(".tab-button");
const tabPanels = {
  editor: document.getElementById("tab-editor"),
  previews: document.getElementById("tab-previews"),
};

const symbolList = document.getElementById("symbol-list");
const anchorTableBody = document.getElementById("anchor-table-body");
const metricsTableBody = document.getElementById("metrics-table-body");
const previewNodeList = document.getElementById("preview-node-list");
const previewGallery = document.getElementById("preview-gallery");
const previewError = document.getElementById("preview-error");
const packagePath = document.getElementById("package-path");
const symbolTitle = document.getElementById("symbol-title");
const iconWidthBadge = document.getElementById("icon-width-badge");
const statusPill = document.getElementById("status-pill");
const saveButton = document.getElementById("save-button");
const resetSymbolButton = document.getElementById("reset-symbol-button");
const revertAllButton = document.getElementById("revert-all-button");
const rebuildPreviewsButton = document.getElementById("rebuild-previews-button");
state.svg = document.getElementById("anchor-canvas");

const SVG_NS = "http://www.w3.org/2000/svg";
const HANDLE_RADIUS = 0.9;

function toSvgPoint(point) {
  return { x: point.x, y: -point.y };
}

function toSvgY(value) {
  return -value;
}

function deepCopy(value) {
  return JSON.parse(JSON.stringify(value));
}

function mm(value) {
  return `${Number(value).toFixed(2).replace(/\.00$/, "").replace(/(\.\d)0$/, "$1")} mm`;
}

function setStatus(message, kind = "") {
  statusPill.textContent = message;
  statusPill.className = `status-pill${kind ? ` ${kind}` : ""}`;
}

function api(path, options = {}) {
  return fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  }).then(async (response) => {
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.error || payload.previewError || response.statusText);
    }
    return payload;
  });
}

function createSvgElement(tag, attrs = {}) {
  const element = document.createElementNS(SVG_NS, tag);
  Object.entries(attrs).forEach(([key, value]) => {
    element.setAttribute(key, String(value));
  });
  return element;
}

function getCurrentSymbol() {
  return state.workingSymbols.get(state.currentSymbolId);
}

function getOriginalSymbol() {
  return state.originalSymbols.get(state.currentSymbolId);
}

function refreshSymbolList() {
  symbolList.innerHTML = "";
  state.symbolOrder.forEach((symbolId) => {
    const symbol = state.workingSymbols.get(symbolId);
    const button = document.createElement("button");
    button.type = "button";
    button.className = `symbol-button${state.currentSymbolId === symbolId ? " active" : ""}`;
    button.textContent = symbol.label;
    button.addEventListener("click", () => {
      state.currentSymbolId = symbolId;
      refreshUI();
    });
    symbolList.appendChild(button);
  });
}

function refreshPreviewNodeList() {
  previewNodeList.innerHTML = "";
  state.previewOnlyNodes.forEach((name) => {
    const li = document.createElement("li");
    li.textContent = name;
    previewNodeList.appendChild(li);
  });
}

function refreshPreviewGallery(cacheBuster = "") {
  previewGallery.innerHTML = "";
  previewError.textContent = state.previewError || "";
  state.previews.forEach((preview) => {
    const card = document.createElement("article");
    card.className = "preview-card";
    const title = document.createElement("h3");
    title.textContent = preview.title;
    const description = document.createElement("p");
    description.textContent = preview.description;
    const img = document.createElement("img");
    img.alt = preview.title;
    img.src = cacheBuster ? `${preview.imageUrl}?t=${cacheBuster}` : preview.imageUrl;
    card.append(title, description, img);
    previewGallery.appendChild(card);
  });
}

function refreshMetricsTable(symbol) {
  metricsTableBody.innerHTML = "";
  Object.entries(symbol.metrics).forEach(([metric, value]) => {
    const row = document.createElement("tr");
    const nameCell = document.createElement("td");
    nameCell.textContent = metric;
    const valueCell = document.createElement("td");
    valueCell.textContent = mm(value);
    row.append(nameCell, valueCell);
    metricsTableBody.appendChild(row);
  });
}

function updateAnchorValue(symbolId, anchorId, axis, rawValue) {
  const value = Number.parseFloat(rawValue);
  if (Number.isNaN(value)) {
    return;
  }
  const symbol = state.workingSymbols.get(symbolId);
  symbol.anchors[anchorId][axis] = snapValue(value);
  renderCanvas();
  refreshAnchorTable(symbol);
}

function refreshAnchorTable(symbol) {
  anchorTableBody.innerHTML = "";
  state.anchorOrder.forEach((anchorId) => {
    const row = document.createElement("tr");
    const nameCell = document.createElement("td");
    nameCell.innerHTML = `<code>${anchorLabel(anchorId)}</code>`;
    const xCell = document.createElement("td");
    const yCell = document.createElement("td");
    const xInput = document.createElement("input");
    xInput.type = "number";
    xInput.step = "0.05";
    xInput.value = symbol.anchors[anchorId].x;
    xInput.addEventListener("change", (event) => updateAnchorValue(symbol.id, anchorId, "x", event.target.value));
    const yInput = document.createElement("input");
    yInput.type = "number";
    yInput.step = "0.05";
    yInput.value = symbol.anchors[anchorId].y;
    yInput.addEventListener("change", (event) => updateAnchorValue(symbol.id, anchorId, "y", event.target.value));
    xCell.appendChild(xInput);
    yCell.appendChild(yInput);
    row.append(nameCell, xCell, yCell);
    anchorTableBody.appendChild(row);
  });
}

function anchorLabel(anchorId) {
  return anchorId.replace("north", "north ").replace("south", "south ").replace("east", "east").replace("west", "west").trim().replace(/\s+/g, " ");
}

function snapValue(value) {
  const rounded = Math.round(value * 20) / 20;
  return Object.is(rounded, -0) ? 0 : rounded;
}

function drawGrid(svg, grid) {
  const group = createSvgElement("g");
  for (let x = grid.xmin; x <= grid.xmax; x += grid.minor_step) {
    group.appendChild(
      createSvgElement("line", {
        x1: x,
        y1: toSvgY(grid.ymin),
        x2: x,
        y2: toSvgY(grid.ymax),
        stroke: x % grid.major_step === 0 ? "rgba(0,0,0,0.18)" : "rgba(0,0,0,0.10)",
        "stroke-width": x % grid.major_step === 0 ? 0.12 : 0.08,
      }),
    );
  }
  for (let y = grid.ymin; y <= grid.ymax; y += grid.minor_step) {
    group.appendChild(
      createSvgElement("line", {
        x1: grid.xmin,
        y1: toSvgY(y),
        x2: grid.xmax,
        y2: toSvgY(y),
        stroke: y % grid.major_step === 0 ? "rgba(0,0,0,0.18)" : "rgba(0,0,0,0.10)",
        "stroke-width": y % grid.major_step === 0 ? 0.12 : 0.08,
      }),
    );
  }
  group.appendChild(createSvgElement("line", { x1: grid.xmin, y1: 0, x2: grid.xmax, y2: 0, stroke: "rgba(0,0,0,0.28)", "stroke-width": 0.18 }));
  group.appendChild(createSvgElement("line", { x1: 0, y1: toSvgY(grid.ymin), x2: 0, y2: toSvgY(grid.ymax), stroke: "rgba(0,0,0,0.28)", "stroke-width": 0.18 }));

  for (let x = grid.xmin; x <= grid.xmax; x += grid.major_step) {
    const label = createSvgElement("text", {
      x,
      y: toSvgY(-1.4),
      "text-anchor": "middle",
      "font-size": 1.2,
      fill: "rgba(0,0,0,0.45)",
      class: "grid-label",
    });
    label.textContent = x;
    group.appendChild(label);
  }
  for (let y = grid.ymin + 3; y <= grid.ymax - 3; y += grid.major_step) {
    const label = createSvgElement("text", {
      x: -1.2,
      y: toSvgY(y),
      "text-anchor": "end",
      "dominant-baseline": "middle",
      "font-size": 1.2,
      fill: "rgba(0,0,0,0.45)",
      class: "grid-label",
    });
    label.textContent = y;
    group.appendChild(label);
  }

  const xLabel = createSvgElement("text", {
    x: grid.xmax + 1,
    y: 0,
    "text-anchor": "start",
    "dominant-baseline": "middle",
    "font-size": 1.3,
    fill: "rgba(0,0,0,0.55)",
    class: "axis-label",
  });
  xLabel.textContent = "x / mm";
  group.appendChild(xLabel);

  const yLabel = createSvgElement("text", {
    x: 0,
    y: toSvgY(grid.ymin - 1.5),
    "text-anchor": "middle",
    "font-size": 1.3,
    fill: "rgba(0,0,0,0.55)",
    class: "axis-label",
  });
  yLabel.textContent = "y / mm";
  group.appendChild(yLabel);

  svg.appendChild(group);
}

function drawIcon(svg, symbol) {
  const iconHeightMm = symbol.iconWidthMm * symbol.iconAspectRatio;
  const image = createSvgElement("image", {
    href: symbol.iconUrl,
    x: -symbol.iconWidthMm / 2,
    y: -iconHeightMm / 2,
    width: symbol.iconWidthMm,
    height: iconHeightMm,
    preserveAspectRatio: "xMidYMid meet",
  });
  svg.appendChild(image);
}

function drawOpenArrow(svg, tail, head) {
  const svgTail = toSvgPoint(tail);
  const svgHead = toSvgPoint(head);
  const line = createSvgElement("line", {
    x1: svgTail.x,
    y1: svgTail.y,
    x2: svgHead.x,
    y2: svgHead.y,
    stroke: "#111",
    "stroke-width": 0.25,
  });
  svg.appendChild(line);

  const dx = svgHead.x - svgTail.x;
  const dy = svgHead.y - svgTail.y;
  const len = Math.hypot(dx, dy) || 1;
  const ux = dx / len;
  const uy = dy / len;
  const headLength = 1.9;
  const headWidth = 0.85;
  const left = {
    x: svgHead.x - ux * headLength - uy * headWidth,
    y: svgHead.y - uy * headLength + ux * headWidth,
  };
  const right = {
    x: svgHead.x - ux * headLength + uy * headWidth,
    y: svgHead.y - uy * headLength - ux * headWidth,
  };
  svg.appendChild(createSvgElement("line", { x1: left.x, y1: left.y, x2: svgHead.x, y2: svgHead.y, stroke: "#111", "stroke-width": 0.25 }));
  svg.appendChild(createSvgElement("line", { x1: right.x, y1: right.y, x2: svgHead.x, y2: svgHead.y, stroke: "#111", "stroke-width": 0.25 }));
}

function drawArrowLabel(svg, anchorId, tail) {
  const svgTail = toSvgPoint(tail);
  const label = createSvgElement("text", {
    x: svgTail.x,
    y: svgTail.y,
    "text-anchor": anchorId.includes("west") ? "end" : anchorId.includes("east") ? "start" : "middle",
    "dominant-baseline": anchorId.includes("north") ? "auto" : anchorId.includes("south") ? "hanging" : "middle",
    "font-size": 1.45,
    fill: "#111",
    class: "arrow-label",
  });
  if (anchorId === "north") {
    label.setAttribute("dominant-baseline", "auto");
  }
  label.textContent = anchorLabel(anchorId);
  svg.appendChild(label);
}

function renderCanvas() {
  const symbol = getCurrentSymbol();
  state.svg.innerHTML = "";
  drawGrid(state.svg, state.grid);
  drawIcon(state.svg, symbol);

  state.anchorOrder.forEach((anchorId) => {
    const tail = state.anchorTails[anchorId];
    const head = symbol.anchors[anchorId];
    drawOpenArrow(state.svg, tail, head);
    drawArrowLabel(state.svg, anchorId, tail);

    const handle = createSvgElement("circle", {
      cx: head.x,
      cy: toSvgY(head.y),
      r: HANDLE_RADIUS,
      fill: "#6d2f11",
      stroke: "white",
      "stroke-width": 0.35,
      class: `anchor-handle${state.dragAnchor === anchorId ? " dragging" : ""}`,
      "data-anchor-id": anchorId,
    });
    handle.addEventListener("mousedown", (event) => {
      event.preventDefault();
      state.dragAnchor = anchorId;
      renderCanvas();
    });
    state.svg.appendChild(handle);
  });
}

function svgPointFromEvent(event) {
  const point = state.svg.createSVGPoint();
  point.x = event.clientX;
  point.y = event.clientY;
  const svgPoint = point.matrixTransform(state.svg.getScreenCTM().inverse());
  return { x: svgPoint.x, y: -svgPoint.y };
}

function handlePointerMove(event) {
  if (!state.dragAnchor || !state.currentSymbolId) {
    return;
  }
  const point = svgPointFromEvent(event);
  const symbol = getCurrentSymbol();
  symbol.anchors[state.dragAnchor].x = snapValue(point.x);
  symbol.anchors[state.dragAnchor].y = snapValue(point.y);
  renderCanvas();
  refreshAnchorTable(symbol);
}

function handlePointerUp() {
  if (!state.dragAnchor) {
    return;
  }
  state.dragAnchor = null;
  renderCanvas();
}

function refreshUI() {
  const symbol = getCurrentSymbol();
  if (!symbol) {
    return;
  }
  refreshSymbolList();
  symbolTitle.textContent = symbol.label;
  iconWidthBadge.textContent = `Icon ${mm(symbol.iconWidthMm)}`;
  refreshMetricsTable(symbol);
  refreshAnchorTable(symbol);
  renderCanvas();
}

function loadState(payload) {
  state.originalSymbols = new Map(payload.symbols.map((symbol) => [symbol.id, deepCopy(symbol)]));
  state.workingSymbols = new Map(payload.symbols.map((symbol) => [symbol.id, deepCopy(symbol)]));
  state.symbolOrder = payload.symbols.map((symbol) => symbol.id);
  state.anchorOrder = payload.anchorOrder;
  state.anchorTails = payload.anchorTails;
  state.grid = payload.grid;
  state.previewOnlyNodes = payload.previewOnlyNodes;
  state.previews = payload.previews;
  state.previewError = payload.previewError;
  state.currentSymbolId = state.currentSymbolId && state.workingSymbols.has(state.currentSymbolId)
    ? state.currentSymbolId
    : state.symbolOrder[0];
  packagePath.textContent = payload.packagePath;
  refreshPreviewNodeList();
  refreshPreviewGallery(String(Date.now()));
  refreshUI();
}

async function fetchState() {
  setStatus("Loading anchor state…");
  const payload = await api("/api/state");
  loadState(payload);
  setStatus("Ready", "success");
}

async function saveChanges() {
  setStatus("Saving changes…");
  const symbols = {};
  state.symbolOrder.forEach((symbolId) => {
    symbols[symbolId] = deepCopy(state.workingSymbols.get(symbolId).anchors);
  });
  const result = await api("/api/save", {
    method: "POST",
    body: JSON.stringify({ symbols }),
  });
  loadState(result.state);
  setStatus(`Saved to package (${result.changed ? "updated" : "no textual diff"})`, "success");
}

function resetCurrentSymbol() {
  if (!state.currentSymbolId) {
    return;
  }
  state.workingSymbols.set(state.currentSymbolId, deepCopy(state.originalSymbols.get(state.currentSymbolId)));
  setStatus(`Reset ${getCurrentSymbol().label}`, "success");
  refreshUI();
}

function revertAll() {
  state.workingSymbols = new Map(
    Array.from(state.originalSymbols.entries()).map(([key, value]) => [key, deepCopy(value)]),
  );
  setStatus("Reverted unsaved changes", "success");
  refreshUI();
}

async function rebuildPreviews() {
  setStatus("Rebuilding preview images…");
  const result = await api("/api/rebuild-preview", {
    method: "POST",
    body: JSON.stringify({}),
  });
  state.previews = result.previews;
  state.previewError = result.previewError;
  refreshPreviewGallery(String(Date.now()));
  setStatus("Preview images rebuilt", "success");
}

function wireTabs() {
  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const tabId = button.dataset.tab;
      tabButtons.forEach((candidate) => candidate.classList.toggle("active", candidate === button));
      Object.entries(tabPanels).forEach(([id, panel]) => {
        panel.classList.toggle("active", id === tabId);
      });
    });
  });
}

function wireActions() {
  saveButton.addEventListener("click", async () => {
    try {
      await saveChanges();
    } catch (error) {
      setStatus(error.message, "error");
    }
  });
  resetSymbolButton.addEventListener("click", resetCurrentSymbol);
  revertAllButton.addEventListener("click", revertAll);
  rebuildPreviewsButton.addEventListener("click", async () => {
    try {
      await rebuildPreviews();
    } catch (error) {
      setStatus(error.message, "error");
    }
  });
  window.addEventListener("mousemove", handlePointerMove);
  window.addEventListener("mouseup", handlePointerUp);
}

document.addEventListener("DOMContentLoaded", async () => {
  wireTabs();
  wireActions();
  try {
    await fetchState();
  } catch (error) {
    setStatus(error.message, "error");
  }
});

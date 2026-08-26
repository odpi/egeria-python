// Dr.Egeria Spec Editor -- vanilla JS, no build step, no framework.

const STYLE_OPTIONS = [
  "Simple", "Simple Int", "Simple Float", "Simple List", "Bool", "Enum",
  "Valid Value", "QN", "GUID", "Reference Name", "Reference Name List",
  "Dictionary", "Named DICT",
];

const state = { family: null, data: null, tab: "attributes" };

function banner(kind, msg) {
  const el = document.getElementById("banner");
  el.textContent = msg;
  el.className = "banner " + kind;
  clearTimeout(banner._t);
  banner._t = setTimeout(() => { el.className = "banner hidden"; }, 5000);
}

async function api(method, url, body) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const resp = await fetch(url, opts);
  const isJson = (resp.headers.get("content-type") || "").includes("application/json");
  const data = isJson ? await resp.json() : null;
  if (!resp.ok) {
    const msg = (data && data.detail) ? data.detail : `${method} ${url} failed (${resp.status})`;
    throw new Error(msg);
  }
  return data;
}

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of [].concat(children)) node.appendChild(c);
  return node;
}

// Drag-to-resize column widths. Call once per freshly-built table, after it's
// in the DOM. `colWidths` (optional) is an array of initial CSS widths
// ('120px', '20%', ...) matching the header cell order.
function makeResizable(table, colWidths) {
  if (!table.rows.length) return;
  const ths = Array.from(table.rows[0].cells);
  ths.forEach((th, i) => {
    if (colWidths && colWidths[i]) th.style.width = colWidths[i];
    const handle = el("div", { class: "col-resize" });
    th.appendChild(handle);
    handle.addEventListener("mousedown", (e) => {
      handle.classList.add("dragging");
      const startX = e.pageX;
      const startW = th.offsetWidth;
      const onMove = (ev) => {
        const w = startW + ev.pageX - startX;
        if (w > 30) th.style.width = w + "px";
      };
      const onUp = () => {
        handle.classList.remove("dragging");
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup", onUp);
      };
      document.addEventListener("mousemove", onMove);
      document.addEventListener("mouseup", onUp);
      e.preventDefault();
    });
  });
}

function plural(n, noun, pluralNoun) {
  return n === 1 ? noun : (pluralNoun || noun + "s");
}

function rowCount(n, noun, pluralNoun) {
  return el("div", { class: "row-count", text: `${n} ${plural(n, noun, pluralNoun)}` });
}

// Adds a search box that filters `table`'s rows by substring match against
// row text, and keeps `countEl` updated with "N of Total noun(s)".
function attachSearch(container, table, countEl, total, noun, pluralNoun) {
  const input = el("input", { type: "text", class: "search-box", placeholder: `Search ${pluralNoun || noun + "s"}...` });
  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    let shown = 0;
    for (let i = 1; i < table.rows.length; i++) {
      const row = table.rows[i];
      const match = !q || row.textContent.toLowerCase().includes(q);
      row.style.display = match ? "" : "none";
      if (match) shown++;
    }
    countEl.textContent = q
      ? `${shown} of ${total} ${plural(total, noun, pluralNoun)}`
      : `${total} ${plural(total, noun, pluralNoun)}`;
  });
  container.appendChild(input);
  return input;
}

// -------------------------------------------------------------- routing

window.addEventListener("hashchange", route);
window.addEventListener("DOMContentLoaded", route);

function route() {
  const hash = location.hash.replace(/^#\/?/, "");
  if (!hash) return renderFamilyList();
  const [, family] = hash.split("/");
  if (family) return openFamily(family);
  renderFamilyList();
}

// --------------------------------------------------------- family list

async function renderFamilyList() {
  const app = document.getElementById("app");
  app.innerHTML = "";
  let families;
  try {
    families = await api("GET", "/api/families");
  } catch (e) {
    banner("error", e.message);
    return;
  }
  const toolbar = el("div", { class: "toolbar" });
  toolbar.appendChild(el("button", { class: "primary", text: "+ New Family", onclick: showNewFamilyForm }));
  app.appendChild(toolbar);
  app.appendChild(el("div", { id: "panel-host" }));

  const count = rowCount(families.length, "family", "families");
  app.appendChild(count);
  const table = el("table");
  table.appendChild(el("tr", {}, [
    el("th", { text: "Family" }), el("th", { text: "File" }),
    el("th", { text: "Attrs" }), el("th", { text: "Bundles" }), el("th", { text: "Commands" }),
  ]));
  for (const f of families) {
    const row = el("tr");
    const link = el("a", { class: "crumb", text: f.family || f.filename, onclick: () => { location.hash = `#/family/${f.filename}`; } });
    row.appendChild(el("td", {}, [link]));
    row.appendChild(el("td", { text: f.filename + ".json" }));
    row.appendChild(el("td", { text: f.error ? "parse error" : f.attribute_count }));
    row.appendChild(el("td", { text: f.error ? "" : f.bundle_count }));
    row.appendChild(el("td", { text: f.error ? "" : f.command_count }));
    table.appendChild(row);
  }
  attachSearch(app, table, count, families.length, "family", "families");
  app.appendChild(table);
  makeResizable(table, ["220px", "260px", "70px", "80px", "100px"]);
}

function showNewFamilyForm() {
  const host = document.getElementById("panel-host");
  host.innerHTML = "";
  const nameInput = el("input", { type: "text", placeholder: "e.g. Curation" });
  const panel = el("div", { class: "panel" }, [
    el("div", { class: "field" }, [el("label", { text: "Family name" }), nameInput]),
    el("button", {
      class: "primary", text: "Create", onclick: async () => {
        try {
          const created = await api("POST", "/api/families", { family: nameInput.value });
          banner("success", `Created family '${created.family}'`);
          location.hash = `#/family/${created.filename}`;
        } catch (e) { banner("error", e.message); }
      },
    }),
    el("button", { text: "Cancel", onclick: () => { host.innerHTML = ""; } }),
  ]);
  host.appendChild(panel);
}

// -------------------------------------------------------- family detail

async function openFamily(filename) {
  const app = document.getElementById("app");
  app.innerHTML = "";
  try {
    state.data = await api("GET", `/api/families/${filename}`);
  } catch (e) {
    banner("error", e.message);
    return;
  }
  state.family = filename;

  app.appendChild(el("a", { class: "crumb", text: "< All families", onclick: () => { location.hash = "#/"; } }));
  app.appendChild(el("h2", { text: `${state.data.family} (${filename}.json)` }));

  const tabs = el("div", { class: "tabs" });
  for (const t of ["attributes", "bundles", "commands"]) {
    tabs.appendChild(el("button", {
      class: t === state.tab ? "active" : "",
      text: t[0].toUpperCase() + t.slice(1),
      onclick: () => { state.tab = t; openFamily(filename); },
    }));
  }
  app.appendChild(tabs);

  const validateRow = el("div", { class: "toolbar" });
  validateRow.appendChild(el("button", { text: "Validate family", onclick: runValidate }));
  app.appendChild(validateRow);
  app.appendChild(el("div", { id: "validate-results" }));

  const body = el("div", { id: "tab-body" });
  app.appendChild(body);
  if (state.tab === "attributes") renderAttributes(body);
  if (state.tab === "bundles") renderBundles(body);
  if (state.tab === "commands") renderCommands(body);
}

async function refresh() {
  state.data = await api("GET", `/api/families/${state.family}`);
  openFamily(state.family);
}

// --------------------------------------------------------- attributes

function renderAttributes(host) {
  const attrs = state.data.attribute_definitions || {};
  const sharing = state.data.attribute_sharing || {};
  host.appendChild(el("button", { class: "primary", text: "+ New Attribute", onclick: () => showAttributeForm() }));
  host.appendChild(el("div", { id: "panel-host" }));
  const count = rowCount(Object.keys(attrs).length, "attribute");
  host.appendChild(count);

  const table = el("table");
  table.appendChild(el("tr", {}, [
    el("th", { text: "Name" }), el("th", { text: "Style" }), el("th", { text: "Variable name" }),
    el("th", { text: "Description" }), el("th", { text: "Scope" }), el("th", { text: "" }),
  ]));
  for (const [name, def] of Object.entries(attrs)) {
    const sharedWith = sharing[name] || [];
    const scopeBadge = sharedWith.length
      ? el("span", { class: "badge-shared", title: `Also defined in: ${sharedWith.join(", ")}`, text: `Shared (${sharedWith.length})` })
      : el("span", { class: "badge-own", text: "Family-only" });
    table.appendChild(el("tr", {}, [
      el("td", { text: name }),
      el("td", { text: def.style || "" }),
      el("td", { text: def.variable_name || "" }),
      el("td", { text: def.description || "" }),
      el("td", {}, [scopeBadge]),
      el("td", {}, [
        el("button", { text: "Edit", onclick: () => showAttributeForm(name, def) }),
        el("button", { class: "danger", text: "Delete", onclick: () => deleteAttribute(name) }),
      ]),
    ]));
  }
  attachSearch(host, table, count, Object.keys(attrs).length, "attribute");
  host.appendChild(table);
  makeResizable(table, ["160px", "120px", "140px", "240px", "110px", "110px"]);
}

function showAttributeForm(name, def = {}) {
  const host = document.getElementById("panel-host");
  host.innerHTML = "";
  const isEdit = !!name;
  const sharedWith = name ? (state.data.attribute_sharing || {})[name] || [] : [];

  const panelChildren = [];
  if (sharedWith.length) {
    panelChildren.push(el("div", {
      class: "warning-note",
      text: `This attribute name is also defined in ${sharedWith.length} other famil${sharedWith.length === 1 ? "y" : "ies"} (${sharedWith.join(", ")}). Editing it here only changes this family's copy — it will not update the others.`,
    }));
  }

  const nameInput = el("input", { type: "text", value: name || "" });
  if (isEdit) nameInput.setAttribute("disabled", "true");
  const varInput = el("input", { type: "text", value: def.variable_name || "" });
  const styleSelect = el("select");
  for (const s of STYLE_OPTIONS) {
    const opt = el("option", { value: s, text: s });
    if (s === def.style) opt.setAttribute("selected", "true");
    styleSelect.appendChild(opt);
  }
  const descInput = el("textarea", { text: def.description || "" });
  const requiredCheck = el("input", { type: "checkbox" });
  requiredCheck.checked = !!def.input_required;
  const minInput = el("input", { type: "number", value: def.min_cardinality ?? "" });
  const maxInput = el("input", { type: "number", value: def.max_cardinality ?? "" });
  const validValuesInput = el("input", { type: "text", value: (def.valid_values || []).join(", ") });

  const panel = el("div", { class: "panel" }, [
    ...panelChildren,
    el("div", { class: "field" }, [el("label", { text: "Name" }), nameInput]),
    el("div", { class: "field" }, [el("label", { text: "variable_name" }), varInput]),
    el("div", { class: "field" }, [el("label", { text: "style" }), styleSelect]),
    el("div", { class: "field" }, [el("label", { text: "description" }), descInput]),
    el("div", { class: "field" }, [el("label", { text: "input_required" }), requiredCheck]),
    el("div", { class: "field" }, [el("label", { text: "min_cardinality" }), minInput]),
    el("div", { class: "field" }, [el("label", { text: "max_cardinality" }), maxInput]),
    el("div", { class: "field" }, [el("label", { text: "valid_values (comma-separated; used when style is Enum/Valid Value)" }), validValuesInput]),
  ]);

  const save = el("button", {
    class: "primary", text: isEdit ? "Save" : "Create", onclick: async () => {
      const definition = {
        variable_name: varInput.value,
        style: styleSelect.value,
        description: descInput.value,
        input_required: requiredCheck.checked,
      };
      if (minInput.value !== "") definition.min_cardinality = Number(minInput.value);
      if (maxInput.value !== "") definition.max_cardinality = Number(maxInput.value);
      const vv = validValuesInput.value.split(",").map(s => s.trim()).filter(Boolean);
      if (vv.length) definition.valid_values = vv;
      try {
        if (isEdit) {
          await api("PUT", `/api/families/${state.family}/attributes/${encodeURIComponent(name)}`, { definition });
        } else {
          await api("POST", `/api/families/${state.family}/attributes`, { name: nameInput.value, definition });
        }
        banner("success", `Saved attribute '${nameInput.value}'`);
        host.innerHTML = "";
        await refresh();
      } catch (e) { banner("error", e.message); }
    },
  });
  panel.appendChild(save);
  panel.appendChild(el("button", { text: "Cancel", onclick: () => { host.innerHTML = ""; } }));
  host.appendChild(panel);
}

async function deleteAttribute(name) {
  if (!confirm(`Delete attribute '${name}'? This cannot be undone.`)) return;
  try {
    await api("DELETE", `/api/families/${state.family}/attributes/${encodeURIComponent(name)}`);
    banner("success", `Deleted attribute '${name}'`);
    await refresh();
  } catch (e) { banner("error", e.message); }
}

// ------------------------------------------------------------ bundles

function renderBundles(host) {
  const bundles = state.data.bundles || {};
  host.appendChild(el("button", { class: "primary", text: "+ New Bundle", onclick: () => showBundleForm() }));
  host.appendChild(el("div", { id: "panel-host" }));
  const count = rowCount(Object.keys(bundles).length, "bundle");
  host.appendChild(count);

  const table = el("table");
  table.appendChild(el("tr", {}, [
    el("th", { text: "Name" }), el("th", { text: "Inherits" }), el("th", { text: "Own attributes" }), el("th", { text: "" }),
  ]));
  for (const [name, def] of Object.entries(bundles)) {
    table.appendChild(el("tr", {}, [
      el("td", { text: name }),
      el("td", { text: def.inherits || "" }),
      el("td", { text: (def.own_attributes || []).join(", ") }),
      el("td", {}, [
        el("button", { text: "Edit", onclick: () => showBundleForm(name, def) }),
        el("button", { class: "danger", text: "Delete", onclick: () => deleteBundle(name) }),
      ]),
    ]));
  }
  attachSearch(host, table, count, Object.keys(bundles).length, "bundle");
  host.appendChild(table);
  makeResizable(table, ["160px", "160px", "360px", "110px"]);
}

function showBundleForm(name, def = {}) {
  const host = document.getElementById("panel-host");
  host.innerHTML = "";
  const isEdit = !!name;
  const bundleNames = Object.keys(state.data.bundles || {}).filter(b => b !== name);
  const attrNames = Object.keys(state.data.attribute_definitions || {});

  const nameInput = el("input", { type: "text", value: name || "" });
  if (isEdit) nameInput.setAttribute("disabled", "true");
  const inheritsSelect = el("select");
  inheritsSelect.appendChild(el("option", { value: "", text: "(none)" }));
  for (const b of bundleNames) {
    const opt = el("option", { value: b, text: b });
    if (b === def.inherits) opt.setAttribute("selected", "true");
    inheritsSelect.appendChild(opt);
  }
  const ownAttrs = new Set(def.own_attributes || []);
  const checklist = el("div", { class: "checkbox-list" });
  const checkboxes = [];
  for (const a of attrNames) {
    const cb = el("input", { type: "checkbox", value: a });
    cb.checked = ownAttrs.has(a);
    checkboxes.push(cb);
    const label = el("label", {}, [cb, document.createTextNode(" " + a)]);
    checklist.appendChild(label);
  }

  const panel = el("div", { class: "panel" }, [
    el("div", { class: "field" }, [el("label", { text: "Name" }), nameInput]),
    el("div", { class: "field" }, [el("label", { text: "inherits" }), inheritsSelect]),
    el("div", { class: "field" }, [el("label", { text: "own_attributes" }), checklist]),
  ]);
  panel.appendChild(el("button", {
    class: "primary", text: isEdit ? "Save" : "Create", onclick: async () => {
      const definition = {
        inherits: inheritsSelect.value || undefined,
        own_attributes: checkboxes.filter(c => c.checked).map(c => c.value),
      };
      try {
        if (isEdit) {
          await api("PUT", `/api/families/${state.family}/bundles/${encodeURIComponent(name)}`, { definition });
        } else {
          await api("POST", `/api/families/${state.family}/bundles`, { name: nameInput.value, definition });
        }
        banner("success", `Saved bundle '${nameInput.value}'`);
        host.innerHTML = "";
        await refresh();
      } catch (e) { banner("error", e.message); }
    },
  }));
  panel.appendChild(el("button", { text: "Cancel", onclick: () => { host.innerHTML = ""; } }));
  host.appendChild(panel);
}

async function deleteBundle(name) {
  if (!confirm(`Delete bundle '${name}'? This cannot be undone.`)) return;
  try {
    await api("DELETE", `/api/families/${state.family}/bundles/${encodeURIComponent(name)}`);
    banner("success", `Deleted bundle '${name}'`);
    await refresh();
  } catch (e) { banner("error", e.message); }
}

// ----------------------------------------------------------- commands

function renderCommands(host) {
  const commands = state.data.commands || {};
  host.appendChild(el("button", { class: "primary", text: "+ New Command", onclick: () => showCommandForm() }));
  host.appendChild(el("div", { id: "panel-host" }));
  const count = rowCount(Object.keys(commands).length, "command");
  host.appendChild(count);

  const table = el("table");
  table.appendChild(el("tr", {}, [
    el("th", { text: "Name" }), el("th", { text: "Verb" }), el("th", { text: "OM_TYPE" }),
    el("th", { text: "Bundle" }), el("th", { text: "" }),
  ]));
  for (const [name, def] of Object.entries(commands)) {
    table.appendChild(el("tr", {}, [
      el("td", { text: name }),
      el("td", { text: def.verb || "" }),
      el("td", { text: def.OM_TYPE || "" }),
      el("td", { text: def.bundle || "" }),
      el("td", {}, [
        el("button", { text: "Edit", onclick: () => showCommandForm(name, def) }),
        el("button", { class: "danger", text: "Delete", onclick: () => deleteCommand(name) }),
      ]),
    ]));
  }
  attachSearch(host, table, count, Object.keys(commands).length, "command");
  host.appendChild(table);
  makeResizable(table, ["200px", "100px", "160px", "180px", "110px"]);
}

function showCommandForm(name, def = {}) {
  const host = document.getElementById("panel-host");
  host.innerHTML = "";
  const isEdit = !!name;
  const bundleNames = Object.keys(state.data.bundles || {});
  const attrNames = Object.keys(state.data.attribute_definitions || {});

  const nameInput = el("input", { type: "text", value: name || "" });
  if (isEdit) nameInput.setAttribute("disabled", "true");
  const verbInput = el("input", { type: "text", value: def.verb || "" });
  const displayNameInput = el("input", { type: "text", value: def.display_name || "" });
  const qnPrefixInput = el("input", { type: "text", value: def.qn_prefix || "" });
  const omTypeInput = el("input", { type: "text", value: def.OM_TYPE || "" });
  const descInput = el("textarea", { text: def.description || "" });
  const bundleSelect = el("select");
  bundleSelect.appendChild(el("option", { value: "", text: "(none)" }));
  for (const b of bundleNames) {
    const opt = el("option", { value: b, text: b });
    if (b === def.bundle) opt.setAttribute("selected", "true");
    bundleSelect.appendChild(opt);
  }
  const upsertCheck = el("input", { type: "checkbox" });
  upsertCheck.checked = !!def.upsert;
  const attachCheck = el("input", { type: "checkbox" });
  attachCheck.checked = !!def.attach;

  const customAttrs = new Set(def.custom_attributes || []);
  const checklist = el("div", { class: "checkbox-list" });
  const checkboxes = [];
  for (const a of attrNames) {
    const cb = el("input", { type: "checkbox", value: a });
    cb.checked = customAttrs.has(a);
    checkboxes.push(cb);
    checklist.appendChild(el("label", {}, [cb, document.createTextNode(" " + a)]));
  }

  const panel = el("div", { class: "panel" }, [
    el("div", { class: "field" }, [el("label", { text: "Name" }), nameInput]),
    el("div", { class: "field" }, [el("label", { text: "verb" }), verbInput]),
    el("div", { class: "field" }, [el("label", { text: "display_name" }), displayNameInput]),
    el("div", { class: "field" }, [el("label", { text: "qn_prefix" }), qnPrefixInput]),
    el("div", { class: "field" }, [el("label", { text: "OM_TYPE" }), omTypeInput]),
    el("div", { class: "field" }, [el("label", { text: "description" }), descInput]),
    el("div", { class: "field" }, [el("label", { text: "bundle" }), bundleSelect]),
    el("div", { class: "field" }, [el("label", { text: "upsert" }), upsertCheck]),
    el("div", { class: "field" }, [el("label", { text: "attach" }), attachCheck]),
    el("div", { class: "field" }, [el("label", { text: "custom_attributes (beyond the bundle)" }), checklist]),
  ]);
  panel.appendChild(el("button", {
    class: "primary", text: isEdit ? "Save" : "Create", onclick: async () => {
      const definition = {
        ...def,
        verb: verbInput.value,
        display_name: displayNameInput.value,
        qn_prefix: qnPrefixInput.value,
        OM_TYPE: omTypeInput.value,
        family: state.data.family,
        description: descInput.value,
        bundle: bundleSelect.value || undefined,
        upsert: upsertCheck.checked,
        attach: attachCheck.checked,
        custom_attributes: checkboxes.filter(c => c.checked).map(c => c.value),
      };
      try {
        if (isEdit) {
          await api("PUT", `/api/families/${state.family}/commands/${encodeURIComponent(name)}`, { definition });
        } else {
          await api("POST", `/api/families/${state.family}/commands`, { name: nameInput.value, definition });
        }
        banner("success", `Saved command '${nameInput.value}'`);
        host.innerHTML = "";
        await refresh();
      } catch (e) { banner("error", e.message); }
    },
  }));
  panel.appendChild(el("button", { text: "Cancel", onclick: () => { host.innerHTML = ""; } }));
  host.appendChild(panel);
}

async function deleteCommand(name) {
  if (!confirm(`Delete command '${name}'? This cannot be undone.`)) return;
  try {
    await api("DELETE", `/api/families/${state.family}/commands/${encodeURIComponent(name)}`);
    banner("success", `Deleted command '${name}'`);
    await refresh();
  } catch (e) { banner("error", e.message); }
}

// ----------------------------------------------------------- validate

async function runValidate() {
  const host = document.getElementById("validate-results");
  host.innerHTML = "Validating...";
  try {
    const result = await api("POST", `/api/validate/${state.family}`);
    host.innerHTML = "";
    const list = el("ul", { class: "findings" });
    if (!result.findings.length) {
      list.appendChild(el("li", { text: "No findings from compact_spec_validator." }));
    }
    for (const f of result.findings) {
      list.appendChild(el("li", { class: f.severity, text: `[${f.severity}] ${f.code} (${f.command_name} in ${f.file}): ${f.message}` }));
    }
    host.appendChild(el("h2", { text: result.structural_ok ? "Structural check: OK" : "Structural check: ERRORS" }));
    host.appendChild(list);
    if (!result.structural_ok) {
      host.appendChild(el("pre", { text: result.structural_output }));
    }
  } catch (e) {
    host.innerHTML = "";
    banner("error", e.message);
  }
}

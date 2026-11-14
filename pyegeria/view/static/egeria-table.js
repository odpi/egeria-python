/* SPDX-License-Identifier: Apache-2.0
 * Copyright Contributors to the ODPi Egeria project.
 *
 * egeria-table.js -- one renderer for pyegeria's structured TABLE result
 * (exec_report_spec(..., output_format="TABLE", table_shape="structured"),
 * pyegeria >= 6.2.37; DESIGN-REPORT-SPEC-COMPLEX-VALUES-RENDERING-2026-11-11
 * section 2.2-2.5):
 *
 *   {kind: "table",
 *    columns: [{key, name, type, render, detail_spec, valid_values,
 *               max_items, max_lines, label?}],
 *    rows: [{key: native value}],
 *    total: int|null, total_basis: "one page"|..., shown: int,
 *    notes: ["..."]}
 *
 * Standalone on purpose: no framework, no build step, and NO globals from the
 * host page (the Egeria Portal loads it with a <script>; trellis-ui vendors it
 * unchanged for Egeria Advisor). It defines exactly one global, EgeriaTable,
 * or a CommonJS export under node.
 *
 *   EgeriaTable.renderHtml(result, opts) -> HTML string
 *   EgeriaTable.attach(root, opts)       -> wires "more"/"less" and the
 *                                           subtable rows inside root; returns
 *                                           a function that unwires them
 *   EgeriaTable.render(result, opts)     -> a <div> (needs a DOM), attached
 *   EgeriaTable.trim(root)               -> hide "more" where text was not cut
 *                                           (for a page that attached once, at
 *                                           its body, and renders tables later)
 *   EgeriaTable.CSS                       -> the stylesheet (injected once by
 *                                           attach/render; ensureStyles(doc))
 *
 *   opts.linkBuilder(element, column) -> URL string or null. Called for each
 *     related element ({guid, qualifiedName, displayName, type}). Without it,
 *     names are plain text and their title says there is no link. Only a
 *     relative or http(s) URL is used; any other is plain text with a note.
 *
 * Rendering (section 2.5, Portal column):
 *   text      clamped to max_lines (default 3) with "more" / "less"
 *   join      "a, b, c" then "+N more" (the rest, expandable) past max_items (10)
 *   bullets   a <ul> in the cell (past max_items: the rest, expandable)
 *   kv        a two-column mini table in the cell
 *   subtable  "N rows" with a row toggle; the nested table opens under the row
 *   count     "N", with the first names as a tooltip
 *   link      the element's link from linkBuilder
 *   elements are shown by column.label (default displayName), QN as tooltip.
 *
 * The two-level rule (section 2.4): an object inside a subtable, kv or bullet
 * cell is never a third table; it is "count + names" (with a link when it
 * names one element) and the footer says so.
 *
 * Absence is an answer: nothing is dropped or capped without words on screen.
 * There is no column cap (the table scrolls sideways) and no row cap (pyegeria
 * pages; every row the result carries is shown). The footer says "first N of
 * M", "first N; more may exist" or "N rows (one page; Egeria doesn't promise
 * it is the last)" -- "All N of N" only for a total_basis that proves it
 * ("counted", "paged to empty") -- never a bare N, then every pyegeria note
 * and every note of this renderer. An empty relationship list ([]) reads
 * "none"; a missing value (null) reads as a dash and the notes say why.
 *
 * Everything is text-escaped. Markdown is not interpreted. The one exception
 * (#846's rule): in a render "text" cell, an exact <br>, <br/> or <br /> from
 * pyegeria's 6.2.37 F9 path is a line break; a newline is one too.
 *
 * Column widths: every header cell is a plain <th>, so egeria-resize.js (load
 * it on the page) makes each column draggable; cell content wraps.
 */
(function (root, factory) {
  'use strict';
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.EgeriaTable = api;
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var DEFAULT_MAX_ITEMS = 10;
  var DEFAULT_MAX_LINES = 3;
  var CHARS_PER_LINE = 60;     // a string-only guess at "longer than max_lines"; attach() measures
  var WIDE_COLS = 5;           // from this many columns the table keeps a minimum column width and scrolls
  var NO_LINK = 'No link: this page gave the table no link builder.';
  var STYLE_ID = 'egeria-table-css';
  var REFUSED_LINK = 'A link was not shown: only relative, http and https links are allowed.';
  // total_basis values that prove the total is every row; any other basis
  // (today pyegeria's "one page") does not: Egeria's paging contract does not
  // promise that a short page is the last one, only an empty page is.
  var COMPLETE_BASES = ['counted', 'paged to empty'];

  var CSS = [
    '.et { font-size: 12px; line-height: 1.45; }',
    '.et-scroll { overflow: auto; max-width: 100%; }',
    '.et-table { border-collapse: separate; border-spacing: 0; width: 100%; }',
    '.et-table.et-wide { min-width: calc(var(--et-cols) * 140px); }',
    '.et-table th, .et-table td { padding: 5px 8px; text-align: left; vertical-align: top;',
    '  border-right: 1px solid var(--border, #d0d7de); border-bottom: 1px solid var(--border, #d0d7de);',
    '  overflow-wrap: anywhere; white-space: normal; }',
    '.et-table > thead > tr > th { position: sticky; top: 0; z-index: 1; background: var(--card, #fff);',
    '  font-weight: 600; border-top: 1px solid var(--border, #d0d7de); }',
    '.et-table th:first-child, .et-table td:first-child { border-left: 1px solid var(--border, #d0d7de); }',
    '.et-table > thead > tr > th { min-width: 6em; }',
    // Long text and lists keep a readable measure, so a wide table scrolls
    // instead of one prose column taking the width and squeezing the rest.
    '.et-text, .et-bullets, .et-rest { max-width: 32em; min-width: 12em; }',
    '.et-text { white-space: pre-line; }',
    '.et-text:not(.et-clamp) { min-width: 0; }',
    '.et-clamp { display: -webkit-box; -webkit-box-orient: vertical; overflow: hidden; }',
    '.et-clamp.et-open { display: block; -webkit-line-clamp: unset !important; }',
    '.et-btn { background: none; border: 0; padding: 0; margin: 0; cursor: pointer; font: inherit;',
    '  color: var(--accent, #0969da); }',
    '.et-btn:hover { text-decoration: underline; }',
    '.et-bullets { margin: 0; padding-left: 1.2em; }',
    '.et-bullets li { margin: 0 0 2px; }',
    '.et-rest > summary { cursor: pointer; color: var(--accent, #0969da); list-style: none; display: inline; }',
    '.et-rest > summary::-webkit-details-marker { display: none; }',
    '.et-rest[open] > summary { display: none; }',
    'details.et-rest { display: inline; }',
    'ul + details.et-rest, details.et-rest.et-block { display: block; }',
    '.et-kv { border-collapse: collapse; font-size: 11px; }',
    '.et-kv td { border: 1px solid var(--border, #d0d7de); padding: 2px 5px; vertical-align: top; }',
    '.et-kv td:first-child { color: var(--muted, #57606a); white-space: nowrap; }',
    '.et-muted, .et-none { color: var(--muted, #57606a); }',
    '.et-sub > td { background: var(--subtle, rgba(127,127,127,.06)); }',
    '.et-sub-title { font-weight: 600; margin: 2px 0 6px; }',
    '.et-sub .et-table.et-wide { min-width: calc(var(--et-cols) * 120px); }',
    '.et-foot { margin-top: 6px; color: var(--muted, #57606a); }',
    '.et-foot ul { margin: 4px 0 0; padding-left: 1.2em; }',
  ].join('\n');

  /* ── Small helpers ────────────────────────────────────────────────────── */

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  // After escaping, turn back ONLY the exact escaped forms of <br>, <br/>,
  // <br />. "&lt;br&gt;" written as text was escaped to "&amp;lt;br&amp;gt;"
  // and does not match, so it stays visible text.
  function restoreBreaks(s) { return s.replace(/&lt;br( ?\/)?&gt;/g, '<br>'); }

  function isObj(v) { return v !== null && typeof v === 'object' && !Array.isArray(v); }
  function isEmpty(v) { return v === null || v === undefined || v === ''; }
  function isElement(v) { return isObj(v) && !!(v.guid || v.qualifiedName); }
  function isReduced(v) { return isObj(v) && typeof v.count === 'number' && Array.isArray(v.names); }
  // A link from the host's linkBuilder is used only when it is relative
  // (same host) or http(s). Browsers ignore control characters and whitespace inside a
  // scheme ("java\tscript:"), so those are removed before the check.
  function safeHref(href) {
    if (typeof href !== 'string') return false;
    var h = href.replace(/[\u0000-\u0020\u007f-\u009f]/g, '');
    if (!h) return false;
    // Protocol-relative ("//host", and browsers read "\\host", "/\\host" and
    // "\\/host" the same way) points at another host: not a relative link.
    if (/^[\/\\]{2}/.test(h)) return false;
    var scheme = /^([a-z][a-z0-9+.-]*):/i.exec(h);
    return scheme ? /^https?$/i.test(scheme[1]) : true;
  }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : (many || one + 's')); }
  function posInt(v, dflt) { return (typeof v === 'number' && v > 0) ? Math.floor(v) : dflt; }

  function scalarText(v) {
    if (v === true) return 'true';
    if (v === false) return 'false';
    return String(v);                 // 0 stays "0": never dropped
  }

  // A column's `label` (pyegeria Column.label / related_label) names which name an element shows:
  // "qualified_name" or "display_name"; an element's own key (e.g. "qualifiedName") also works.
  var LABEL_KEYS = { qualified_name: 'qualifiedName', display_name: 'displayName' };

  function nameOf(item, labelKey) {
    if (!isObj(item)) return scalarText(item);
    if (labelKey && LABEL_KEYS[labelKey]) labelKey = LABEL_KEYS[labelKey];
    var n = (labelKey && item[labelKey]) || item.displayName || item.name || item.qualifiedName ||
            item['Display Name'] || item['Qualified Name'];
    return n ? String(n) : '(unnamed)';
  }

  /* ── Context: options plus the renderer's own notes ───────────────────── */

  function Ctx(opts) {
    this.linkBuilder = opts && typeof opts.linkBuilder === 'function' ? opts.linkBuilder : null;
    this.notes = [];
    this.seq = 0;
  }
  Ctx.prototype.note = function (text) { if (this.notes.indexOf(text) < 0) this.notes.push(text); };
  Ctx.prototype.id = function () { this.seq += 1; return this.seq; };

  /* ── Elements, names, links ───────────────────────────────────────────── */

  function elementHtml(el, col, ctx) {
    var name = nameOf(el, col && col.label);
    var qn = el.qualifiedName || '';
    var href = null;
    if (ctx.linkBuilder) {
      try { href = ctx.linkBuilder(el, col); } catch (e) { href = null; }
    }
    var refused = href ? !safeHref(href) : false;
    if (href && !refused) {
      return '<a href="' + esc(href) + '" title="' + esc(qn || name) + '">' + esc(name) + '</a>';
    }
    if (refused) ctx.note(REFUSED_LINK);
    var title = (qn ? qn + ' — ' : '') +
                (refused ? REFUSED_LINK : ctx.linkBuilder ? 'No link for this element.' : NO_LINK);
    return '<span title="' + esc(title) + '">' + esc(name) + '</span>';
  }

  // A third-level value (an object, or a list holding objects) as
  // "count + names", linked when it names one element. reducedBy names who
  // reduced it: pyegeria already noted its own reductions.
  function reducedHtml(value, where, col, ctx) {
    var r;
    if (isReduced(value)) {
      r = value;
    } else {
      var items = Array.isArray(value) ? value : [value];
      r = { count: items.length, names: items.map(function (i) { return nameOf(i); }) };
      if (items.length === 1 && isObj(items[0]) && items[0].guid) r.guid = items[0].guid;
      ctx.note(where + ' holds a third level, shown as a count and names (a table shows two levels).');
    }
    var names = r.names.join(', ');
    var label = r.count + (names ? ': ' + names : '');
    if (r.guid && r.count === 1 && ctx.linkBuilder) {
      return elementHtml({ guid: r.guid, displayName: label }, col, ctx);
    }
    return '<span title="' + esc(names) + '">' + esc(label) + '</span>';
  }

  /* ── Cell renderers ───────────────────────────────────────────────────── */

  function textHtml(value, col) {
    var s = scalarText(value);
    var lines = posInt(col && col.max_lines, DEFAULT_MAX_LINES);
    var body = restoreBreaks(esc(s));
    var breaks = (s.match(/\n|<br ?\/?>/g) || []).length;
    var long = breaks >= lines || s.length > lines * CHARS_PER_LINE;
    if (!long) return '<div class="et-text">' + body + '</div>';
    return '<div class="et-text et-clamp" style="-webkit-line-clamp:' + lines + '" data-et-lines="' + lines + '">' +
           body + '</div><button type="button" class="et-btn" data-et-more aria-expanded="false">more</button>';
  }

  function itemHtml(item, where, col, ctx) {
    if (isElement(item)) return elementHtml(item, col, ctx);
    if (isObj(item) || Array.isArray(item)) return reducedHtml(item, where, col, ctx);
    return esc(scalarText(item));
  }

  function restHtml(hidden, n, block) {
    return '<details class="et-rest' + (block ? ' et-block' : '') + '"><summary>+' + n + ' more</summary>' +
           hidden + '</details>';
  }

  function joinHtml(list, col, ctx) {
    var max = posInt(col && col.max_items, DEFAULT_MAX_ITEMS);
    var where = (col && col.name) || 'A cell';
    var parts = list.map(function (i) { return itemHtml(i, where, col, ctx); });
    if (parts.length <= max) return parts.join(', ');
    return parts.slice(0, max).join(', ') + ' ' + restHtml(', ' + parts.slice(max).join(', '), parts.length - max);
  }

  function bulletsHtml(list, col, ctx) {
    var max = posInt(col && col.max_items, DEFAULT_MAX_ITEMS);
    var where = (col && col.name) || 'A cell';
    var li = list.map(function (i) {
      return '<li>' + itemHtml(i, where, col, ctx) + '</li>';
    });
    if (li.length <= max) return '<ul class="et-bullets">' + li.join('') + '</ul>';
    return '<ul class="et-bullets">' + li.slice(0, max).join('') + '</ul>' +
           restHtml('<ul class="et-bullets">' + li.slice(max).join('') + '</ul>', li.length - max, true);
  }

  function kvHtml(map, col, ctx) {
    var where = (col && col.name) || 'A cell';
    var keys = Object.keys(map);
    if (!keys.length) return '<span class="et-none">none</span>';
    return '<table class="et-kv" data-no-col-resize><tbody>' + keys.map(function (k) {
      var v = map[k];
      var cell = isEmpty(v) ? '<span class="et-muted">—</span>'
        : (isObj(v) || Array.isArray(v)) ? (Array.isArray(v) && v.every(function (x) { return !isObj(x) && !Array.isArray(x); })
            ? esc(v.map(scalarText).join(', ')) : itemHtml(v, where + ' · ' + k, col, ctx))
        : esc(scalarText(v));
      return '<tr><td>' + esc(k) + '</td><td>' + cell + '</td></tr>';
    }).join('') + '</tbody></table>';
  }

  function countHtml(value, col) {
    var max = posInt(col && col.max_items, DEFAULT_MAX_ITEMS);
    var n, names;
    if (isReduced(value)) { n = value.count; names = value.names; }
    else { var list = Array.isArray(value) ? value : [value]; n = list.length; names = list.map(function (i) { return nameOf(i, col && col.label); }); }
    var tip = names.slice(0, max).join(', ') + (names.length > max ? ', +' + (names.length - max) + ' more' : '');
    return '<span title="' + esc(tip) + '">' + n + '</span>';
  }

  function linkHtml(value, col, ctx) {
    if (Array.isArray(value)) return joinHtml(value, col, ctx);
    if (isElement(value)) return elementHtml(value, col, ctx);
    return esc(scalarText(value));
  }

  // The render a value actually gets: the column's own when the value fits
  // it, else the one its shape calls for (and a note says so).
  var RENDERS = ['text', 'join', 'bullets', 'kv', 'subtable', 'count', 'link'];

  function shapeRender(v) {
    if (Array.isArray(v)) {
      if (v.every(isElement)) return 'join';
      if (v.some(function (x) { return isObj(x) || Array.isArray(x); })) return 'subtable';
      return 'bullets';
    }
    if (isReduced(v)) return 'count';
    if (isElement(v)) return 'link';
    if (isObj(v)) return 'kv';
    return 'text';
  }

  function fits(render, v) {
    switch (render) {
      case 'text': return !isObj(v) && !Array.isArray(v);
      case 'join': case 'bullets': return Array.isArray(v) || !isObj(v);
      case 'kv': return isObj(v) && !isElement(v) && !isReduced(v);
      case 'subtable': return Array.isArray(v) || (isObj(v) && !isElement(v) && !isReduced(v));
      case 'count': return Array.isArray(v) || isReduced(v) || isElement(v);
      case 'link': return isElement(v) || (Array.isArray(v) && v.every(isElement)) || !isObj(v);
      default: return false;
    }
  }

  function cellHtml(value, col, row, rowIdx, ctx, sub) {
    if (Array.isArray(value) && value.length === 0) return '<span class="et-none">none</span>';
    if (isEmpty(value)) return '<span class="et-muted" title="No value in this row (the notes say why, where pyegeria knows).">—</span>';
    var render = col.render;
    if (RENDERS.indexOf(render) < 0) {
      ctx.note((col.name || col.key) + ': render "' + render + '" is not known here; shown by its value\'s shape.');
      render = shapeRender(value);
    } else if (!fits(render, value)) {
      ctx.note((col.name || col.key) + ': some values do not fit render "' + render + '"; those are shown by their shape.');
      render = shapeRender(value);
    }
    switch (render) {
      case 'text': return textHtml(value, col);
      case 'join': return joinHtml(Array.isArray(value) ? value : [value], col, ctx);
      case 'bullets': return bulletsHtml(Array.isArray(value) ? value : [value], col, ctx);
      case 'kv': return kvHtml(value, col, ctx);
      case 'count': return countHtml(value, col);
      case 'link': return linkHtml(value, col, ctx);
      case 'subtable': {
        var n = Array.isArray(value) ? value.length : 1;
        var id = sub.add(value, col, row);
        return '<button type="button" class="et-btn" data-et-sub="' + id + '" aria-expanded="false">▸ ' +
               plural(n, 'row') + '</button>';
      }
    }
    return esc(scalarText(value));
  }

  /* ── Subtables (level 2) ──────────────────────────────────────────────── */

  function rowName(row, columns) {
    var v = row.display_name || row.displayName || row.name || row.qualified_name || row.qualifiedName;
    if (!isEmpty(v) && !isObj(v)) return scalarText(v);
    for (var i = 0; i < columns.length; i++) {
      var c = row[columns[i].key];
      if (!isEmpty(c) && !isObj(c) && !Array.isArray(c)) return scalarText(c);
    }
    return '(row)';
  }

  // The sub-rows' columns: the keys the sub-rows carry (pyegeria builds them
  // from the column's detail_spec), in first-seen order.
  function subColumns(rows) {
    var keys = [];
    rows.forEach(function (r) {
      if (isObj(r)) Object.keys(r).forEach(function (k) { if (keys.indexOf(k) < 0) keys.push(k); });
    });
    return keys;
  }

  function subtableHtml(value, col, parentName, ctx) {
    var rows = Array.isArray(value) ? value : [value];
    var objs = rows.filter(isObj);
    var title = '<div class="et-sub-title">' + esc(parentName + ' · ' + (col.name || col.key)) +
                (col.detail_spec ? ' <span class="et-muted">(' + esc(col.detail_spec) + ')</span>' : '') + '</div>';
    if (!objs.length) {                     // a list of scalars or lists: shown as bullets
      return title + bulletsHtml(rows, col, ctx);
    }
    var keys = subColumns(objs);
    var where = (col.name || col.key) + ' · ';
    var html = title + '<div class="et-scroll"><table class="et-table' + (keys.length >= WIDE_COLS ? ' et-wide' : '') +
               '" style="--et-cols:' + keys.length + '"><thead><tr>' +
               keys.map(function (k) { return '<th>' + esc(k) + '</th>'; }).join('') + '</tr></thead><tbody>';
    rows.forEach(function (r) {
      if (!isObj(r)) {
        html += '<tr><td colspan="' + keys.length + '">' + itemHtml(r, where + 'row', col, ctx) + '</td></tr>';
        return;
      }
      html += '<tr>' + keys.map(function (k) {
        var v = r[k];
        var inner;
        if (Array.isArray(v) && v.length === 0) inner = '<span class="et-none">none</span>';
        else if (isEmpty(v)) inner = '<span class="et-muted">—</span>';
        else if (isObj(v) || (Array.isArray(v) && v.some(function (x) { return isObj(x) || Array.isArray(x); }))) {
          inner = reducedHtml(v, where + k, col, ctx);           // the two-level rule
        } else if (Array.isArray(v)) inner = esc(v.map(scalarText).join(', '));
        else inner = textHtml(v, { max_lines: col.max_lines });
        return '<td>' + inner + '</td>';
      }).join('') + '</tr>';
    });
    return html + '</tbody></table></div>';
  }

  /* ── The table ────────────────────────────────────────────────────────── */

  function footerHtml(result, ctx) {
    var shown = typeof result.shown === 'number' ? result.shown : (result.rows || []).length;
    var total = result.total;
    var basis = result.total_basis ? String(result.total_basis) : '';
    var line;
    if (typeof total !== 'number') line = 'First ' + shown + '; more may exist.';
    else if (total > shown) line = 'First ' + shown + ' of ' + total + '.';
    else if (shown === 0) line = 'No rows.';                  // an empty page: the paging contract's "done"
    else if (COMPLETE_BASES.indexOf(basis) >= 0) line = 'All ' + shown + ' of ' + total + ' rows (' + basis + ').';
    else if (basis === 'one page') line = plural(shown, 'row') + " (one page; Egeria doesn't promise it is the last).";
    else line = plural(shown, 'row') + ' (' + (basis ? basis + '; ' : '') + 'not shown to be every row).';
    var notes = (Array.isArray(result.notes) ? result.notes : []).map(String).concat(ctx.notes);
    var html = '<div class="et-foot"><div class="et-count">' + esc(line) + '</div>';
    if (notes.length) html += '<ul class="et-notes">' + notes.map(function (n) { return '<li>' + esc(n) + '</li>'; }).join('') + '</ul>';
    return html + '</div>';
  }

  function renderHtml(result, opts) {
    var ctx = new Ctx(opts);
    if (!isObj(result) || result.kind !== 'table' || !Array.isArray(result.columns)) {
      return '<div class="et"><div class="et-foot">Not a structured table result (kind ' +
             esc(isObj(result) ? result.kind : typeof result) + '); nothing to show here.</div></div>';
    }
    var columns = result.columns.filter(isObj);
    var rows = Array.isArray(result.rows) ? result.rows : [];
    var nCols = columns.length;
    var subs = [];
    var sub = { add: function (value, col, row) { var id = ctx.id(); subs.push({ id: id, value: value, col: col, row: row }); return id; } };

    var html = '<div class="et" data-et-table><div class="et-scroll"><table class="et-table' +
               (nCols >= WIDE_COLS ? ' et-wide' : '') + '" style="--et-cols:' + nCols + '"><thead><tr>' +
               columns.map(function (c) {
                 var tip = [c.key, c.type, c.render].filter(Boolean).join(' · ');
                 return '<th title="' + esc(tip) + '">' + esc(c.name || c.key) + '</th>';
               }).join('') + '</tr></thead><tbody>';
    if (!rows.length) {
      html += '<tr><td colspan="' + Math.max(nCols, 1) + '" class="et-muted">No rows.</td></tr>';
    }
    rows.forEach(function (row, i) {
      if (!isObj(row)) return;
      subs.length = 0;
      html += '<tr>' + columns.map(function (c) {
        return '<td>' + cellHtml(row[c.key], c, row, i, ctx, sub) + '</td>';
      }).join('') + '</tr>';
      var name = rowName(row, columns);
      subs.slice().forEach(function (s) {
        html += '<tr class="et-sub" data-et-sub-row="' + s.id + '" hidden><td colspan="' + nCols + '">' +
                subtableHtml(s.value, s.col, name, ctx) + '</td></tr>';
      });
    });
    var bad = rows.filter(function (r) { return !isObj(r); }).length;
    if (bad) ctx.note(plural(bad, 'row') + ' in the result ' + (bad === 1 ? 'is' : 'are') + ' not an object and ' + (bad === 1 ? 'is' : 'are') + ' not shown.');
    html += '</tbody></table></div>' + footerHtml(result, ctx) + '</div>';
    return html;
  }

  /* ── Interactions ─────────────────────────────────────────────────────── */

  function ensureStyles(doc) {
    if (!doc || !doc.createElement || (doc.getElementById && doc.getElementById(STYLE_ID))) return;
    var style = doc.createElement('style');
    style.id = STYLE_ID;
    style.textContent = CSS;
    (doc.head || doc.documentElement || doc.body).appendChild(style);
  }

  function closestAttr(el, attr, stop) {
    while (el && el !== stop) {
      if (el.getAttribute && el.getAttribute(attr) !== null) return el;
      el = el.parentNode;
    }
    return null;
  }

  function onClick(root, ev) {
    var more = closestAttr(ev.target, 'data-et-more', root);
    if (more) {
      var box = more.previousElementSibling || more.previousSibling;
      var open = more.getAttribute('aria-expanded') === 'true';
      if (box && box.classList) box.classList.toggle('et-open', !open);
      more.setAttribute('aria-expanded', open ? 'false' : 'true');
      more.textContent = open ? 'more' : 'less';
      return;
    }
    var btn = closestAttr(ev.target, 'data-et-sub', root);
    if (btn) {
      var id = btn.getAttribute('data-et-sub');
      // Sub-row ids restart in every rendered table, so look only inside the
      // table this button belongs to (a page may attach once, at its body).
      var scope = closestAttr(btn, 'data-et-table', null) || root;
      var tr = scope.querySelector('tr[data-et-sub-row="' + id + '"]');
      if (!tr) return;
      var opened = btn.getAttribute('aria-expanded') === 'true';
      if (opened) tr.setAttribute('hidden', ''); else tr.removeAttribute('hidden');
      btn.setAttribute('aria-expanded', opened ? 'false' : 'true');
      btn.textContent = (opened ? '▸ ' : '▾ ') + btn.textContent.slice(2);
    }
  }

  // Hide "more" where the clamped text was not cut after all (the string
  // render only guesses from the length; here the browser has laid it out).
  function trimToggles(root) {
    var boxes = root.querySelectorAll ? root.querySelectorAll('.et-clamp') : [];
    for (var i = 0; i < boxes.length; i++) {
      var b = boxes[i];
      if (b.clientHeight && b.scrollHeight <= b.clientHeight + 1) {
        var btn = b.nextElementSibling;
        if (btn && btn.getAttribute && btn.getAttribute('data-et-more') !== null) btn.setAttribute('hidden', '');
      }
    }
  }

  function attach(root, opts) {
    if (!root || !root.addEventListener) return function () {};
    ensureStyles(root.ownerDocument);
    var handler = function (ev) { onClick(root, ev); };
    root.addEventListener('click', handler);
    trimToggles(root);
    return function () { root.removeEventListener('click', handler); };
  }

  function render(result, opts) {
    var doc = (opts && opts.document) || (typeof document !== 'undefined' ? document : null);
    if (!doc) throw new Error('EgeriaTable.render needs a DOM document; use renderHtml() and attach() instead.');
    var div = doc.createElement('div');
    div.innerHTML = renderHtml(result, opts);
    var node = div.firstChild;
    attach(node, opts);
    return node;
  }

  return {
    renderHtml: renderHtml, attach: attach, render: render, ensureStyles: ensureStyles, CSS: CSS,
    trim: trimToggles,
    esc: esc, DEFAULT_MAX_ITEMS: DEFAULT_MAX_ITEMS, DEFAULT_MAX_LINES: DEFAULT_MAX_LINES,
  };
}));

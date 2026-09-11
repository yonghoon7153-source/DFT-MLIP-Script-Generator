/* compare.js — 비교표 거르기·정렬. 행을 DOM 에 두고 숨기거나 순서만 바꾼다 (다시 그리지 않는다).
 * 정렬 키는 서버가 tr 의 data-upper(상한 전압 vs. Li/Li⁺) · data-cutoff(formation cut-off) · data-updated 에 넣어 둔 값이다.
 * 우리 행(data-ours=1)은 항상 맨 위에 둔다. */
(function () {
  "use strict";
  var q = document.getElementById("cmp-q");
  var table = document.getElementById("cmp-table");
  if (!table) return;
  var body = table.tBodies[0];
  var rows = Array.prototype.slice.call(body.rows);
  rows.forEach(function (r) { r.setAttribute("data-s", r.textContent.toLowerCase()); });
  var flt = "all", sortKey = "upper";

  function apply() {
    var v = (q && q.value || "").trim().toLowerCase();
    rows.forEach(function (r) {
      var ok = (!v || r.getAttribute("data-s").indexOf(v) >= 0);
      if (ok && flt !== "all" && r.getAttribute("data-ours") !== "1") {
        if (flt === "in") ok = r.getAttribute("data-form") === "in";
        else ok = r.getAttribute("data-main") === flt;
      }
      r.hidden = !ok;
    });
  }
  function sortRows() {
    var sorted = rows.slice().sort(function (a, b) {
      var oa = a.getAttribute("data-ours") === "1", ob = b.getAttribute("data-ours") === "1";
      if (oa !== ob) return oa ? -1 : 1;
      if (sortKey === "updated") return (b.getAttribute("data-updated") || "").localeCompare(a.getAttribute("data-updated") || "");
      var ka = parseFloat(a.getAttribute("data-" + sortKey)), kb = parseFloat(b.getAttribute("data-" + sortKey));
      if (isNaN(ka)) ka = -1; if (isNaN(kb)) kb = -1;
      return kb - ka;                                   // 내림차순 — 높은 전압이 위
    });
    sorted.forEach(function (r) { body.appendChild(r); });
  }
  if (q) q.addEventListener("input", apply);
  Array.prototype.forEach.call(document.querySelectorAll("[data-sort]"), function (b) {
    b.addEventListener("click", function () {
      sortKey = b.getAttribute("data-sort");
      Array.prototype.forEach.call(document.querySelectorAll("[data-sort]"), function (x) { x.classList.toggle("is-on", x === b); });
      sortRows();
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll("[data-flt]"), function (b) {
    b.addEventListener("click", function () {
      flt = b.getAttribute("data-flt");
      Array.prototype.forEach.call(document.querySelectorAll("[data-flt]"), function (x) { x.classList.toggle("is-on", x === b); });
      apply();
    });
  });
  sortRows(); apply();
})();

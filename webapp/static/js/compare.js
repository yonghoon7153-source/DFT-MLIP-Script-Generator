/* compare.js — 비교표 거르기. 행을 DOM 에 두고 숨긴다 (다시 그리지 않는다). */
(function () {
  "use strict";
  var q = document.getElementById("cmp-q");
  var table = document.getElementById("cmp-table");
  if (!q || !table) return;
  var rows = Array.prototype.slice.call(table.tBodies[0].rows);
  rows.forEach(function (r) { r.setAttribute("data-s", r.textContent.toLowerCase()); });
  q.addEventListener("input", function () {
    var v = q.value.trim().toLowerCase();
    rows.forEach(function (r) { r.hidden = !!v && r.getAttribute("data-s").indexOf(v) < 0; });
  });
})();

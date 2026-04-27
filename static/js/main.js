"use strict";

const patternInput = document.getElementById("pattern");
const textInput = document.getElementById("text");
const runBtn = document.getElementById("run-btn");

const errorBox = document.getElementById("error-box");
const highlightBox = document.getElementById("highlight-box");
const highlightedText = document.getElementById("highlighted-text");
const resultsBox = document.getElementById("results-box");
const resultsTableBody = document.querySelector("#results-table tbody");
const noMatchBox = document.getElementById("no-match-box");

// Run on button click
runBtn.addEventListener("click", runMatch);

// Run on Enter in pattern field
patternInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") runMatch();
});

async function runMatch() {
  const pattern = patternInput.value.trim();
  const text = textInput.value;
  const mode = document.querySelector('input[name="mode"]:checked').value;

  resetOutput();

  if (!pattern) {
    showError("Please enter a pattern.");
    return;
  }

  let data;
  try {
    const response = await fetch("/api/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pattern, text, mode }),
    });
    data = await response.json();
  } catch (err) {
    showError("Network error: " + err.message);
    return;
  }

  if (data.error) {
    showError(data.error);
    return;
  }

  if (!data.results || data.results.length === 0) {
    noMatchBox.classList.remove("hidden");
    return;
  }

  renderHighlights(text, data.results);
  renderTable(data.results);
}

function resetOutput() {
  errorBox.classList.add("hidden");
  highlightBox.classList.add("hidden");
  resultsBox.classList.add("hidden");
  noMatchBox.classList.add("hidden");
  resultsTableBody.innerHTML = "";
  highlightedText.innerHTML = "";
}

function showError(msg) {
  errorBox.textContent = msg;
  errorBox.classList.remove("hidden");
}

function renderHighlights(text, results) {
  // Build a set of [start, end) ranges
  const ranges = results.map((r) => [r.start, r.end]);

  // Sort ranges by start position
  ranges.sort((a, b) => a[0] - b[0]);

  let html = "";
  let pos = 0;
  for (const [start, end] of ranges) {
    if (start > pos) {
      html += escapeHtml(text.slice(pos, start));
    }
    html += `<span class="match">${escapeHtml(text.slice(start, end))}</span>`;
    pos = end;
  }
  if (pos < text.length) {
    html += escapeHtml(text.slice(pos));
  }

  highlightedText.innerHTML = html || "(empty string)";
  highlightBox.classList.remove("hidden");
}

function renderTable(results) {
  results.forEach((r, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td><code>${escapeHtml(r.span)}</code></td>
      <td>${r.start}</td>
      <td>${r.end}</td>
      <td>${r.groups && r.groups.length ? r.groups.map((g) => `<code>${escapeHtml(g)}</code>`).join(", ") : "—"}</td>
    `;
    resultsTableBody.appendChild(tr);
  });
  resultsBox.classList.remove("hidden");
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

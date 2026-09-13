const findBtn = document.getElementById("findBtn");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const itemsEl = document.getElementById("items");

findBtn.addEventListener("click", () => {
  const rawText = itemsEl.value.trim();
  if (!rawText) {
    setStatus("Write at least one item on your list first.", false);
    return;
  }
  const items = rawText.split(/[\n,]+/).map((s) => s.trim()).filter((s) => s.length > 0);
  resultsEl.innerHTML = "";
  fetchComparison(items);
});

function setStatus(text, isLoading) {
  statusEl.textContent = text;
  statusEl.classList.toggle("loading", !!isLoading);
}

async function fetchComparison(items) {
  setStatus("Checking the ledger...", true);
  try {
    const res = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items }),
    });
    const data = await res.json();
    if (!res.ok || data.error) {
      setStatus(data.error || "Something went wrong.", false);
      return;
    }
    setStatus("", false);
    renderResults(data);
  } catch (e) {
    setStatus("Network error — check your connection and try again.", false);
  }
}

function el(html) {
  const div = document.createElement("div");
  div.innerHTML = html.trim();
  return div.firstElementChild;
}

function receiptLine(name, value, extraClass = "") {
  return `
    <div class="receipt-line ${extraClass}">
      <span class="receipt-line__name">${name}</span>
      <span class="receipt-line__leader"></span>
      <span class="receipt-line__value">${value}</span>
    </div>`;
}

function renderResults(data) {
  resultsEl.innerHTML = "";

  if (data.cheapest_single_store) {
    const s = data.cheapest_single_store;
    const itemLines = s.matched_items.map((mi) => {
      const tag = mi.matched_via === "groq" ? '<span class="match-tag">AI-matched</span>' : "";
      return receiptLine(`${mi.you_typed}${tag}`, `Rs. ${mi.price}`);
    }).join("");
    const unmatchedLine = s.unmatched_items.length
      ? `<div class="store-row__meta">Not found: ${s.unmatched_items.join(", ")}</div>` : "";

    resultsEl.appendChild(el(`
      <div class="store-row is-cheapest">
        <div class="stamp">CHEAPEST</div>
        <div class="receipt-line__name" style="font-weight:700; font-size:1rem;">${s.name}</div>
        ${s.address ? `<div class="store-row__meta">${s.address}</div>` : ""}
        ${itemLines}
        ${unmatchedLine}
        <div class="combo-total">
          <span class="combo-total__label">Total here</span>
          <span class="combo-total__value">Rs. ${s.total}</span>
        </div>
      </div>
    `));
  }

  if (data.all_stores?.length > 1) {
    resultsEl.appendChild(el(`<div class="block-title">Other stores</div>`));
    data.all_stores.slice(1).forEach((s) => {
      resultsEl.appendChild(el(`
        <div class="store-row">
          <div class="receipt-line__name" style="font-weight:600;">${s.name}</div>
          ${s.address ? `<div class="store-row__meta">${s.address}</div>` : ""}
          ${receiptLine("Total", `Rs. ${s.total}`)}
        </div>
      `));
    });
  }

  if (data.best_combo?.length) {
    resultsEl.appendChild(el(`<div class="block-title">Best combo — mix &amp; match cheapest per item</div>`));
    const comboLines = data.best_combo.map((c) => receiptLine(`${c.item} — ${c.store}`, `Rs. ${c.price}`)).join("");
    resultsEl.appendChild(el(`
      <div class="store-row">
        ${comboLines}
        <div class="combo-total">
          <span class="combo-total__label">Combo total</span>
          <span class="combo-total__value">Rs. ${data.best_combo_total}</span>
        </div>
      </div>
    `));
  }
}

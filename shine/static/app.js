const form = document.getElementById("shine-form");
const runBtn = document.getElementById("run-btn");
const summaryEl = document.getElementById("summary");
const statusEl = document.getElementById("status");
const parlaysEl = document.getElementById("parlays");
const sportsGrid = document.getElementById("sports-grid");
const template = document.getElementById("parlay-template");
const storageKey = "shine:v4:web:config";

function formatPct(value) {
  return `${(value * 100).toFixed(2)}%`;
}

function formatSignedPct(value) {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${(value * 100).toFixed(2)}%`;
}

function formatSigned(value, digits = 3) {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(digits)}`;
}

function buildSportCheckbox(option, selectedKeys) {
  const wrapper = document.createElement("label");
  wrapper.className = "sport-toggle";

  const input = document.createElement("input");
  input.type = "checkbox";
  input.value = option.key;
  input.checked = selectedKeys.includes(option.key);
  input.dataset.sportKey = option.key;

  const span = document.createElement("span");
  span.textContent = option.label;

  wrapper.append(input, span);
  return wrapper;
}

function selectedSports() {
  return Array.from(sportsGrid.querySelectorAll("input[type='checkbox']:checked")).map(
    (input) => input.value
  );
}

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function collectPayload() {
  return {
    api_key: document.getElementById("api_key").value.trim(),
    sports: selectedSports(),
    regions: document.getElementById("regions").value.trim(),
    bookmakers: document.getElementById("bookmakers").value.trim(),
    max_legs: Number(document.getElementById("max_legs").value),
    max_parlays: Number(document.getElementById("max_parlays").value),
    min_tier: document.getElementById("min_tier").value,
  };
}

function saveConfig(payload) {
  const clone = { ...payload, api_key: "" };
  localStorage.setItem(storageKey, JSON.stringify(clone));
}

function loadSavedConfig() {
  try {
    return JSON.parse(localStorage.getItem(storageKey) || "{}");
  } catch (err) {
    return {};
  }
}

function applySavedConfig(saved) {
  if (saved.regions) document.getElementById("regions").value = saved.regions;
  if (saved.bookmakers) document.getElementById("bookmakers").value = saved.bookmakers;
  if (saved.max_legs) document.getElementById("max_legs").value = String(saved.max_legs);
  if (saved.max_parlays) document.getElementById("max_parlays").value = String(saved.max_parlays);
  if (saved.min_tier) document.getElementById("min_tier").value = saved.min_tier;
}

function renderParlays(parlays) {
  parlaysEl.innerHTML = "";

  parlays.forEach((parlay, index) => {
    const fragment = template.content.cloneNode(true);
    const card = fragment.querySelector(".parlay-card");
    const tierEl = fragment.querySelector(".tier");
    const headlineEl = fragment.querySelector(".headline");
    const metricsEl = fragment.querySelector(".metrics");
    const legsEl = fragment.querySelector(".legs");

    tierEl.textContent = `Tier ${parlay.tier}`;
    tierEl.classList.add(parlay.tier);
    headlineEl.textContent = `#${index + 1} EV ${formatSignedPct(parlay.expected_value)} | Payout ${parlay.payout_multiplier.toFixed(2)}x`;

    const metrics = [
      ["True Win", formatPct(parlay.adjusted_probability)],
      ["Book Implied", formatPct(parlay.sportsbook_implied_probability)],
      ["Edge", formatSignedPct(parlay.edge_over_book)],
      ["Corr", formatSigned(parlay.correlation_score)],
      ["Corr Mult", `${parlay.correlation_multiplier.toFixed(3)}x`],
    ];

    metrics.forEach(([label, value]) => {
      const metric = document.createElement("div");
      metric.className = "metric";
      metric.innerHTML = `<span class="label">${label}</span><span class="value">${value}</span>`;
      metricsEl.appendChild(metric);
    });

    parlay.legs.forEach((leg) => {
      const legEl = document.createElement("div");
      legEl.className = "leg";
      legEl.innerHTML = `
        <div class="leg-main">
          <span>${leg.sport_key} | <strong>${leg.pick} ML</strong> in ${leg.matchup}</span>
          <span>@ ${leg.american_odds > 0 ? `+${leg.american_odds}` : leg.american_odds}</span>
        </div>
        <div class="leg-sub">
          adj p=${formatPct(leg.adjusted_probability)} | base=${formatPct(leg.base_true_probability)}
          | pressure=${leg.pressure_multiplier.toFixed(3)}x | travel=${leg.travel_multiplier.toFixed(3)}x
          | env=${leg.environment_multiplier.toFixed(3)}x | stage=${leg.context.stage}
        </div>
      `;
      legsEl.appendChild(legEl);
    });

    parlaysEl.appendChild(card);
  });
}

async function loadMetaAndInit() {
  setStatus("Loading metadata...");
  const response = await fetch("/api/meta");
  if (!response.ok) {
    throw new Error("Failed to load app metadata.");
  }
  const data = await response.json();
  const saved = loadSavedConfig();
  const selected = Array.isArray(saved.sports) && saved.sports.length ? saved.sports : data.defaults.sports;

  sportsGrid.innerHTML = "";
  data.sport_options.forEach((option) => {
    sportsGrid.appendChild(buildSportCheckbox(option, selected));
  });

  applySavedConfig(saved);
  setStatus("Ready.");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = collectPayload();

  if (!payload.sports.length) {
    setStatus("Select at least one sport.", true);
    return;
  }

  runBtn.disabled = true;
  setStatus("Running Shine engine...");
  summaryEl.textContent = "Fetching odds and building parlays...";
  parlaysEl.innerHTML = "";

  try {
    const response = await fetch("/api/parlays", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || `Request failed (${response.status})`);
    }

    saveConfig(payload);
    renderParlays(data.parlays);
    summaryEl.textContent = `${data.parlay_count} parlays from ${data.event_count} events (${data.generated_at_utc})`;
    setStatus("Completed.");
    if (!data.parlays.length) {
      setStatus("No parlays met the selected thresholds.", false);
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unexpected error.";
    setStatus(message, true);
    summaryEl.textContent = "Run failed.";
  } finally {
    runBtn.disabled = false;
  }
});

loadMetaAndInit().catch((err) => {
  const message = err instanceof Error ? err.message : "Initialization failed.";
  setStatus(message, true);
});

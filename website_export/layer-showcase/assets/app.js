const DATA_ROOT = "/assets/data";

async function loadJSON(name) {
  const response = await fetch(`${DATA_ROOT}/${name}.json`, { cache: "no-store" });
  if (!response.ok) throw new Error(`Failed to load ${name}.json`);
  return response.json();
}

function titleize(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (match) => match.toUpperCase());
}

function formatPct(value, digits = 0) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "n/a";
  return `${(number * 100).toFixed(digits)}%`;
}

function formatNumber(value, digits = 2) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "n/a";
  return number.toFixed(digits);
}

function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function setHTML(id, html) {
  const node = document.getElementById(id);
  if (node) node.innerHTML = html;
}

function groupBy(list, key) {
  return list.reduce((acc, item) => {
    const group = item[key];
    acc[group] = acc[group] || [];
    acc[group].push(item);
    return acc;
  }, {});
}

function buildBarList(items) {
  return `
    <div class="bar-list">
      ${items
        .map(
          (item) => `
            <div class="bar-row">
              <div class="bar-label"><span>${titleize(item.label)}</span><strong>${formatPct(item.value, 1)}</strong></div>
              <div class="bar-track"><div class="bar-fill" style="width:${Math.max(0, Math.min(100, item.value * 100))}%"></div></div>
            </div>
          `
        )
        .join("")}
    </div>
  `;
}

function buildTable(headers, rows) {
  return `
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr></thead>
        <tbody>
          ${rows
            .map(
              (row) => `<tr>${row.map((cell) => `<td>${cell ?? ""}</td>`).join("")}</tr>`
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

function buildMiniCards(items) {
  return `
    <div class="mini-grid">
      ${items
        .map(
          (item) => `
            <article class="mini-stat">
              <span class="section-tag">${item.label}</span>
              <h3>${item.value}</h3>
              <p>${item.body}</p>
            </article>
          `
        )
        .join("")}
    </div>
  `;
}

function formatSigned(value, digits = 1, suffix = "") {
  const number = Number(value);
  if (!Number.isFinite(number)) return `n/a${suffix}`;
  const sign = number > 0 ? "+" : "";
  return `${sign}${number.toFixed(digits)}${suffix}`;
}

function formatProbability(value) {
  const number = Number(value);
  if (number > 0 && number < 0.01) return "<1%";
  return formatPct(number, 1);
}

function formatProbabilityDelta(current, prior) {
  const delta = (Number(current) - Number(prior || 0)) * 100;
  return `${delta > 0 ? "+" : ""}${delta.toFixed(1)} pp`;
}

function termStructureChart(points, options = {}) {
  const cleanPoints = points.filter((point) => Number.isFinite(Number(point.value)));
  if (!cleanPoints.length) {
    return `<p class="muted">Treasury term-structure points are not available yet.</p>`;
  }
  const width = options.width || 760;
  const height = options.height || 280;
  const paddingX = 44;
  const paddingY = 30;
  const values = cleanPoints.map((point) => Number(point.value));
  const minY = Math.min(...values);
  const maxY = Math.max(...values);
  const scaleX = (index) =>
    paddingX + ((width - paddingX * 2) * index) / Math.max(1, cleanPoints.length - 1);
  const scaleY = (value) =>
    height - paddingY - ((value - minY) * (height - paddingY * 2)) / Math.max(1e-9, maxY - minY);

  const polyline = cleanPoints
    .map((point, index) => `${scaleX(index)},${scaleY(point.value)}`)
    .join(" ");

  const circles = cleanPoints
    .map(
      (point, index) => `
        <circle cx="${scaleX(index)}" cy="${scaleY(point.value)}" r="4.5" fill="#c66a2b"></circle>
        <text x="${scaleX(index)}" y="${height - 6}" text-anchor="middle" fill="#4d5b69" font-size="12">${point.label}</text>
      `
    )
    .join("");

  const yLabels = [minY, (minY + maxY) / 2, maxY]
    .map(
      (value) =>
        `<text x="0" y="${scaleY(value) + 4}" fill="#4d5b69" font-size="12">${formatNumber(value)}</text>`
    )
    .join("");

  return `
    <div class="chart-shell">
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Treasury yield curve">
        <rect x="${paddingX}" y="${paddingY / 2}" width="${width - paddingX * 2}" height="${height - paddingY * 1.5}" fill="rgba(16,34,53,0.03)" rx="18"></rect>
        <polyline fill="none" stroke="#102235" stroke-width="3" points="${polyline}" />
        ${circles}
        ${yLabels}
      </svg>
    </div>
  `;
}

function extractRegimeSeries(history, horizon = "mid") {
  const latest = history[history.length - 1] || {};
  const oneDay = history[history.length - 2] || latest;
  const oneWeek = history[Math.max(0, history.length - 6)] || latest;
  return Object.keys(latest)
    .filter((key) => key.startsWith(`${horizon}_`) && !key.includes("dominant"))
    .map((key) => {
      const regimeId = key.replace(`${horizon}_`, "");
      return {
        regimeId,
        current: Number(latest[key] || 0),
        d1: Number(oneDay[key] || 0),
        w1: Number(oneWeek[key] || 0),
      };
    })
    .sort((a, b) => b.current - a.current);
}

function evidenceTagsForRegime(channelUpdates, regimeId, horizon = "mid") {
  return (channelUpdates || [])
    .filter((item) => item.horizon === horizon)
    .map((item) => ({
      channel: item.channel_name,
      score: Number(item.regime_likelihoods?.[regimeId] || 0),
      confidence: Number(item.confidence || 0),
    }))
    .sort((a, b) => b.score - a.score)
    .filter((item) => item.score > 0)
    .slice(0, 2);
}

function distributionLabel(probability) {
  if (probability >= 0.65) return "High concentration";
  if (probability >= 0.45) return "Moderate concentration";
  return "Contested regime";
}

function buildRegimeMap(history, channelUpdates) {
  const series = extractRegimeSeries(history, "mid");
  if (!series.length) return `<p class="muted">Regime history is not available yet.</p>`;

  const dominant = series[0];
  const alternatives = series.slice(1, 5);
  const dominantTags = evidenceTagsForRegime(channelUpdates, dominant.regimeId);
  const remainingMass = Math.max(0, 1 - dominant.current);
  const topThreeMass = series.slice(0, 3).reduce((sum, item) => sum + Number(item.current || 0), 0);
  const strip = `
    <div class="probability-strip">
      ${series
        .slice(0, 6)
        .map(
          (node, index) => `
            <span
              class="probability-segment probability-segment-${index + 1}"
              style="width:${Math.max(4, node.current * 100)}%"
              title="${titleize(node.regimeId)} ${formatProbability(node.current)}"
            ></span>
          `
        )
        .join("")}
    </div>
  `;
  const renderNode = (node, emphasis = false) => {
    const tags = evidenceTagsForRegime(channelUpdates, node.regimeId)
      .map((item) => `<span class="node-tag">${titleize(item.channel)}</span>`)
      .join("");
    return `
      <article class="regime-node ${emphasis ? "regime-node-focus" : ""}">
        <span class="section-tag">${emphasis ? "Current node" : "Alternative path"}</span>
        <h3>${titleize(node.regimeId)}</h3>
        <div class="node-prob">${formatProbability(node.current)}</div>
        <div class="node-deltas">
          <span>Δ1D ${formatProbabilityDelta(node.current, node.d1)}</span>
          <span>Δ1W ${formatProbabilityDelta(node.current, node.w1)}</span>
        </div>
        <div class="node-tags">${tags || `<span class="muted">No positive evidence tags</span>`}</div>
      </article>
    `;
  };

  return `
    <div class="regime-map-layout">
      <div class="regime-map-side">
        ${alternatives.slice(0, 2).map((node) => renderNode(node)).join("")}
      </div>
      <div class="regime-map-focus">
        ${renderNode(dominant, true)}
        <div class="regime-focus-note">
          ${strip}
          <p><strong>Evidence:</strong> ${dominantTags.map((item) => titleize(item.channel)).join(", ") || "No positive evidence tags"}.</p>
          <p><strong>Uncertainty:</strong> ${distributionLabel(dominant.current)}. Remaining scenario mass is ${formatProbability(remainingMass)}, and the top three regimes account for ${formatProbability(topThreeMass)}.</p>
          <p><strong>Interpretation:</strong> ${titleize(dominant.regimeId)} remains the highest-probability regime path, but the adjacent nodes still retain enough mass to matter for the next repricing.</p>
        </div>
      </div>
      <div class="regime-map-side">
        ${alternatives.slice(2, 4).map((node) => renderNode(node)).join("")}
      </div>
    </div>
  `;
}

function buildEvidenceBars(channelUpdates, dominantRegime) {
  const items = (channelUpdates || [])
    .filter((item) => item.horizon === "mid")
    .map((item) => ({
      channel: item.channel_name,
      score: Number(item.regime_likelihoods?.[dominantRegime] || 0),
      confidence: Number(item.confidence || 0),
      note: item.notes,
    }))
    .sort((a, b) => b.score - a.score);

  if (!items.length) return `<p class="muted">No evidence decomposition available.</p>`;

  const maxScore = Math.max(...items.map((item) => Math.abs(item.score)), 1e-9);
  return `
    <div class="bar-list">
      ${items
        .map(
          (item) => `
            <div class="bar-row">
              <div class="bar-label">
                <span>${titleize(item.channel)}</span>
                <strong>${formatNumber(item.score, 2)}</strong>
              </div>
              <div class="bar-track">
                <div class="bar-fill" style="width:${(Math.abs(item.score) / maxScore) * 100}%"></div>
              </div>
              <p class="muted">Confidence ${formatNumber(item.confidence, 2)}. ${item.note}</p>
            </div>
          `
        )
        .join("")}
    </div>
  `;
}

function buildPlayerHorizonGrid(playerRows) {
  if (!playerRows.length) return `<p class="muted">Player probabilities are not available yet.</p>`;
  const byHorizon = groupBy(playerRows, "horizon");
  return `
    <div class="horizon-columns">
      ${["short", "mid", "long"]
        .map((horizon) => {
          const rows = byHorizon[horizon] || [];
          const byPlayer = groupBy(rows, "player_id");
          return `
            <article class="horizon-card">
              <span class="section-tag">${titleize(horizon)} horizon</span>
              <h3>${titleize(horizon)} player paths</h3>
              <ul class="horizon-list">
                ${Object.entries(byPlayer)
                  .map(([playerId, playerActions]) => {
                    const top = playerActions
                      .sort((a, b) => Number(b.probability) - Number(a.probability))
                      .slice(0, 2)
                      .map((item) => `${titleize(item.action)} (${formatPct(item.probability, 0)})`)
                      .join(", ");
                    return `<li><strong>${titleize(playerId)}:</strong> ${top}</li>`;
                  })
                  .join("")}
              </ul>
            </article>
          `;
        })
        .join("")}
    </div>
  `;
}

function buildReviewOverview(archive) {
  const missSummary = archive.miss_summary || [];
  if (!missSummary.length) return `<p class="muted">Review statistics will populate as the archive deepens.</p>`;

  const byHorizon = groupBy(missSummary, "target_horizon");
  const cards = ["short", "mid", "long"].map((horizon) => {
    const rows = (byHorizon[horizon] || []).sort((a, b) => Number(b.observations) - Number(a.observations));
    const top = rows[0];
    if (!top) {
      return {
        label: `${horizon} horizon`,
        value: "No data",
        body: "Review memory is still building.",
      };
    }
    return {
      label: `${horizon} horizon`,
      value: titleize(top.miss_type),
      body: `${top.observations} observations. Avg directional accuracy ${formatPct(top.avg_directional_accuracy, 0)}.`,
    };
  });
  return buildMiniCards(cards);
}

function buildMetricBoard(items, className = "metric-board") {
  return `
    <div class="${className}">
      ${items
        .map(
          (item) => `
            <article class="metric-cell">
              <span class="metric-label">${item.label}</span>
              <div class="metric-value">${item.value}</div>
              <div class="metric-change">${item.change || ""}</div>
              ${item.note ? `<p class="metric-note">${item.note}</p>` : ""}
            </article>
          `
        )
        .join("")}
    </div>
  `;
}

function lineChart(series, options = {}) {
  const width = options.width || 720;
  const height = options.height || 280;
  const padding = 36;
  const values = series.flatMap((item) => item.values.map((point) => point.value));
  const minY = Math.min(...values);
  const maxY = Math.max(...values);
  const xCount = series[0]?.values.length || 0;
  const scaleX = (index) => padding + ((width - padding * 2) * index) / Math.max(1, xCount - 1);
  const scaleY = (value) =>
    height - padding - ((value - minY) * (height - padding * 2)) / Math.max(1e-9, maxY - minY);

  const lines = series
    .map((item) => {
      const points = item.values.map((point, index) => `${scaleX(index)},${scaleY(point.value)}`).join(" ");
      return `<polyline fill="none" stroke="${item.color}" stroke-width="3" points="${points}" />`;
    })
    .join("");

  const xLabels = [0, Math.floor((xCount - 1) / 2), xCount - 1]
    .filter((value, index, array) => value >= 0 && array.indexOf(value) === index)
    .map((index) => {
      const point = series[0].values[index];
      return `<text x="${scaleX(index)}" y="${height - 8}" text-anchor="middle" fill="#4d5b69" font-size="12">${formatDate(point.date)}</text>`;
    })
    .join("");

  const yLabels = [minY, (minY + maxY) / 2, maxY]
    .map(
      (value) =>
        `<text x="0" y="${scaleY(value) + 4}" fill="#4d5b69" font-size="12">${formatNumber(value)}</text>`
    )
    .join("");

  const legend = `
    <div class="chart-legend">
      ${series
        .map(
          (item) =>
            `<span class="legend-pill"><span class="legend-dot" style="background:${item.color}"></span>${item.label}</span>`
        )
        .join("")}
    </div>
  `;

  return `
    <div class="chart-shell">
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Line chart">
        <rect x="${padding}" y="${padding / 2}" width="${width - padding * 2}" height="${height - padding * 1.5}" fill="rgba(16,34,53,0.03)" rx="18"></rect>
        ${lines}
        ${xLabels}
        ${yLabels}
      </svg>
      ${legend}
    </div>
  `;
}

async function renderHome() {
  const latest = await loadJSON("latest");
  const history = await loadJSON("history");
  const archive = await loadJSON("archive");
  const summary = latest.summary || {};
  const current = summary.current_regime || {
    short: { regime_id: "unknown", probability: 0 },
    mid: { regime_id: "unknown", probability: 0 },
    long: { regime_id: "unknown", probability: 0 },
  };
  const roadmapSummary = latest.roadmap_summary || {};
  const curve = summary.curve_snapshot || {};
  const daily = summary.daily_changes || {};
  const shock = summary.shock_event || {};
  const strategy = summary.strategy || {};
  const channelUpdates = summary.channel_updates || [];
  const sourceScorecard = latest.source_scorecard || [];
  const regimeSeries = extractRegimeSeries(history, "mid");
  const alternative = regimeSeries[1] || { regimeId: "no_alternative_path", current: 0, d1: 0, w1: 0 };
  const dominantEvidence = evidenceTagsForRegime(channelUpdates, current.mid.regime_id || "unknown")
    .map((item) => titleize(item.channel))
    .join(", ");

  setHTML(
    "hero-summary",
    `
      <div class="command-meta">
        <span class="section-tag">As of ${formatDate(summary.date)}</span>
        <span class="badge">War anchor ${summary.war_anchor_date || "2025-06-21"}</span>
        <span class="badge">System ${roadmapSummary.system_version || "v1"}</span>
      </div>
      <div class="command-topline">
        <div>
          <div class="command-title">${titleize(current.mid.regime_id)}</div>
          <p class="body-copy">The market is still centered on <strong>${titleize(current.mid.regime_id)}</strong>, with <strong>${titleize(shock.dominant_category)}</strong> acting as the dominant shock overlay.</p>
        </div>
        <div class="probability-tile">
          <span class="section-tag">Mid-horizon probability</span>
          <div class="probability-number">${formatProbability(current.mid.probability)}</div>
          <div class="metric-change">Dominant regime node</div>
        </div>
      </div>
      <div class="command-kpis">
        <article class="command-kpi">
          <span class="metric-label">Top alternative</span>
          <div class="metric-value">${titleize(alternative.regimeId)}</div>
          <div class="metric-change">${formatProbability(alternative.current)} | Δ1D ${formatProbabilityDelta(alternative.current, alternative.d1)}</div>
        </article>
        <article class="command-kpi">
          <span class="metric-label">Dominant shock</span>
          <div class="metric-value">${titleize(shock.dominant_category)}</div>
          <div class="metric-change">Persistence ${formatNumber(shock.persistence_score, 2)} | Confidence ${formatNumber(shock.confidence_score, 2)}</div>
        </article>
        <article class="command-kpi">
          <span class="metric-label">Treasury bias</span>
          <div class="metric-value">${titleize(strategy.directional_view)}</div>
          <div class="metric-change">${titleize(strategy.curve_view)} | Risk ${titleize(strategy.main_risk)}</div>
        </article>
      </div>
      <div class="takeaway-strip">
        <strong>Before the open:</strong> ${summary.curve_decomposition?.interpretation || "Treasury decomposition note is not available."}
      </div>
    `
  );

  setHTML(
    "hero-signals",
    buildMetricBoard(
      [
        {
          label: "2Y",
          value: formatNumber(curve.yield_2y, 2),
          change: formatSigned(daily.yield_2y_bp, 1, " bp"),
          note: "Front-end policy pricing",
        },
        {
          label: "10Y",
          value: formatNumber(curve.yield_10y, 2),
          change: formatSigned(daily.yield_10y_bp, 1, " bp"),
          note: "Benchmark duration level",
        },
        {
          label: "2s10s",
          value: `${formatNumber(Number(curve.curve_2s10s) * 100, 1)} bp`,
          change: formatSigned(daily.curve_2s10s_bp, 1, " bp"),
          note: "Growth-policy slope",
        },
        {
          label: "10Y breakeven",
          value: formatNumber(curve.breakeven_10y, 2),
          change: formatSigned(daily.breakeven_10y_bp, 1, " bp"),
          note: "Inflation compensation",
        },
        {
          label: "10Y real",
          value: formatNumber(curve.real_10y, 2),
          change: formatSigned(daily.real_10y_bp, 1, " bp"),
          note: "Real-rate anchor",
        },
        {
          label: "SOFR-FF",
          value: `${formatNumber(Number(curve.sofr_minus_ff) * 100, 1)} bp`,
          change: formatSigned(daily.sofr_minus_ff_bp, 1, " bp"),
          note: "Funding wedge proxy",
        },
      ],
      "signal-board"
    )
  );

  setHTML(
    "curve-term-chart",
    termStructureChart([
      { label: "3M", value: curve.yield_3m },
      { label: "6M", value: curve.yield_6m },
      { label: "1Y", value: curve.yield_1y },
      { label: "2Y", value: curve.yield_2y },
      { label: "3Y", value: curve.yield_3y },
      { label: "5Y", value: curve.yield_5y },
      { label: "7Y", value: curve.yield_7y },
      { label: "10Y", value: curve.yield_10y },
      { label: "20Y", value: curve.yield_20y },
      { label: "30Y", value: curve.yield_30y },
    ]) +
      `
        <div class="curve-footnotes">
          <span class="badge">5s30s ${formatNumber(Number(curve.curve_5s30s) * 100, 1)} bp</span>
          <span class="badge">2s5s10s fly ${formatNumber(curve.fly_2s5s10s, 1)} bp</span>
          <span class="badge">NS curvature ${formatNumber(curve.ns_curvature, 2)}</span>
          <span class="badge">10Y term premium ${formatNumber(curve.term_premium_proxy_10y, 2)}</span>
        </div>
      `
  );

  setHTML(
    "snapshot-metrics",
    buildMetricBoard([
      { label: "3M", value: formatNumber(curve.yield_3m, 2), change: formatSigned(daily.yield_3m_bp, 1, " bp") },
      { label: "5Y", value: formatNumber(curve.yield_5y, 2), change: formatSigned(daily.yield_5y_bp, 1, " bp") },
      { label: "30Y", value: formatNumber(curve.yield_30y, 2), change: formatSigned(daily.yield_30y_bp, 1, " bp") },
      { label: "5s30s", value: `${formatNumber(Number(curve.curve_5s30s) * 100, 1)} bp`, change: formatSigned(daily.curve_5s30s_bp, 1, " bp") },
      { label: "5Y breakeven", value: formatNumber(curve.breakeven_5y, 2), change: formatSigned(daily.breakeven_5y_bp, 1, " bp") },
      { label: "10Y breakeven", value: formatNumber(curve.breakeven_10y, 2), change: formatSigned(daily.breakeven_10y_bp, 1, " bp") },
      { label: "5Y real", value: formatNumber(curve.real_5y, 2), change: "" },
      { label: "10Y real", value: formatNumber(curve.real_10y, 2), change: formatSigned(daily.real_10y_bp, 1, " bp") },
      { label: "SOFR", value: formatNumber(curve.sofr, 2), change: formatSigned(daily.sofr_bp, 1, " bp") },
      { label: "OBFR-SOFR", value: `${formatNumber(Number(curve.repo_minus_sofr) * 100, 1)} bp`, change: formatSigned(daily.repo_minus_sofr_bp, 1, " bp") },
      { label: "10Y expected short", value: formatNumber(curve.expected_short_rate_proxy_10y, 2), change: "" },
      { label: "10Y term premium", value: formatNumber(curve.term_premium_proxy_10y, 2), change: formatSigned(daily.term_premium_proxy_10y_bp, 1, " bp") },
    ])
  );

  setHTML("regime-map", buildRegimeMap(history, channelUpdates));
  setHTML("evidence-bars", buildEvidenceBars(channelUpdates, current.mid.regime_id));

  setHTML(
    "executive-report",
    `
      <p><strong>Dominant regime:</strong> ${titleize(current.mid.regime_id)} at ${formatProbability(current.mid.probability)}.</p>
      <p><strong>Dominant shock:</strong> ${titleize(shock.dominant_category)} with persistence ${formatNumber(shock.persistence_score, 2)} and confidence ${formatNumber(shock.confidence_score, 2)}.</p>
      <p><strong>Evidence mix:</strong> ${dominantEvidence || "Positive channel evidence is still sparse."}</p>
      <p><strong>Curve signal:</strong> Nelson-Siegel curvature is ${formatNumber(curve.ns_curvature, 2)}, 10Y term premium is ${formatNumber(curve.term_premium_proxy_10y, 2)}, and policy uncertainty is ${formatNumber(summary.curve_decomposition?.policy_uncertainty_score, 2)}.</p>
      <p><strong>Desk implication:</strong> ${titleize(strategy.directional_view)} with ${titleize(strategy.curve_view)} and a main risk of ${titleize(strategy.main_risk)}.</p>
      <p><strong>Falsifier:</strong> ${strategy.falsifier || "No falsifier recorded."}</p>
    `
  );

  setHTML("player-horizon-grid", buildPlayerHorizonGrid(latest.player_probabilities || []));
  setHTML("review-overview", buildReviewOverview(archive));

  setHTML(
    "source-table",
    sourceScorecard.length
      ? buildTable(
          ["Source", "Tracked", "D+1", "W+1", "M+1"],
          sourceScorecard.map((item) => [
            item.source_name,
            item.claims_tracked,
            formatNumber(item.d1_score, 2),
            formatNumber(item.w1_score, 2),
            formatNumber(item.m1_score, 2),
          ])
        )
      : `<p class="muted">Source scorecards will populate as the forecast-review memory builds.</p>`
  );
}

async function renderFramework() {
  const framework = await loadJSON("framework");
  setHTML(
    "regime-cards",
    framework.regimes
      .map(
        (regime) => `
          <article class="regime-card">
            <span class="badge">${titleize(regime.regime_family)}</span>
            <h3>${titleize(regime.regime_name)}</h3>
            <p class="muted">${regime.economic_definition}</p>
            <p class="muted"><strong>Treasury signature:</strong> ${regime.treasury_signature.join("; ")}</p>
          </article>
        `
      )
      .join("")
  );

  const headers = ["From / To", ...framework.regimes.map((regime) => titleize(regime.regime_id))];
  const rows = Object.entries(framework.transition_matrix).map(([from, row]) => [
    titleize(from),
    ...framework.regimes.map((regime) => formatPct(row[regime.regime_id] || 0, 0)),
  ]);
  setHTML("transition-matrix", buildTable(headers, rows));
}

async function renderRoadmap() {
  const roadmap = await loadJSON("roadmap");
  const hierarchy = roadmap.hierarchy || [];
  const upgrades = hierarchy.flatMap((layer) =>
    (layer.next_upgrades || []).map((upgrade) => ({
      ...upgrade,
      layer_title: layer.title,
      layer_order: layer.order,
    }))
  );

  const priorityRank = { high: 0, medium: 1, low: 2 };
  upgrades.sort((a, b) => {
    const byPriority = (priorityRank[a.priority] ?? 9) - (priorityRank[b.priority] ?? 9);
    if (byPriority !== 0) return byPriority;
    return (a.layer_order || 99) - (b.layer_order || 99);
  });

  setHTML(
    "roadmap-summary",
    [
      {
        label: "Version",
        value: roadmap.system_version || "v1",
        body: roadmap.version_label || "Tracked research system version.",
      },
      {
        label: "Layers",
        value: String(hierarchy.length),
        body: "Architectural layers in the current research stack.",
      },
      {
        label: "High priority",
        value: String(upgrades.filter((item) => item.priority === "high").length),
        body: "Upgrades that should shape the next research pass.",
      },
      {
        label: "In progress",
        value: String(upgrades.filter((item) => item.status === "in_progress").length),
        body: "Tracked improvements already underway.",
      },
    ]
      .map(
        (card) => `
          <article class="summary-card">
            <span class="section-tag">${card.label}</span>
            <h3>${card.value}</h3>
            <p>${card.body}</p>
          </article>
        `
      )
      .join("")
  );

  setHTML(
    "roadmap-layers",
    hierarchy
      .sort((a, b) => (a.order || 99) - (b.order || 99))
      .map(
        (layer) => `
          <article class="regime-card">
            <span class="badge">Layer ${layer.order}</span>
            <h3>${layer.title}</h3>
            <p class="muted">${layer.role}</p>
            <p class="muted"><strong>Status:</strong> ${titleize(layer.current_status)}</p>
            <p class="muted"><strong>V1 scope:</strong></p>
            <ul class="bullet-list">
              ${(layer.v1_scope || []).map((item) => `<li>${item}</li>`).join("")}
            </ul>
            <p class="muted"><strong>Known problems:</strong></p>
            <ul class="bullet-list">
              ${(layer.known_problems || []).map((item) => `<li>${item}</li>`).join("")}
            </ul>
          </article>
        `
      )
      .join("")
  );

  setHTML(
    "roadmap-upgrades",
    buildTable(
      ["Layer", "Upgrade", "Priority", "Status", "Success metric"],
      upgrades.map((item) => [
        item.layer_title,
        `<strong>${item.upgrade_id}</strong><br />${item.title}<br /><span class="muted">${item.planned_change}</span>`,
        titleize(item.priority),
        titleize(item.status),
        item.success_metric,
      ])
    )
  );

  const cadence = roadmap.review_cadence || {};
  setHTML(
    "roadmap-rules",
    `
      <p><strong>Purpose:</strong> ${roadmap.purpose || ""}</p>
      <p><strong>Maintenance rule:</strong> ${roadmap.maintenance_rule || ""}</p>
      <p><strong>Daily:</strong> ${cadence.daily || ""}</p>
      <p><strong>Weekly:</strong> ${cadence.weekly || ""}</p>
      <p><strong>Monthly:</strong> ${cadence.monthly || ""}</p>
    `
  );
}

async function renderArchive() {
  const archive = await loadJSON("archive");
  const notes = archive.notes || [];
  const review = archive.regime_review || [];
  const missSummary = archive.miss_summary || [];

  setHTML(
    "archive-table",
    buildTable(
      ["Date", "Short", "Mid", "Shock", "2Y", "10Y"],
      notes.slice(0, 40).map((item) => [
        formatDate(item.date),
        titleize(item.short_dominant_regime),
        titleize(item.mid_dominant_regime),
        titleize(item.dominant_category),
        formatNumber(item.yield_2y, 2),
        formatNumber(item.yield_10y, 2),
      ])
    )
  );

  const groupedReview = groupBy(review, "target_horizon");
  setHTML(
    "review-table",
    Object.keys(groupedReview).length
      ? buildTable(
          ["Horizon", "Observations", "Avg directional accuracy"],
          Object.entries(groupedReview).map(([horizon, rows]) => {
            const avg = rows.reduce((sum, row) => sum + Number(row.directional_accuracy || 0), 0) / rows.length;
            return [titleize(horizon), rows.length, formatPct(avg, 0)];
          })
        )
      : `<p class="muted">Review statistics will build as the archive deepens.</p>`
  );

  setHTML(
    "miss-table",
    missSummary.length
      ? buildTable(
          ["Horizon", "Miss type", "Observations", "Avg directional accuracy"],
          missSummary.map((item) => [
            titleize(item.target_horizon),
            titleize(item.miss_type),
            item.observations,
            formatPct(item.avg_directional_accuracy, 0),
          ])
        )
      : `<p class="muted">Miss taxonomy statistics will populate as the review archive builds.</p>`
  );
}

function buildPrimerMap(primer) {
  const studyList = (primer.studyFramework || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");

  const layerCards = (primer.layers || [])
    .map(
      (layer) => `
        <article class="primer-mini-card">
          <span class="badge">Layer ${escapeHtml(layer.number)}</span>
          <h3>${escapeHtml(layer.title)}</h3>
          <p>${escapeHtml(layer.strapline)}</p>
          <div class="primer-mini-meta">
            <span><strong>Desk:</strong> ${escapeHtml(layer.deskSpeed)}</span>
            <span><strong>Public:</strong> ${escapeHtml(layer.publicRhythm)}</span>
          </div>
        </article>
      `
    )
    .join("");

  return `
    <div class="primer-intro-note">
      <p>${escapeHtml(primer.introduction || "")}</p>
    </div>
    <article class="primer-study-card">
      <span class="section-tag">Reading order</span>
      <ul class="bullet-list">${studyList}</ul>
    </article>
    <div class="primer-mini-grid">${layerCards}</div>
  `;
}

function buildPrimerToc(layers) {
  return `
    <ul class="primer-toc-list">
      ${layers
        .map(
          (layer) => `
            <li>
              <a href="#primer-${escapeHtml(layer.id)}">
                <span class="toc-number">${escapeHtml(layer.number)}</span>
                <span>
                  <strong>${escapeHtml(layer.title)}</strong>
                  <small>${escapeHtml(layer.strapline)}</small>
                </span>
              </a>
            </li>
          `
        )
        .join("")}
    </ul>
  `;
}

function buildPrimerSection(layer) {
  const implications = (layer.implications || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");

  const terminology = (layer.terminology || [])
    .map(
      (item) => `
        <article class="term-box">
          <span class="term-label">${escapeHtml(item.term)}</span>
          <p>${escapeHtml(item.meaning)}</p>
          <div class="term-desk-read"><strong>Desk read:</strong> ${escapeHtml(item.deskRead)}</div>
        </article>
      `
    )
    .join("");

  const deskVariables = (layer.deskVariables || [])
    .map(
      (item) => `
        <article class="desk-variable-card">
          <h4>${escapeHtml(item.name)}</h4>
          <p>${escapeHtml(item.description)}</p>
          <div class="desk-variable-why"><strong>Why it matters:</strong> ${escapeHtml(item.whyItMatters)}</div>
        </article>
      `
    )
    .join("");

  const publicRows = (layer.publicInstruments || [])
    .map(
      (item) => `
        <tr>
          <td>
            <strong><a href="${escapeHtml(item.link)}" target="_blank" rel="noreferrer">${escapeHtml(item.source)}</a></strong>
            <div class="cell-note">${escapeHtml(item.description)}</div>
          </td>
          <td>${escapeHtml(item.frequency)}</td>
          <td>${escapeHtml(item.publishTiming)}</td>
          <td>${escapeHtml(item.use)}</td>
          <td>${escapeHtml(item.gap)}</td>
        </tr>
      `
    )
    .join("");

  return `
    <section class="panel primer-section" id="primer-${escapeHtml(layer.id)}">
      <div class="primer-section-head">
        <div>
          <span class="section-tag">Hidden layer ${escapeHtml(layer.number)}</span>
          <h2>${escapeHtml(layer.title)}</h2>
          <p class="body-copy">${escapeHtml(layer.strapline)}</p>
        </div>
        <div class="primer-speed">
          <span class="badge">Desk speed: ${escapeHtml(layer.deskSpeed)}</span>
          <span class="badge">Public rhythm: ${escapeHtml(layer.publicRhythm)}</span>
        </div>
      </div>

      <div class="primer-grid-two">
        <article class="primer-copy-block">
          <h3>Definition</h3>
          <p>${escapeHtml(layer.definition)}</p>
        </article>
        <article class="primer-copy-block">
          <h3>Why the desk cares</h3>
          <p>${escapeHtml(layer.whyDeskCares)}</p>
        </article>
      </div>

      <article class="primer-copy-block">
        <h3>What it usually implies</h3>
        <ul class="bullet-list">${implications}</ul>
      </article>

      <article class="primer-block">
        <div class="primer-block-head">
          <span class="section-tag">Terminology box</span>
          <h3>Words you need to hear the way a desk hears them</h3>
        </div>
        <div class="term-grid">${terminology}</div>
      </article>

      <article class="primer-block">
        <div class="primer-block-head">
          <span class="section-tag">Desk variables</span>
          <h3>What professionals actually watch</h3>
        </div>
        <div class="desk-variable-grid">${deskVariables}</div>
      </article>

      <article class="primer-block">
        <div class="primer-block-head">
          <span class="section-tag">Public instruments</span>
          <h3>What you can collect, how often, and where the lag begins</h3>
        </div>
        <div class="table-wrap">
          <table class="data-table primer-table">
            <thead>
              <tr>
                <th>Source</th>
                <th>Frequency</th>
                <th>Publication timing</th>
                <th>What it captures</th>
                <th>Gap versus desk data</th>
              </tr>
            </thead>
            <tbody>${publicRows}</tbody>
          </table>
        </div>
      </article>

      <article class="primer-callout">
        <span class="section-tag">Research use</span>
        <p>${escapeHtml(layer.researchUse)}</p>
      </article>
    </section>
  `;
}

async function renderPrimer() {
  const primer = window.HIDDEN_LAYER_PRIMER;
  if (!primer || !Array.isArray(primer.layers)) {
    throw new Error("Primer data is not available.");
  }

  setHTML("primer-map", buildPrimerMap(primer));
  setHTML("primer-toc", buildPrimerToc(primer.layers));
  setHTML(
    "primer-sections",
    primer.layers.map((layer) => buildPrimerSection(layer)).join("")
  );
}

async function boot() {
  const page = document.body.dataset.page;
  if (page === "home") await renderHome();
  if (page === "framework") await renderFramework();
  if (page === "primer") await renderPrimer();
  if (page === "roadmap") await renderRoadmap();
  if (page === "archive") await renderArchive();
}

boot().catch((error) => {
  console.error(error);
  document.body.dataset.error = error?.message || "unknown";
  setHTML(
    "hero-summary",
    `<div class="takeaway-strip"><strong>Load error:</strong> ${error?.message || "Unknown render failure."}</div>`
  );
});

/**
 * CodeMix Lab — Gujarati–English NLP Research Interface
 * Standalone Frontend JavaScript Application
 */

document.addEventListener("DOMContentLoaded", () => {
  // Input & action elements
  const inputText = document.getElementById("input-text");
  const analyzeBtn = document.getElementById("analyze-btn");
  const clearBtn = document.getElementById("clear-btn");
  const charCount = document.getElementById("char-count");
  const alertBanner = document.getElementById("alert-banner");

  // State containers
  const emptyStateCard = document.getElementById("empty-state-card");
  const loadingStateCard = document.getElementById("loading-state-card");
  const errorStateCard = document.getElementById("error-state-card");
  const errorCardDesc = document.getElementById("error-card-desc");
  const resultsSection = document.getElementById("results-section");

  // Overview metrics elements
  const statTotalTokens = document.getElementById("stat-total-tokens");
  const statLangTypes = document.getElementById("stat-lang-types");
  const statNormTokens = document.getElementById("stat-norm-tokens");
  const statUnkTokens = document.getElementById("stat-unk-tokens");
  const statDomLang = document.getElementById("stat-dom-lang");
  const statSentiment = document.getElementById("stat-sentiment");
  const statTopic = document.getElementById("stat-topic");

  // Sentiment classification elements
  const sentimentBadge = document.getElementById("sentiment-badge");
  const sentimentConfLabel = document.getElementById("sentiment-confidence-label");
  const sentimentProbBars = document.getElementById("sentiment-prob-bars");

  // Topic classification elements
  const topicBadge = document.getElementById("topic-badge");
  const topicConfLabel = document.getElementById("topic-confidence-label");
  const topicProbBars = document.getElementById("topic-prob-bars");

  // Language composition & switching elements
  const langCompBars = document.getElementById("lang-comp-bars");
  const tokenSequenceBox = document.getElementById("token-sequence-box");
  const transitionsContainer = document.getElementById("transitions-container");
  const transitionsTags = document.getElementById("transitions-tags");

  // Normalization elements
  const originalTextBox = document.getElementById("original-text-box");
  const normalizedTextBox = document.getElementById("normalized-text-box");
  const normSummaryTag = document.getElementById("norm-summary-tag");
  const normTransformationsGrid = document.getElementById("norm-transformations-grid");

  // Token analysis table elements
  const tokensTableTbody = document.getElementById("tokens-table-tbody");
  const cntTotal = document.getElementById("cnt-total");
  const cntGuj = document.getElementById("cnt-guj");
  const cntEng = document.getElementById("cnt-eng");
  const cntRom = document.getElementById("cnt-rom");
  const cntUnk = document.getElementById("cnt-unk");
  const unknownTokensPanel = document.getElementById("unknown-tokens-panel");
  const unknownCountPill = document.getElementById("unknown-count-pill");
  const unknownTokensTags = document.getElementById("unknown-tokens-tags");

  // Research insights elements
  const researchInsightContent = document.getElementById("research-insight-content");
  const confidenceAssessmentBox = document.getElementById("confidence-assessment-box");
  const confidenceAssessmentText = document.getElementById("confidence-assessment-text");

  // Text statistics elements
  const scChars = document.getElementById("sc-chars");
  const scTokens = document.getElementById("sc-tokens");
  const scUnique = document.getElementById("sc-unique");
  const scNorm = document.getElementById("sc-norm");
  const scUnk = document.getElementById("sc-unk");
  const scAvgLen = document.getElementById("sc-avg-len");

  let isAnalyzing = false;

  // 1. Live Character Counter (0 / 500)
  inputText.addEventListener("input", () => {
    const len = inputText.value.length;
    charCount.textContent = `${len} / 500`;
    if (len > 0) hideAlert();
  });

  // 2. Keyboard UX: Ctrl + Enter / Cmd + Enter
  inputText.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      analyzeBtn.click();
    }
  });

  // 3. Preset Example Buttons
  document.querySelectorAll(".preset-pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      inputText.value = pill.getAttribute("data-sample") || "";
      inputText.dispatchEvent(new Event("input"));
      inputText.focus();
    });
  });

  // 4. Clear Button
  clearBtn.addEventListener("click", () => {
    inputText.value = "";
    inputText.dispatchEvent(new Event("input"));
    resultsSection.style.display = "none";
    loadingStateCard.style.display = "none";
    errorStateCard.style.display = "none";
    emptyStateCard.style.display = "block";
    hideAlert();
    inputText.focus();
  });

  // 5. Analyze Button
  analyzeBtn.addEventListener("click", async () => {
    if (isAnalyzing) return;

    const text = inputText.value.trim();

    // Client-side empty validation: do NOT send request
    if (!text) {
      showAlert("Please enter some text to analyze.");
      resultsSection.style.display = "none";
      loadingStateCard.style.display = "none";
      errorStateCard.style.display = "none";
      emptyStateCard.style.display = "block";
      inputText.focus();
      return;
    }

    if (text.length > 500) {
      showAlert("Text exceeds maximum allowed length of 500 characters.");
      return;
    }

    hideAlert();
    setLoading(true);

    try {
      // Relative URL for robust standalone deployment
      const response = await fetch("/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ text: text })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        const errorMsg = data && data.error
          ? data.error
          : "The NLP service could not process this request. Please try again.";
        showAnalysisError(errorMsg);
        return;
      }

      renderAllResults(data.result);
      emptyStateCard.style.display = "none";
      loadingStateCard.style.display = "none";
      errorStateCard.style.display = "none";
      resultsSection.style.display = "block";
      resultsSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } catch (err) {
      showAnalysisError("Unable to process the text. Please check that the Flask server is running at http://127.0.0.1:5000.");
    } finally {
      setLoading(false);
    }
  });

  // =========================================================================
  // Master Render Function
  // =========================================================================
  function renderAllResults(result) {
    const orig = (result.original_text || "").trim();
    const norm = (result.normalized_text || "").trim();
    const stats = result.statistics || {};
    const codeMix = result.code_mixing || {};
    const dist = result.language_distribution || {};
    const counts = result.language_counts || {};
    const sentiment = result.sentiment || {};
    const topic = result.topic || {};
    const transitions = result.language_transitions || {};
    const normComp = result.normalization_comparison || {};
    const tokens = result.tokens || [];
    const unknownTokens = result.unknown_tokens || [];

    // --- 1. Overview Metrics Tiles ---
    statTotalTokens.textContent = stats.total_tokens || tokens.length;
    statLangTypes.textContent = codeMix.language_count || 0;
    statNormTokens.textContent = normComp.tokens_changed_count || 0;
    statUnkTokens.textContent = stats.unknown_tokens || 0;
    statDomLang.textContent = codeMix.dominant_language || "None";
    statSentiment.textContent = sentiment.label || "Neutral";
    statTopic.textContent = topic.label || "General";

    // --- 2. Sentiment Classifier Panel ---
    const sentLabel = sentiment.label || "Neutral";
    const sentConf = Number(sentiment.confidence || 0).toFixed(1);
    sentimentBadge.textContent = sentLabel;
    sentimentBadge.className = `pred-pill ${sentLabel.toLowerCase()}`;
    sentimentConfLabel.textContent = `Model confidence: ${sentConf}%`;

    // Horizontal bars for Sentiment
    sentimentProbBars.innerHTML = "";
    const sentProbs = sentiment.probabilities || { "Positive": 0, "Neutral": 0, "Negative": 0 };
    ["Positive", "Neutral", "Negative"].forEach((cls) => {
      const probVal = sentProbs[cls] !== undefined ? sentProbs[cls] : 0;
      const row = document.createElement("div");
      row.className = "prob-bar-row";
      row.innerHTML = `
        <span class="prob-bar-label">${cls}</span>
        <div class="prob-bar-track">
          <div class="prob-bar-fill sentiment-${cls.toLowerCase()}" style="width: ${probVal}%;"></div>
        </div>
        <span class="prob-bar-pct">${Number(probVal).toFixed(1)}%</span>
      `;
      sentimentProbBars.appendChild(row);
    });

    // --- 3. Topic Classifier Panel ---
    const topicLabel = topic.label || "General";
    const topicConf = Number(topic.confidence || 0).toFixed(1);
    topicBadge.textContent = topicLabel;
    topicConfLabel.textContent = `Model confidence: ${topicConf}%`;

    // Horizontal bars for Topic (ranked descending)
    topicProbBars.innerHTML = "";
    const topicProbs = topic.probabilities || {};
    const sortedTopics = Object.entries(topicProbs).sort((a, b) => b[1] - a[1]);

    sortedTopics.forEach(([tClass, probVal]) => {
      const row = document.createElement("div");
      row.className = "prob-bar-row";
      row.innerHTML = `
        <span class="prob-bar-label" title="${escapeHtml(tClass)}">${escapeHtml(tClass)}</span>
        <div class="prob-bar-track">
          <div class="prob-bar-fill topic-fill" style="width: ${probVal}%;"></div>
        </div>
        <span class="prob-bar-pct">${Number(probVal).toFixed(1)}%</span>
      `;
      topicProbBars.appendChild(row);
    });

    // --- 4. Language Composition Bars ---
    langCompBars.innerHTML = "";
    const langCategories = [
      { key: "English", label: "English", class: "english" },
      { key: "Romanized Gujarati", label: "Romanized Gujarati", class: "romanized" },
      { key: "Gujarati", label: "Gujarati Script", class: "gujarati" },
      { key: "Unknown", label: "Unknown / Other", class: "unknown" }
    ];

    langCategories.forEach((cat) => {
      const pct = dist[cat.key] || 0;
      const count = counts[cat.key] || 0;
      if (count > 0 || cat.key !== "Unknown") {
        const row = document.createElement("div");
        row.className = "lang-bar-line";
        row.innerHTML = `
          <div class="lang-name-tag">
            <span class="lang-pip ${cat.class}"></span>
            <span>${cat.label}</span>
          </div>
          <div class="lang-track-full">
            <div class="lang-fill-full ${cat.class}" style="width: ${pct}%;"></div>
          </div>
          <div class="lang-num-pct">${pct}%</div>
        `;
        langCompBars.appendChild(row);
      }
    });

    // --- 5. Switching Pattern & Transitions ---
    tokenSequenceBox.innerHTML = "";
    const rawTokens = tokens.filter(t => t.language !== "Punctuation");
    if (rawTokens.length === 0) {
      tokenSequenceBox.innerHTML = `<span style="color: var(--text-tertiary); font-size: 0.84rem;">No word tokens detected.</span>`;
    } else {
      const tagMap = {
        "English": "EN",
        "Gujarati": "GU",
        "Romanized Gujarati": "RG",
        "Unknown": "UN"
      };
      rawTokens.forEach((t, i) => {
        const code = tagMap[t.language] || "UN";
        const item = document.createElement("div");
        item.className = "seq-item";
        item.innerHTML = `
          <span class="seq-word">${escapeHtml(t.token || t.word)}</span>
          <span class="seq-code ${code}">${code}</span>
        `;
        tokenSequenceBox.appendChild(item);

        if (i < rawTokens.length - 1) {
          const arrow = document.createElement("span");
          arrow.className = "seq-arrow-sym";
          arrow.textContent = "→";
          tokenSequenceBox.appendChild(arrow);
        }
      });
    }

    // Transitions List
    const transitionItems = transitions.transitions || [];
    if (transitionItems.length > 0) {
      transitionsContainer.style.display = "flex";
      transitionsTags.innerHTML = "";
      transitionItems.forEach((trItem) => {
        const chip = document.createElement("span");
        chip.className = "transition-chip";
        chip.innerHTML = `${escapeHtml(trItem.transition)}: <strong>${trItem.count}</strong>`;
        transitionsTags.appendChild(chip);
      });
    } else {
      transitionsContainer.style.display = "none";
    }

    // --- 6. Normalization Comparison ---
    originalTextBox.textContent = orig || "—";
    if (result.is_normalized_identical || (orig && norm && orig.toLowerCase() === norm.toLowerCase())) {
      normalizedTextBox.innerHTML = `<span class="side-content unchanged">No normalization required</span>`;
    } else {
      normalizedTextBox.textContent = norm || "—";
    }

    const totalNormTokens = normComp.total_word_tokens || 0;
    const changedNormTokens = normComp.tokens_changed_count || 0;
    normSummaryTag.textContent = `Tokens Changed: ${changedNormTokens} / ${totalNormTokens}`;

    // Token transformation cards
    normTransformationsGrid.innerHTML = "";
    const changesList = (normComp.changes || []).filter(c => c.changed);
    if (changesList.length === 0) {
      normTransformationsGrid.innerHTML = `<div class="no-norm-msg">No normalization changes detected.</div>`;
    } else {
      changesList.forEach((ch) => {
        const card = document.createElement("div");
        card.className = "norm-transform-card";
        card.innerHTML = `
          <span class="norm-from">${escapeHtml(ch.original)}</span>
          <span class="norm-arrow">→</span>
          <span class="norm-to">${escapeHtml(ch.normalized)}</span>
        `;
        normTransformationsGrid.appendChild(card);
      });
    }

    // --- 7. Token Table ---
    cntTotal.textContent = stats.total_tokens || tokens.length;
    cntGuj.textContent = stats.gujarati_tokens || 0;
    cntEng.textContent = stats.english_tokens || 0;
    cntRom.textContent = stats.romanized_tokens || 0;
    cntUnk.textContent = stats.unknown_tokens || 0;

    tokensTableTbody.innerHTML = "";
    tokens.forEach((t, index) => {
      const tr = document.createElement("tr");
      const langClass = (t.language || "unknown").toLowerCase().replace(/\s+/g, "-");
      tr.innerHTML = `
        <td style="color: var(--text-tertiary);">${index + 1}</td>
        <td><strong>${escapeHtml(t.token || t.word)}</strong></td>
        <td><span class="lang-badge ${langClass}">${escapeHtml(t.language)}</span></td>
        <td>${escapeHtml(t.normalized)}</td>
        <td>${escapeHtml(t.transliteration || t.normalized)}</td>
      `;
      tokensTableTbody.appendChild(tr);
    });

    // Unknown tokens panel
    if (unknownTokens.length > 0) {
      unknownTokensPanel.style.display = "block";
      unknownCountPill.textContent = `${unknownTokens.length} unmapped`;
      unknownTokensTags.innerHTML = "";
      unknownTokens.forEach((ut) => {
        const chip = document.createElement("span");
        chip.className = "unknown-chip";
        chip.textContent = ut;
        unknownTokensTags.appendChild(chip);
      });
    } else {
      unknownTokensPanel.style.display = "none";
    }

    // --- 8. Research Insight (What the model found) ---
    // Deterministic rule-based interpretation as instructed
    const recognizedList = [];
    if (stats.english_tokens > 0) recognizedList.push("English");
    if (stats.romanized_tokens > 0) recognizedList.push("Romanized Gujarati");
    if (stats.gujarati_tokens > 0) recognizedList.push("Gujarati");

    let insightText = "";
    if (codeMix.is_mixed) {
      insightText = `The input contains ${recognizedList.join(" and ")}, indicating code-mixed usage. `;
    } else if (codeMix.dominant_language !== "None") {
      insightText = `The input is predominantly in ${codeMix.dominant_language} with no significant code-mixing detected. `;
    } else {
      insightText = `The input contains minimal recognized vocabulary. `;
    }

    if (codeMix.dominant_language !== "None") {
      insightText += `${codeMix.dominant_language} is the dominant language (${dist[codeMix.dominant_language] || 0}%). `;
    }

    insightText += `The sentiment classifier predicts ${sentiment.label || "Neutral"} with ${sentConf}% confidence, while the topic classifier predicts ${topic.label || "General"} with ${topicConf}% confidence.`;

    researchInsightContent.textContent = insightText;

    const confAssessment = result.confidence_assessment || {};
    if (confAssessment.status === "low" || Math.min(Number(sentiment.confidence || 0), Number(topic.confidence || 0)) < 60) {
      confidenceAssessmentBox.className = "confidence-notice low";
      confidenceAssessmentText.textContent = "Low Confidence: One or more predictions have confidence below 60%. Consider these results as academic estimates.";
    } else {
      confidenceAssessmentBox.className = "confidence-notice solid";
      confidenceAssessmentText.textContent = "Model prediction confidence is relatively strong (≥ 60%) across evaluated TF-IDF feature weights.";
    }

    // --- 9. Text Statistics ---
    scChars.textContent = stats.characters || orig.length;
    scTokens.textContent = stats.total_tokens || tokens.length;
    scUnique.textContent = stats.unique_tokens || 0;
    scNorm.textContent = stats.normalized_tokens || 0;
    scUnk.textContent = stats.unknown_tokens || 0;
    scAvgLen.textContent = stats.avg_token_length !== undefined ? `${stats.avg_token_length}` : "0.0";
  }

  // =========================================================================
  // UI State Helpers
  // =========================================================================
  function setLoading(isLoading) {
    isAnalyzing = isLoading;
    if (isLoading) {
      analyzeBtn.disabled = true;
      analyzeBtn.innerHTML = `
        <span class="loading-spinner" style="width: 14px; height: 14px; border-width: 2px; margin: 0; display: inline-block;"></span>
        <span>Analyzing text…</span>
      `;
      emptyStateCard.style.display = "none";
      resultsSection.style.display = "none";
      errorStateCard.style.display = "none";
      loadingStateCard.style.display = "block";
    } else {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = `<span>Analyze text</span><span class="btn-arrow" aria-hidden="true">→</span>`;
      loadingStateCard.style.display = "none";
    }
  }

  function showAnalysisError(msg) {
    showAlert(msg);
    resultsSection.style.display = "none";
    emptyStateCard.style.display = "none";
    loadingStateCard.style.display = "none";
    if (errorCardDesc && msg) {
      errorCardDesc.innerHTML = `${escapeHtml(msg)}<br>Please check that the Flask server is running and try again.`;
    }
    errorStateCard.style.display = "block";
  }

  function showAlert(msg) {
    alertBanner.textContent = msg;
    alertBanner.className = "alert-banner error";
  }

  function hideAlert() {
    alertBanner.textContent = "";
    alertBanner.className = "alert-banner";
  }

  function escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  // =========================================================================
  // Load Model Metrics for Comparison Chart (Section 23)
  // =========================================================================
  async function loadMetrics() {
    try {
      const res = await fetch("/metrics");
      if (res.ok) {
        const data = await res.json();
        if (data.metrics) {
          const sentM = data.metrics.sentiment || {};
          const topM = data.metrics.topic || {};

          // Model comparison graph bars
          if (sentM.accuracy !== undefined) {
            updateCompBar("comp-acc-sent", "comp-acc-sent-val", sentM.accuracy);
            updateCompBar("comp-prec-sent", "comp-prec-sent-val", sentM.precision);
            updateCompBar("comp-rec-sent", "comp-rec-sent-val", sentM.recall);
            updateCompBar("comp-f1-sent", "comp-f1-sent-val", sentM.f1_score);
          }

          if (topM.accuracy !== undefined) {
            updateCompBar("comp-acc-top", "comp-acc-top-val", topM.accuracy);
            updateCompBar("comp-prec-top", "comp-prec-top-val", topM.precision);
            updateCompBar("comp-rec-top", "comp-rec-top-val", topM.recall);
            updateCompBar("comp-f1-top", "comp-f1-top-val", topM.f1_score);
          }

          // Detailed metrics table
          if (sentM.accuracy !== undefined) {
            setText("det-sent-acc", `${Number(sentM.accuracy).toFixed(2)}%`);
            setText("det-sent-prec", `${Number(sentM.precision).toFixed(2)}%`);
            setText("det-sent-rec", `${Number(sentM.recall).toFixed(2)}%`);
            setText("det-sent-f1", `${Number(sentM.f1_score).toFixed(2)}%`);
          }

          if (topM.accuracy !== undefined) {
            setText("det-top-acc", `${Number(topM.accuracy).toFixed(2)}%`);
            setText("det-top-prec", `${Number(topM.precision).toFixed(2)}%`);
            setText("det-top-rec", `${Number(topM.recall).toFixed(2)}%`);
            setText("det-top-f1", `${Number(topM.f1_score).toFixed(2)}%`);
          }
        }
      }
    } catch (_) {
      // Fallback to static verified metrics if offline
    }
  }

  function updateCompBar(barId, valId, val) {
    const barEl = document.getElementById(barId);
    const valEl = document.getElementById(valId);
    if (barEl) barEl.style.width = `${val}%`;
    if (valEl) valEl.textContent = `${Number(val).toFixed(2)}%`;
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  loadMetrics();
});

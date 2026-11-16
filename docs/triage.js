/* JavaScript copy of the checking scripts in scripts/. No AI here, only plain rules.
   Each function matches its Python twin, and tests/test_js_parity.py checks they agree. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.Triage = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // ---- scripts/common.py: seeded random sample -------------------------------------------
  function mulberry32(seed) {
    let a = seed | 0;
    return function () {
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function seededSample(ids, size, seed) {
    const list = ids.slice().sort();
    const rnd = mulberry32(seed);
    for (let i = list.length - 1; i > 0; i--) {
      const j = Math.floor(rnd() * (i + 1));
      const tmp = list[i];
      list[i] = list[j];
      list[j] = tmp;
    }
    return list.slice(0, size);
  }

  // ---- scripts/detect_language.py --------------------------------------------------------
  const TOKEN = /[a-zà-ÿœ]+(?:['’][a-zà-ÿœ]+)?/g;
  const ACCENT = /[à-ÿœ]/;
  const APOSTROPHE = /['’]/;

  function score(text, words) {
    const fr = new Set(words.fr_words);
    const en = new Set(words.en_words);
    const elision = new Set(words.fr_elision);
    let frScore = 0;
    let enScore = 0;
    for (const token of text.toLowerCase().match(TOKEN) || []) {
      let parts = token.split(APOSTROPHE);
      if (parts.length === 2 && elision.has(parts[0])) {
        frScore += 1;
        parts = parts.slice(1);
      }
      for (const part of parts) {
        if (fr.has(part)) frScore += 1;
        else if (en.has(part)) enScore += 1;
      }
      if (ACCENT.test(token)) frScore += 1;
    }
    return { fr: frScore, en: enScore };
  }

  function detect(text, words) {
    const s = score(text, words);
    if (s.fr === s.en) return { language: "EN", confidence: "low", fr: s.fr, en: s.en };
    return {
      language: s.fr > s.en ? "FR" : "EN",
      confidence: Math.abs(s.fr - s.en) >= 2 ? "high" : "low",
      fr: s.fr,
      en: s.en,
    };
  }

  // ---- scripts/validate_ticket.py --------------------------------------------------------
  function validate(ticket, seen) {
    if (ticket === null || typeof ticket !== "object" || Array.isArray(ticket)) return "ticket is not an object";
    for (const f of ["id", "subject", "body", "received_at"]) {
      if (typeof ticket[f] !== "string" || ticket[f].trim() === "") return "missing or empty field " + f;
    }
    if (!/^T\d{3}$/.test(ticket.id)) return "id must be T plus 3 digits";
    if (seen.has(ticket.id)) return "duplicate id";
    if (ticket.subject.length < 1 || ticket.subject.length > 120) return "subject must be 1 to 120 characters";
    if (ticket.body.length < 10 || ticket.body.length > 2000) return "body must be 10 to 2000 characters";
    if (!/^\d{4}-\d{2}-\d{2}$/.test(ticket.received_at)) return "received_at must look like YYYY-MM-DD";
    const [y, m, d] = ticket.received_at.split("-").map(Number);
    const date = new Date(Date.UTC(y, m - 1, d));
    if (date.getUTCFullYear() !== y || date.getUTCMonth() !== m - 1 || date.getUTCDate() !== d) {
      return "received_at is not a real date";
    }
    return null;
  }

  // ---- scripts/check_classification.py ---------------------------------------------------
  function classificationProblems(item, cfg) {
    const found = [];
    if (!cfg.categories.includes(item.category)) found.push("category '" + item.category + "' is not allowed");
    if (!cfg.priorities.includes(item.priority)) found.push("priority '" + item.priority + "' is not allowed");
    if (typeof item.needs_human !== "boolean") found.push("needs_human must be true or false");
    if (typeof item.reason !== "string" || item.reason.trim() === "") found.push("reason is empty");
    return found;
  }

  // ---- scripts/route_ticket.py -----------------------------------------------------------
  function route(item, table) {
    const team = table[item.category];
    if (team === undefined) return null; // never guess a team
    return { team: team, urgent: item.priority === "P1" };
  }

  // ---- scripts/check_reply.py ------------------------------------------------------------
  function sentenceCount(text) {
    return text.trim().split(/(?<=[.!?])\s+/).filter(Boolean).length;
  }

  function bannedHits(text, cfg) {
    const lowered = text.toLowerCase();
    const hits = new Set();
    for (const lang of Object.keys(cfg.banned_phrases)) {
      for (const phrase of cfg.banned_phrases[lang]) if (lowered.includes(phrase)) hits.add(phrase);
    }
    return Array.from(hits).sort();
  }

  function internalWords(text, table) {
    const lowered = text.toLowerCase();
    const found = Object.values(table).filter((team) => lowered.includes(team.toLowerCase()));
    if (/\bP[123]\b/.test(text)) found.push("a priority label");
    return found;
  }

  function replyProblems(item, cfg, table, words) {
    const draft = item.draft;
    if (typeof draft !== "string" || draft.trim() === "") return ["draft is empty"];
    const found = [];
    const count = sentenceCount(draft);
    if (count < 3 || count > 5) found.push("draft has " + count + " sentences, needs 3 to 5");
    if (item.draft_language !== item.language || detect(draft, words).language !== item.language) {
      found.push("draft language does not match ticket language " + item.language);
    }
    const hits = bannedHits(draft, cfg);
    if (hits.length) found.push("banned promise phrase: " + hits.join(", "));
    const leaked = internalWords(draft, table);
    if (leaked.length) found.push("internal words in draft: " + leaked.join(", "));
    if (item.status !== "waiting_for_approval") found.push("status must be waiting_for_approval");
    return found;
  }

  // ---- scripts/audit_sample.py -----------------------------------------------------------
  const CHECK_NAMES = {
    1: "language is EN or FR",
    2: "category is one of the 6",
    3: "priority is one of the 3",
    4: "team matches the routing table",
    5: "draft is in the ticket's language",
    6: "no banned phrase and no internal words",
    7: "status is waiting_for_approval",
  };
  const STAGE_FOR_CHECK = { 1: "01_intake", 2: "02_classify", 3: "02_classify", 4: "03_route", 5: "04_reply", 6: "04_reply", 7: "04_reply" };

  function failedChecks(t, cfg, table, words) {
    const failed = [];
    if (!cfg.languages.includes(t.language)) failed.push(1);
    if (!cfg.categories.includes(t.category)) failed.push(2);
    if (!cfg.priorities.includes(t.priority)) failed.push(3);
    if (table[t.category] !== t.team) failed.push(4);
    const draft = t.draft || "";
    if (draft.trim() === "" || detect(draft, words).language !== t.language || t.draft_language !== t.language) failed.push(5);
    if (bannedHits(draft, cfg).length || internalWords(draft, table).length) failed.push(6);
    if (t.status !== "waiting_for_approval") failed.push(7);
    return failed;
  }

  function audit(tickets, cfg, table, words) {
    const ids = tickets.map((t) => t.id);
    const sampled = seededSample(ids, Math.min(cfg.sample_size, ids.length), cfg.sample_seed);
    const byId = {};
    tickets.forEach((t) => (byId[t.id] = t));
    const results = sampled.map((id) => {
      const failed = failedChecks(byId[id], cfg, table, words);
      return { id: id, passed: failed.length === 0, failed_checks: failed };
    });
    const passed = results.filter((r) => r.passed).length;
    return {
      sample_size: sampled.length,
      seed: cfg.sample_seed,
      sampled_ids: sampled,
      results: results,
      passed_count: passed,
      verdict: passed === sampled.length ? "PASS" : "FAIL",
    };
  }

  // ---- whole pipeline for recorded data ----------------------------------------------------
  function buildRows(data) {
    const seen = new Set();
    const rows = [];
    for (const ticket of data.tickets) {
      const reason = validate(ticket, seen);
      if (reason) {
        rows.push({ id: ticket.id, rejected: reason });
        continue;
      }
      seen.add(ticket.id);
      const lang = detect(ticket.subject + " " + ticket.body, data.words);
      const cls = data.classify[ticket.id];
      const routed = route(cls, data.routing);
      rows.push({
        id: ticket.id,
        subject: ticket.subject,
        body: ticket.body,
        received_at: ticket.received_at,
        language: lang.language,
        confidence: lang.confidence,
        category: cls.category,
        priority: cls.priority,
        needs_human: cls.needs_human,
        reason: cls.reason,
        team: routed ? routed.team : undefined,
        urgent: routed ? routed.urgent : false,
        draft: data.replies[ticket.id],
        draft_language: lang.language,
        status: "waiting_for_approval",
      });
    }
    return rows;
  }

  return {
    mulberry32, seededSample, score, detect, validate, classificationProblems, route,
    sentenceCount, bannedHits, internalWords, replyProblems, failedChecks, audit, buildRows,
    CHECK_NAMES, STAGE_FOR_CHECK,
  };
});

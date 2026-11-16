// Prints JSON the Python parity test compares against. Usage: node tests/js_parity.js
const fs = require("fs");
const path = require("path");
const T = require("../docs/triage.js");
const data = JSON.parse(fs.readFileSync(path.join(__dirname, "../docs/data/run.json"), "utf8"));
const bad = JSON.parse(fs.readFileSync(path.join(__dirname, "bad_tickets.json"), "utf8"));
const rows = T.buildRows(data);
const seen = new Set();
const badOut = bad.map((t) => { const r = T.validate(t, seen); if (!r) seen.add(t.id); return r; });
const audit = T.audit(rows, data.config, data.routing, data.words);
const replyProblems = rows.map((r) => T.replyProblems(r, data.config, data.routing, data.words));
const rnd = T.mulberry32(42);
console.log(JSON.stringify({
  languages: rows.map((r) => r.language),
  teams: rows.map((r) => r.team),
  sampled: audit.sampled_ids,
  verdict: audit.verdict,
  passed: audit.passed_count,
  reply_problem_count: replyProblems.filter((p) => p.length).length,
  bad_ticket_reasons: badOut,
  random: [rnd(), rnd(), rnd()].map((x) => Number(x.toFixed(6))),
}));

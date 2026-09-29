// Integration tests for the AFJEN web API: Express (JavaScript) -> bridge.py -> Python compiler engine.
// Run with:  npm test
const { test, before, after } = require("node:test");
const assert = require("node:assert/strict");
const { PythonBridge, createApp } = require("../server");

let bridge, server, base;

before(async () => {
  bridge = new PythonBridge();
  server = createApp(bridge).listen(0);
  await new Promise((resolve) => server.once("listening", resolve));
  base = `http://127.0.0.1:${server.address().port}`;
});

after(() => {
  bridge.stop();
  server.close();
});

const call = async (method, url, body) => {
  const res = await fetch(base + url, { method, headers: { "Content-Type": "application/json" },
                                        body: body ? JSON.stringify(body) : undefined });
  return { status: res.status, data: await res.json() };
};

test("health check reaches the Python engine", async () => {
  const { status, data } = await call("GET", "/api/health");
  assert.equal(status, 200);
  assert.equal(data.status, "ok");
});

test("translates by sense, not word by word", async () => {
  const ok = await call("POST", "/api/analyze", { text: "You dey ok" });
  assert.equal(ok.data.translations.en.text, "You are alright.");
  const normal = await call("POST", "/api/analyze", { text: "You dey dey ok so?" });
  assert.equal(normal.data.translations.en.text, "Are you normal?");
  assert.equal(normal.data.translations.fr.text, "Tu es normal ?");
});

test("verified statements come back as verified", async () => {
  const { data } = await call("POST", "/api/analyze", { text: "Driver, stop for junction, I don reach" });
  assert.equal(data.translations.en.method, "verified");
  assert.equal(data.translations.fr.text, "Chauffeur, arrêtez-vous au carrefour, je suis arrivé.");
  assert.equal(data.allFull, true);
});

test("never rejects any text", async () => {
  for (const text of ["x", "asdf qwerty 123 !!!", "the the the", "é à ü 你好 😀", "Brother, drop me. ".repeat(50)]) {
    const { status, data } = await call("POST", "/api/analyze", { text });
    assert.equal(status, 200);
    assert.equal(data.empty, false);
    assert.ok(data.translations.en.text.length > 0);
  }
});

test("dictionary is alphabetical and has 100+ words", async () => {
  const { data } = await call("GET", "/api/dictionary");
  assert.ok(data.total >= 100);
  const key = (w) => w.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const keys = data.rows.map((r) => key(r.word));
  assert.deepEqual(keys, [...keys].sort());
});

test("add and remove a word, and use it straight away", async () => {
  const add = await call("POST", "/api/dictionary", { word: "kwatest", type: "noun", english: "neighbourhood", french: "quartier", gender: "m" });
  assert.equal(add.data.ok, true);
  const seen = await call("POST", "/api/analyze", { text: "The taxi dey for kwatest" });
  assert.match(seen.data.translations.en.text, /neighbourhood/);
  const gone = await call("DELETE", "/api/dictionary", { word: "kwatest" });
  assert.equal(gone.data.ok, true);
  const bad = await call("POST", "/api/dictionary", { word: "two words", type: "noun", english: "a", french: "b" });
  assert.equal(bad.data.ok, false);
});

test("30 statements, and users can add their own", async () => {
  const list = await call("GET", "/api/statements");
  assert.equal(list.data.total >= 30, true);
  const text = "Waka go slow, road dey bad node test";
  const add = await call("POST", "/api/statements", { text, english: "Walk slowly, the road is bad.", french: "Marche doucement, la route est mauvaise.", topic: "Taxi & Commuting" });
  assert.equal(add.data.ok, true);
  const verified = await call("POST", "/api/analyze", { text });
  assert.equal(verified.data.translations.fr.method, "verified");
  const gone = await call("DELETE", "/api/statements", { text });
  assert.equal(gone.data.ok, true);
});

"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const vm = require("node:vm");
const fs = require("node:fs");

const code = fs.readFileSync("web/app.js", "utf8");
function browser() {
  const nodes = new Map();
  for (const id of ["evaluate", "export", "task_id", "target_id", "primary_metric",
                     "secondary_metric", "status_descriptor", "is_critical", "outputConsole",
                     "m-status", "m-tasks", "m-audit"]) {
    nodes.set(id, {value: "", textContent: "", checked: false, disabled: true,
      addEventListener(event, handler) { this[event] = handler; }});
  }
  const context = vm.createContext({document: {
    getElementById(id) { return nodes.get(id); }
  }, Blob, URL, Number, JSON});
  vm.runInContext(code, context);
  return {nodes, context};
}

test("threshold rules agree with the Python supervisor", () => {
  const {context} = browser();
  const evaluate = input => vm.runInContext("evaluate(" + JSON.stringify(input) + ")", context);
  const base = {task_id: "TEST", target_identifier: "KEY", primary_metric: 25,
    secondary_metric: 12, is_critical_flag: false, status_descriptor: "NOMINAL"};
  assert.equal(evaluate(base).overall_urgency, "ROUTINE");
  assert.equal(evaluate({...base, primary_metric: 26}).overall_urgency, "ELEVATED_RISK");
  assert.equal(evaluate({...base, secondary_metric: 13}).total_alerts, 1);
  assert.equal(evaluate({...base, is_critical_flag: true}).overall_urgency, "CRITICAL_STAT_PANIC");
  assert.equal(evaluate({...base, status_descriptor: "REJECT"}).total_alerts, 1);
  assert.equal(evaluate(base).cryptographic_signature_generated, false);
});

test("invalid browser input does not generate a dossier", () => {
  const {nodes} = browser();
  nodes.get("task_id").value = "../secret";
  nodes.get("target_id").value = "KEY";
  nodes.get("primary_metric").value = "5";
  nodes.get("secondary_metric").value = "4";
  nodes.get("evaluate").click();
  assert.match(nodes.get("outputConsole").textContent, /Validation error/);
  assert.equal(nodes.get("export").disabled, true);
});

test("valid browser input increments real local counters", () => {
  const {nodes} = browser();
  nodes.get("task_id").value = "TASK_1";
  nodes.get("target_id").value = "KEY";
  nodes.get("primary_metric").value = "26";
  nodes.get("secondary_metric").value = "4";
  nodes.get("evaluate").click();
  assert.equal(nodes.get("m-tasks").textContent, "1");
  assert.equal(nodes.get("m-audit").textContent, "1");
  assert.equal(nodes.get("export").disabled, false);
  assert.equal(JSON.parse(nodes.get("outputConsole").textContent).demonstration, true);
});

"use strict";

// Browser-only demonstration of the legacy operational rules.
// This file deliberately does not pretend to generate ML-DSA signatures.
const LIMITS = Object.freeze({ primary: 25, secondary: 12 });
const FLAGS = ["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"];
let processed = 0;
let alertCount = 0;
let lastResult = null;
const byId = id => document.getElementById(id);

function validateIdentifier(value, label) {
  if (!/^[A-Za-z0-9_-]{1,128}$/.test(value)) {
    throw new Error(label + " must contain 1–128 letters, digits, underscores, or hyphens.");
  }
  return value;
}

function evaluate(payload) {
  const alerts = [];
  if (payload.primary_metric > LIMITS.primary) {
    alerts.push({origin_worker: "InvariantQCWorker", urgency: "ELEVATED_RISK",
      summary: "Primary metric exceeds the demonstration threshold (25)"});
  }
  if (payload.is_critical_flag || payload.secondary_metric > LIMITS.secondary) {
    alerts.push({origin_worker: "SafetyEscalationWorker",
      urgency: payload.is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      summary: "Critical flag set or secondary metric exceeds the demonstration threshold (12)"});
  }
  if (FLAGS.some(flag => payload.status_descriptor.toUpperCase().includes(flag))) {
    alerts.push({origin_worker: "ProtocolConformanceWorker", urgency: "ELEVATED_RISK",
      summary: "Descriptor matches an operational alert keyword"});
  }
  const urgency = alerts.some(a => a.urgency === "CRITICAL_STAT_PANIC")
    ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK" : "ROUTINE";
  return {
    demonstration: true,
    cryptographic_signature_generated: false,
    compliance_claim: "None: thresholds are project-specific examples, not NIST FIPS 204 tests.",
    task_id: payload.task_id,
    target_identifier: payload.target_identifier,
    overall_urgency: urgency,
    integrity_status: urgency === "CRITICAL_STAT_PANIC" ? "RECALIBRATION_REQUIRED"
      : urgency === "ELEVATED_RISK" ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
    total_alerts: alerts.length,
    alerts
  };
}

function runAudit() {
  const output = byId("outputConsole");
  try {
    const primary = Number(byId("primary_metric").value);
    const secondary = Number(byId("secondary_metric").value);
    if (byId("primary_metric").value.trim() === "" || byId("secondary_metric").value.trim() === "" ||
        !Number.isFinite(primary) || !Number.isFinite(secondary)) {
      throw new Error("Both numeric metrics are required and must be finite.");
    }
    const status = byId("status_descriptor").value.trim();
    if (status.length > 64) throw new Error("Status descriptor must be 64 characters or fewer.");
    const payload = {
      task_id: validateIdentifier(byId("task_id").value.trim(), "Task ID"),
      target_identifier: validateIdentifier(byId("target_id").value.trim(), "Target ID"),
      primary_metric: primary,
      secondary_metric: secondary,
      status_descriptor: status,
      is_critical_flag: byId("is_critical").checked
    };
    lastResult = evaluate(payload);
    processed += 1;
    alertCount += lastResult.total_alerts;
    byId("m-status").textContent = lastResult.overall_urgency;
    byId("m-tasks").textContent = String(processed);
    byId("m-audit").textContent = String(alertCount);
    output.textContent = JSON.stringify(lastResult, null, 2);
    byId("export").disabled = false;
  } catch (error) {
    lastResult = null;
    byId("export").disabled = true;
    output.textContent = "Validation error: " + error.message;
  }
}

function exportResult() {
  if (!lastResult) return;
  const blob = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], {type: "application/json"});
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "audit-demo-report.json";
  anchor.click();
  URL.revokeObjectURL(url);
}

byId("evaluate").addEventListener("click", runAudit);
byId("export").addEventListener("click", exportResult);

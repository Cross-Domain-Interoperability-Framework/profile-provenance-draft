"""The data-flow join in galaxyROCrateToCDIFActions must close.

A consumer names an input entity; the step that produced it names the same
entity as an output. If the two mint that @id differently the graph silently
falls apart: the ids still look plausible, every example still passes the JSON
Schema gate, and nothing reports that no activity produces what the next one
consumes. Measured on 2026-11-07, before `_output_entity_id` existed, 110 of
113 consumed entity ids in the six committed examples were produced by no
activity at all.

The four cases below are the four ways a step can reach the data flow: CWL
declares the output or the Galaxy job does, and the consumer reads a CWL source
or a job dataset mapping. The bug was never visible within one branch -- both
CWL sides agreed with each other and both job sides agreed with each other. It
appeared when a producer took one branch and its consumer took the other, so
the cross pairs are the ones that matter.

Run: python tools/test_galaxy_actions_dataflow.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import galaxyROCrateToCDIFActions as G


STEP_IDS = {"step1": "#step-1-step1", "step2": "#step-2-step2"}

failures = []


def check(label, got, want):
    if got != want:
        failures.append("%s\n     got:  %s\n     want: %s" % (label, got, want))


def ids_of(node, key):
    out = []
    for item in node.get(key) or []:
        if isinstance(item, dict) and "@id" in item:
            out.append(item["@id"])
    return out


def cwl_step(name, sources=(), outputs=()):
    src_steps = set()
    for s in sources:
        if "/" in s:
            src_steps.add(s.split("/")[0])
    return {
        "name": name,
        "inputs": {},
        "sources": list(sources),
        "source_steps": src_steps,
        "outputs": list(outputs),
    }


# --- producer side: CWL-declared output, then job-declared output --------

prod_cwl = G._build_step_activity(
    cwl_step("step1", outputs=["outfile"]), None, STEP_IDS)

prod_job = G._build_step_activity(
    cwl_step("step1"), {"tool_id": "t", "tool_version": "1"}, STEP_IDS,
    job_index=0, job_inputs=[[]], job_outputs=[[("outfile", "ds1")]],
    matched_steps=[(cwl_step("step1"), {"tool_id": "t"})])

check("CWL producer and job producer name the same output differently",
      ids_of(prod_job, "schema:result"), ids_of(prod_cwl, "schema:result"))

produced = ids_of(prod_cwl, "schema:result")
check("a CWL producer declares exactly one result", len(produced), 1)

# --- consumer side: CWL source, then job dataset mapping -----------------

cons_cwl = G._build_step_activity(
    cwl_step("step2", sources=["step1/outfile"]), None, STEP_IDS)

cons_job = G._build_step_activity(
    cwl_step("step2"), {"tool_id": "t", "tool_version": "1"}, STEP_IDS,
    job_index=1,
    job_inputs=[[], [("in1", "ds1", 0, "outfile")]],
    job_outputs=[[], []],
    matched_steps=[(cwl_step("step1"), {"tool_id": "t"}),
                   (cwl_step("step2"), {"tool_id": "t"})])

# job_to_step is keyed on the matched_steps index, so step1 is index 0
check("CWL consumer does not join to the CWL producer",
      ids_of(cons_cwl, "schema:object"), produced)
check("job consumer does not join to the CWL producer",
      ids_of(cons_job, "schema:object"), produced)

# --- the properties that had to go --------------------------------------

for node, what in ((prod_cwl, "CWL producer"), (cons_job, "job consumer")):
    for gone in ("schema:position", "prov:wasInfluencedBy",
                 "prov:wasInformedBy"):
        if gone in node:
            failures.append("%s still carries %s" % (what, gone))
    if "schema:CreateAction" in (node.get("schema:additionalType") or []):
        failures.append("%s still marked schema:CreateAction" % what)

# --- inputs are schema:object, and prov:used is left for roles -----------

if "prov:used" in cons_cwl:
    failures.append("data inputs are back in prov:used, which is role-keyed")
check("inputs are not in schema:object", bool(cons_cwl.get("schema:object")), True)

# --- one minting site, not two ------------------------------------------
# The defect was two independent expressions building the same id. Anything
# that formats "output-" into an @id outside the helper is a second one.

with open(G.__file__.replace(".pyc", ".py"), encoding="utf-8") as fh:
    body = fh.read()
hand_minted = [
    m for m in re.findall(r'"@id": f?"[^"]*output-[^"]*"', body)
]
if hand_minted:
    failures.append("output @id minted outside _output_entity_id: %s"
                    % hand_minted)

# --- report -------------------------------------------------------------

if failures:
    print("FAILED (%d)" % len(failures))
    for f in failures:
        print("  - %s" % f)
    sys.exit(1)

print("ok: data-flow join closes across all four producer/consumer branches")
print("    canonical output id: %s" % produced[0])

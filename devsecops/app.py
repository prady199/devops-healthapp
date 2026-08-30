"""
Healthcare Patient Portal - security hardened build.

Security controls demonstrated in this module:
  * No credentials in source. The API key is injected at runtime from a
    Kubernetes Secret, which is itself created from the Jenkins credential store.
  * Every access to patient data is written to an audit log (stdout, collected
    by the cluster), which is a core requirement of health data regulation.
  * Patient records are synthetic. No real protected health information.
  * The service refuses to start if no API key was supplied.
"""

import logging
import os
import sys
from datetime import datetime, timezone

from flask import Flask, jsonify, request

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("healthportal")

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
VERSION = os.getenv("APP_VERSION", "v1")

if not API_KEY:
    log.error("STARTUP ABORTED - API_KEY was not supplied by the Secret")
    sys.exit(1)

# Synthetic records only - never real patient data.
PATIENTS = [
    {"id": "P-1001", "name": "Record A", "ward": "Cardiology", "status": "admitted"},
    {"id": "P-1002", "name": "Record B", "ward": "Neurology", "status": "discharged"},
    {"id": "P-1003", "name": "Record C", "ward": "Orthopaedics", "status": "admitted"},
]

AUDIT_TRAIL = []


def audit(event, allowed):
    entry = {
        "time": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "source_ip": request.remote_addr,
        "decision": "ALLOW" if allowed else "DENY",
    }
    AUDIT_TRAIL.append(entry)
    log.info("AUDIT %s", entry)
    return entry


def authorised():
    return request.headers.get("X-API-Key") == API_KEY


@app.route("/")
def home():
    return f"""
    <body style="font-family:sans-serif;max-width:640px;margin:60px auto">
      <h1>Healthcare Patient Portal</h1>
      <p>Build: {VERSION}</p>
      <h3>Active security controls</h3>
      <ul>
        <li>Runs as a non-root user with a read-only root filesystem</li>
        <li>All Linux capabilities dropped, privilege escalation blocked</li>
        <li>API key sourced from a Kubernetes Secret, never from source code</li>
        <li>Least-privilege service account, no API token mounted</li>
        <li>Network policy restricts ingress and egress traffic</li>
        <li>Every patient data request is written to an audit trail</li>
      </ul>
      <p><code>/api/patients</code> requires a valid <code>X-API-Key</code> header.</p>
    </body>"""


@app.route("/health")
def health():
    return jsonify(status="ok", version=VERSION)


@app.route("/api/patients")
def patients():
    if not authorised():
        audit("patient_records_read", allowed=False)
        return jsonify(error="unauthorised - valid X-API-Key required"), 401
    audit("patient_records_read", allowed=True)
    return jsonify(count=len(PATIENTS), records=PATIENTS)


@app.route("/audit")
def audit_log():
    return jsonify(entries=len(AUDIT_TRAIL), trail=AUDIT_TRAIL[-20:])


if __name__ == "__main__":
    log.info("Patient portal starting on port 5000, build %s", VERSION)
    app.run(host="0.0.0.0", port=5000)

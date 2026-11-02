# 🛡️ Inquira — The Trust Layer for Professional AI
<img width="1350" height="598" alt="Inquira" src="https://github.com/user-attachments/assets/ad3148fc-4e55-41bc-b495-041c780f3ebc" />

A governance-first AI prototype that evaluates every query against the
**EU AI Act (Regulation (EU) 2024/1689)** before any output is returned.
Four role-based workspaces, dual-lens verdicts (Policy + Governance),
a Responsible-AI dashboard, and an exportable compliance certificate.

> **Prototype only.** Not CE-marked. Not placed on the EU market. No legal compliance claim.

---

## Table of Contents

- [Features](#-features)
- [Workspaces & Risk Classification](#-workspaces--risk-classification)
- [How It Works](#-how-it-works)
- [EU AI Act Alignment](#-eu-ai-act-alignment)
- [Installation](#-installation)
- [Running the App](#-running-the-app)
- [Usage](#-usage)
- [Compliance Certificate](#-compliance-certificate)
- [Project Structure](#-project-structure)
- [Limitations](#-limitations)
- [Roadmap](#-roadmap)

---

## ✨ Features

- **4 role-based workspaces** — Professional, Business Owners, Students, Teachers.
- **Google-style prompt bar** with optional file attachment for grounding.
- **Art. 5 Prohibited-Practice Shield** — blocks social scoring, manipulation,
  workplace/education emotion inference, biometric categorisation, real-time
  public biometrics, and predictive policing (hard block, no override).
- **Named human approver gate** for high-risk systems (Art. 14(4)(d)).
- **RAI Governance dashboard** — traffic-light status (🟢 / 🟡 / 🔴), confidence
  metric, 4-pillar checklist, "Why Flagged" explanation, **Auto-Fix** button,
  and **JSON certificate export**.
- **Dual-angle verdict** — Policy (is this lawful?) vs. Governance (were
  controls operated correctly?), each row cross-referenced to its article.
- **Hash-chained audit ledger** written to `compliance/events.jsonl`
  (Art. 12 record-keeping; Art. 19 automatically generated logs).
- **Mandatory AI disclosure stamp** on every allowed result (Art. 13 & 50),
  including a right-to-contest notice (Art. 86).

---

## 🗂️ Workspaces & Risk Classification

| Workspace | System ID | Risk tier | Annex III | Human oversight |
|-----------|-----------|-----------|-----------|------------------|
| 💼 Professional | `professional.trust_query` | **HIGH** | 5(b) — creditworthiness & financial | Required |
| 🏢 Business Owners | `business.trust_query` | **HIGH** | 5(b) — creditworthiness & financial | Required |
| 🎓 Students | `student.trust_query` | **LIMITED** | — | Optional |
| 📚 Teachers | `teacher.trust_query` | **HIGH** | 3(b) — education & assessment | Required |

---

## ⚙️ How It Works

Every query passes through a five-stage pipeline:

1. **Prohibited-Practice Shield (Art. 5)** — regex scan over prompt + attachment; any match is a hard block.
2. **Human Oversight Gate (Art. 14)** — high-risk systems require a named approver.
3. **Responsible-AI checklist** — four pillars (transparency, bias, privacy, accuracy) evaluated per system tier.
4. **Disclosure build (Art. 13, 50)** — mandatory AI-content stamp attached to allowed output.
5. **Hash-chained ledger write (Art. 12, 19)** — tamper-evident event record with `prev_hash` continuity.

Results are rendered through **two explicit lenses**:

| Lens | Question answered |
|------|-------------------|
| 🏛️ **Policy** | Is this use lawful under the EU AI Act? |
| ⚙️ **Governance** | Did the organisation operate its controls correctly? |

---

## 🇪🇺 EU AI Act Alignment

| Article | Topic | Implementation |
|---------|-------|----------------|
| **Art. 5** | Prohibited practices | `scan_prohibited()` — hard block |
| **Art. 6 / Annex III** | High-risk classification | `AI_SYSTEM_REGISTRY` |
| **Art. 10** | Data governance & bias | "Bias" and "Privacy" pillars |
| **Art. 12** | Record-keeping | `HashChainedLedger.log()` |
| **Art. 13** | Transparency to deployers | `build_disclosure()` |
| **Art. 14** | Human oversight | `human_oversight_gate()` |
| **Art. 15** | Accuracy & robustness | "Technical Accuracy" pillar |
| **Art. 19** | Automatically generated logs | Hash-chained `events.jsonl` |
| **Art. 50** | AI-content marking | Disclosure stamp on every output |
| **Art. 86** | Right to explanation / contest | Surfaced in disclosure |

---

## 🚀 Installation

**Prerequisites:** Python 3.10+

```bash
# Clone or download the project
git clone https://github.com/<your-org>/inquira.git
cd inquira

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install streamlit

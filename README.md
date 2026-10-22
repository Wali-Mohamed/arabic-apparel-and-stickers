# Custom HTV & High-Vis Apparel Studio

[![CI/CD Pipeline](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/actions/workflows/cicd.yml/badge.svg)](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/actions)


An end-to-end full-stack e-commerce application designed for personalizing, rendering, and ordering Arabic Heat Transfer Vinyl (HTV) stickers, high-vis safety tags, and custom apparel.

---

## 📸 Demo & Public URL

* **Live Application:** [https://your-app-domain.com](https://your-app-domain.com) *(or staging link)*
* **Public Task Tracker:** [View GitHub Issues](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues)

---

## 1. Problem Description (2 / 2 Points)

### 🎯 The Problem
Custom apparel and sticker printing stores often struggle to handle non-Latin script personalizations (such as Arabic calligraphy and typography). Standard customizers frequently misrender right-to-left (RTL) text, fail to provide accurate live previews of complex Google Arabic fonts, and lack clear options for high-visibility material sizing and shape selection. On the merchant side, manually verifying custom Arabic text and high-vis safety requirements leads to high error rates, slow fulfillment times, and wasteful refunds.

### 💡 System Functionality
The **Arabic Apparel & Stickers Studio** automates the custom order pipeline for Arabic HTV stickers, safety tags, and high-visibility apparel. The platform provides:
1. **Interactive Real-Time Preview:** A dynamic canvas that correctly renders RTL Arabic text in real time across **3 Google Arabic Fonts** (*Amiri*, *Cairo*, *Tajawal*) and high-visibility HTV colors.
2. **Product Catalog & Customization Engine:**
   * **HTV Arabic Stickers:** Interactive selection of 3 sizes (Small 10cm, Medium 15cm, Large 20cm), HTV material options, and color themes.
   * **High-Vis Safety Tags:** Specialized support for Arabic-only text in **Diamond** (short names) and **Rectangle** (long names) geometric layouts, including pre-configured B-Series (ب س) tags.
   * **High-Vis Black Sweater ("Be Seen"):** Sweatshirt visualizer featuring custom high-vis Arabic back/chest typography.
3. **Automated Order Processing & Persistence:** Stores order configurations, custom SVG path renders, and user parameters safely in a PostgreSQL database with strict schema validation.
4. **Order Policy Enforcement:** Automatic display and agreement validation for application instructions and non-refundable custom item disclosures before payment processing.

### 🤖 Expected System Behavior
* **User Workflow:** The customer visits the site, enters Arabic text, selects a Google Font, picks a high-vis material color/size, verifies the real-time preview, agrees to non-refundable custom terms, and places an order.
* **Backend Processing:** The backend validates the inputs (e.g., ensuring Arabic character boundaries and valid font IDs), generates a persistent record, calculates pricing, and emits OpenTelemetry traces and structured logs for every step.
* **Merchant/Production Flow:** Orders are persisted with precise design vectors and metadata ready for vinyl cutting machines.

---

## 2. Product Specification & Task Tracker (2 / 2 Points)

### 📋 Product Specification (`spec.md`)
The full, granular technical product specification—including system architecture, API schemas, database models, and agent interaction rules—is located in [`spec.md`](./spec.md) and [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md).

#### Core Technical Acceptance Criteria:
* **AC-1 (Frontend Preview):** Typing in the input field updates the live visual preview immediately with correct RTL direction and selected Google Font (*Amiri*, *Cairo*, or *Tajawal*).
* **AC-2 (Product Matrix):** Users can customize and configure HTV Stickers (3 sizes), High-Vis Tags (Diamond vs. Rectangle shape validation), and Black Sweaters.
* **AC-3 (Data Persistence):** Submitting an order persists the full configuration (text, font, shape, size, color, price) to PostgreSQL via the REST API.
* **AC-4 (Validation):** Input fields block non-Arabic text where required (e.g., High-Vis Tags) and require policy acknowledgement before checkout.

---

### 📌 Public Task Tracker & Agent Execution

This project strictly follows **Spec-Driven, Agentic Development**. All features, bug fixes, and infrastructure setup tasks were specified as structured issues with clear Acceptance Criteria (AC) prior to code generation.

* **Public Task Board:** [View GitHub Project Board](https://github.com/users/[your-username]/projects/[project-number])
* **Public Issues List:** [View GitHub Issues](https://github.com/[your-username]/[your-repo]/issues?q=is%3Aissue)

#### Task & Agent Workflow:
1. **Specification:** Human/PM defines user stories in GitHub Issues with strict AC checkboxes.
2. **Agent Execution:** Autonomous coding agents (Claude Code / Cursor) read `AGENTS.md` and the linked issue specs to execute development tasks.
3. **Verification:** Agents run automated unit and integration tests to verify AC compliance before submitting pull requests.

#### Example Issue Traceability:

| Issue ID | Task Title | Defined Acceptance Criteria | Agent Action / PR |
| :--- | :--- | :--- | :--- |
| **[#1]** | Create Full-Stack App Skeleton | - FastAPI backend & React frontend initialized<br>- PostgreSQL container integrated | Agent created base architecture & Docker Compose configuration. |
| **[#2]** | Arabic Live Preview Canvas | - Render 3 Google Fonts (*Amiri*, *Cairo*, *Tajawal*)<br>- Handle dynamic color & size switching | Developer Agent created custom React canvas component. |
| **[#3]** | Tag & Sweater API Schemas | - REST endpoint POST `/api/orders`<br>- Database migration for sticker/tag schemas | Agent generated Pydantic models, Alembic migration, and SQL database routes. |
| **[#4]** | Telemetry & Observability | - OpenTelemetry trace injection<br>- Grafana metric dashboard setup | Agent instrumented FastAPI routes and exported trace IDs. |

---

## ⚡ Quick Start (Single Command Run)

To launch the full system locally (Frontend, Backend, PostgreSQL Database, Prometheus, and Grafana):

```bash
docker compose up --build

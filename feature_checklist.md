# AI-UMROH FEATURE CHECKLIST & IMPLEMENTATION BACKLOG

This backlog breaks down the **AI-Umroh (WhatsApp Bot)** blueprint and use case simulations into modular, implementable features. Progress can be tracked here step-by-step as we develop the system.

---

## 🚀 FEATURE 1: Database & Persistence Layer (Repository Pattern)
*Establish a clean database layer to track pilgrim profiles and booking transactions.*

- [ ] **1.1. Database Schema Setup**
  - Define `Jemaah` model: `id` (UUID), `whatsapp_number` (Unique Key), `nama_lengkap`, `domisili`, `status_pembayaran` (`POTENTIAL`, `PENDING_DP`, `WAITING_VERIFY`, `PAID`).
  - Define `Booking` model: `id` (INV-XXXX format), `jemaah_id` (FK), `paket_nama` (Economy/Premium), `jumlah_pax`, `total_tagihan` (Decimal), `kode_unik` (3-digit int), `bukti_transfer_url` (Nullable).
- [ ] **1.2. Repository Class Implementations**
  - Create standard CRUD methods: `get_or_create_jemaah()`, `create_booking()`, `upload_transfer_proof()`, and `verify_payment()`.
- [ ] **1.3. Local Migration & Seed Scripts**
  - Run database migration and seed initial package prices (e.g., economy package starting at IDR 28,500,000).

---

## 💬 FEATURE 2: WhatsApp Gateway & Media Routing
*Connect to the WhatsApp network to handle incoming/outgoing messages and media files.*

- [ ] **2.1. Client Connection & Authentication**
  - Initialize the WhatsApp gateway (e.g., using a local API client or gateway wrapper).
  - Handle QR Code generation for device pairing and save session tokens for persistent login.
- [ ] **2.2. Message Parsing & Router**
  - Parse incoming text messages and route them to the LangGraph AI Orchestrator.
  - Detect incoming media (images) and recognize them as payment proofs.
- [ ] **2.3. Document Attachment Sender**
  - Implement a helper to send generated PDF invoice files directly to the WhatsApp chat as standard documents (not simple links).

---

## 🧠 FEATURE 3: LangGraph Agent & State Orchestrator
*Construct the brain of the chatbot using LangGraph, handling the conversation state and agent routing.*

- [ ] **3.1. Graph State Definition (`state.py`)**
  - Define `UmrohAgentState` containing message history, pilgrim data, booking details, and payment/bot-mute statuses.
- [ ] **3.2. AI Prompt & Persona Engineering (Salsa)**
  - Implement system instructions for Salsa: extremely friendly Indonesian-speaking virtual assistant, utilizing relevant emojis.
- [ ] **3.3. Sales Manifest Node (`nodes.py`)**
  - Design the node that listens to manifest details (Name, Pax Count, Domicile), parses them, and updates the local state.
- [ ] **3.4. Guardrails & Handling Objections (`edges.py` / `nodes.py`)**
  - **Objection Handler**: Instantly provide reassuring, highly structured bullet points on Kemenag PPIU License, Corporate-only accounts, and Physical office locations.
  - **Strict Guardrails**: Politely steer the conversation back to Umrah packages if the user goes off-topic (e.g., weather inquiries).

---

## 🧮 FEATURE 4: Pricing Engine & Unique Code Calculator
*Calculate transactional totals dynamically with unique numbers for automatic mutation detection.*

- [ ] **4.1. Total Booking Fee Calculator**
  - DP formula: `Total DP = (5,000,000 * Jumlah Peserta) + Kode Unik`.
  - Calculate total remaining package cost for the final invoice.
- [ ] **4.2. Unique Code Pool Generator**
  - Generate a 3-digit random number (`001` - `999`).
  - *Optional:* Keep track of active codes to prevent duplicate unpaid amounts in the same window.

---

## 📄 FEATURE 5: Premium PDF Invoice Generator
*Dynamically create gorgeous, official PDF invoices inside the backend.*

- [ ] **5.1. Invoice Template Layout (Design)**
  - Create a clean layout containing: PT Berkah Umroh logo, Invoice ID, Date, Pilgrim Manifest details, itemized breakdown (Package Cost, DP, Unique Code), and official BSI payment account details.
- [ ] **5.2. HTML-to-PDF / PDFKit Compiler**
  - Build a module that compiles the invoice details into a physical PDF file.
  - Save the file to a secure directory (or cloud storage) and return the path/URL.

---

## 🛑 FEATURE 6: Payment Verification & Human-in-the-Loop Muting
*Pause the bot and transition to human-driven verification once the payment proof is uploaded.*

- [ ] **6.1. Image Upload & State Shift**
  - Save the uploaded image to the server, update `bukti_transfer_url`, and shift the pilgrim status to `WAITING_VERIFY`.
- [ ] **6.2. Bot Muting (LangGraph Breakpoint/Interrupt)**
  - Configure the LangGraph compiler to interrupt the thread *before* moving to payment verification nodes: `compile(checkpointer=memory, interrupt_before=["verify_payment_node"])`.
  - Inhibit the bot from auto-responding to any subsequent messages from that phone number during the `WAITING_VERIFY` state.
- [ ] **6.3. Admin Resume Endpoint**
  - Implement an endpoint or CLI command for the finance team: `/verify-payment?status=success`.
  - Upon success, update the graph state (`payment_status = PAID`), resume the graph thread, and trigger the bot to send the "Verification Success" congratulations message.

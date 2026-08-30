# Frontend Development Guide: NexBill

To build a premium frontend for NexBill, you should follow modern best practices for SaaS applications.

## 🛠️ Required Frontend Changes

1.  **Secure Authentication & User Management**:
    - Implement a full auth flow: Registration, Login, Token Refresh, and Role-Based Access Control (RBAC).
    - **Password Management**: Flows for Forgot Password, Reset Password (using token), and Change Password.
    - **Team Management**: Admin UI to Invite Users (`POST /auth/invite`), view pending invites (`GET /auth/invites`), and list active users (`GET /auth/users`).
    - **Invited User Flow**: Dedicated route `/register-invited/{token}` for new users to complete their setup.

2.  **Dynamic Dashboard & Reports**:
    - Build a high-level dashboard utilizing multiple endpoints:
      - `GET /reports/revenue`: "Revenue over Time" chart (Line/Area chart).
      - `GET /reports/aging`: Visualize the Aging Receivables risk buckets (Pie chart) to highlight overdue collections.
      - `GET /reports/tax-summary`: Display yearly tax summaries.

3.  **Client Management (CRM)**:
    - **CRUD Operations**: Build a list view and profile view for clients (`GET /clients`).
    - Include functionality to Create, Update, and Soft-Delete (`DELETE /clients/{uid}`) clients.

4.  **Contract Management**:
    - **New Feature**: Implement a Contracts section.
    - Features: List all contracts, Create new contracts, Update terms, Pause active contracts, and Cancel contracts (which also voids pending invoices).

5.  **Invoice Management**:
    - Create a multi-step invoice builder. Include status tracking and optimistic updates.
    - **Actions**:
      - Send Invoice (`POST /invoices/{uid}/send`) moving it from DRAFT to SENT.
      - Record Payment (`POST /invoices/{uid}/payments`) against an invoice.
      - "Live Preview" or a direct "Download PDF" button that calls the `GET /invoices/{uid}/pdf` endpoint.

6.  **Branding Engine & Settings**:
    - Implement a settings page where Admins can live-preview color and font changes before saving them to the backend via `PATCH /brand/`.
    - **Logo Management**: Support uploading logos (`POST /brand/logo`) and resetting to defaults (`POST /brand/reset`).

7.  **UUIDv7 Integration**:
    - Ensure all routing uses the `internal_id` (UUIDv7) rather than sequential IDs.
    - This is already handled by the backend endpoints expecting UUID path parameters.

---

## 🚀 Prompt for Frontend Development

Copy and use this prompt to generate the frontend codebase:

```text
Act as a Senior Frontend Engineer. Build a premium, enterprise-grade Invoice Management System (SaaS) called "NexBill" using Next.js 14+ (App Router), TypeScript, Tailwind CSS, and Shadcn/UI.

### Core Architecture:
1. **Design System**: Use a sleek "Glassmorphism" aesthetic with a semi-transparent sidebar, soft shadows, and a sophisticated Dark Mode. Use Inter or Outfit as the primary typography.
2. **State Management**: Use React Query (TanStack Query) for all server-state handling and caching. Use Axios for API requests with a global interceptor for JWT handling (including Token Refresh).
3. **Data Visualization**: Integrate Tremor or Recharts for the Dashboard (Revenue trends, Aging buckets, and Tax summaries).
4. **Forms**: Use React Hook Form with Zod for robust client-side validation.

### Pages to Implement:
1. **Dashboard**: High-level metrics cards, Revenue Area Chart (`/reports/revenue`), Aging Buckets Pie Chart (`/reports/aging`), and Tax Summary (`/reports/tax-summary`).
2. **Clients**: A CRM-style list and profile view for clients (CRUD and Soft-delete capability).
3. **Contracts**: Management interface to Create, View, Pause, and Cancel billing contracts.
4. **Invoices**: A master-detail view for managing invoices. Include a "Create Invoice" flow, Send Invoice action, Record Payment modal, and PDF downloader.
5. **Auth & Profile**: Login (JWT), Registration, Forgot/Reset Password, Change Password, and a "Complete Invitation" page for new users.
6. **Settings & Admin**:
   - **Branding**: Real-time preview of theme colors, typography, Logo upload, and Reset to Defaults.
   - **Organization**: User management list (`/auth/users`), viewing pending invites (`/auth/invites`), and an "Invite Colleague" action (Admin only).

### Technical Requirements:
- All dynamic routes must use UUIDv7 (e.g., /invoices/[internal_id]).
- Implement "Optimistic Updates" for status changes (e.g., marking an invoice as SENT or PAID).
- Ensure 100% responsiveness for Mobile and Tablet.
- Implement accessible components (Radix UI / Shadcn).

API Base URL: http://localhost:8000/api/v1
```

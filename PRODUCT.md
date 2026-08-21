# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Reflex: full-stack Python with Radix-based components compiled to a React frontend. PostgreSQL is the planned production datastore.

## Users

- Philippine small service-business owners who need to accept bookings, manage appointments, and issue invoices without relying on spreadsheets.
- Their customers, who need a quick public booking experience without an account.
- Portfolio reviewers who need to understand and safely explore the end-to-end product.

## Product Purpose

Takdora gives a configurable appointment-based business one dependable path from public booking through owner operations to an invoice with manually tracked payment status. Success means a real owner can configure a business, receive a booking, confirm it by email, complete the work, and issue a PDF invoice.

## Positioning

Philippines-first, configurable booking and invoice operations for varied small service businesses rather than one industry-specific booking tool. v1 intentionally keeps payments manual while making the core workflow dependable.

## Operating Context

Owners configure a single private business workspace, set services and availability, and manage customer-requested changes. Customers use a public business page. A portfolio visitor can use a safe demo account and pre-filled example business. The marketing site has multiple pages and its primary call to action is "Create your business."

## Capabilities and Constraints

- Public booking pages, private owner dashboard, email confirmation, PDF invoices, and manual payment-status tracking.
- One owner and one workspace in v1; customers do not use accounts or self-manage booking changes.
- Default market settings suit the Philippines while each business can configure branding, currency, invoice details, services, and working hours.
- Generated invoices are BIR-aware but must never be represented as registered BIR-compliant e-invoices or sales reporting.
- The finished product must be publicly deployable, responsive, tenant-safe, and accessible.

## Brand Commitments

Takdora is a Filipino-inspired name connecting *takda* (appointment/scheduled time) and *oras* (time). The product should feel clear, capable, and welcoming to small-business owners without becoming tied to a single business type.

## Evidence on Hand

- Planning documents in `.planning/` define the product workflow and phase decisions.
- No existing logo, product screenshots, customer testimonials, or customer case studies. Marketing must use generated original visuals, real product screenshots once available, and clearly labelled demo examples; it must not invent customer claims.

## Product Principles

- Make the normal workflow obvious and keep exceptions out of the main path.
- Preserve trust: booking times, invoices, payment states, and private customer data must be reliable.
- Give small businesses polished defaults without forcing design work on them.
- Show useful recovery guidance whenever something goes wrong.

## Accessibility & Inclusion

Use clear plain-language copy, keyboard-accessible interaction alternatives, responsive layouts, and sufficient contrast for public and owner-facing flows.

# Bureau Automation (CRM Robot)

![Cover](./assets/cover.png)

**Role:** Backend automation  
**Status:** Production (optional — can be stopped when unused)  
**Stack:** FastAPI · CRM webhooks · OCR · DOCX fill · mail agent · HMAC callbacks

## Overview

Webhook-driven robot: on CRM stage change, assemble deal files, OCR passport fields, fill claim templates, upload letters, ask the mail agent to send, then classify replies.

## What I built

- Stage-gated pipeline with file locks per deal
- PDF classification (passport vs bureau reports)
- Document fill using a ready signature image (not fragile signature OCR)
- Strict CRM category guards before any download/write
- PII masking in logs

## Results

- Mass standard correspondence without manual copy-paste
- Clear split: robot for volume, lawyer UI for complex/retry cases

## Hard problem

**Robot touching the wrong CRM funnels** (partners / installment) would corrupt deals.  
**Fix:** allowlist/blocklist checked **before** downloading files; optional stack shutdown to save RAM when unused.

## Confidentiality

No webhook URLs, HMAC secrets, or sample letters published.

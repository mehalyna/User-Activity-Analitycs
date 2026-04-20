# User-Activity-Analitycs

## Project Overview

This project is a minimal demo application for collecting and analyzing user activity events in an internet service.

The backend is built with **Django** and exposes a small REST API for recording events such as:

* clicks
* page views
* navigations
* add-to-cart actions

Event data is stored in **HBase**, which is used as the main event store. The goal of the demo is to show how HBase works well for large volumes of append-only activity data and time-based access patterns.

The project is intentionally kept small and focused. It is not a full analytics platform. It demonstrates only the essential flow:

1. receive an event from the API
2. store the event in HBase
3. read activity history for one user
4. produce a simple daily activity report

## Why This Project Uses HBase

HBase is a good fit for this demo because the system works with a large number of user events, and the most common access patterns are:

* get activity for one user
* get activity for one day
* aggregate events by date

This makes HBase a practical choice for showing:

* fast writes
* row-key based reads
* sparse, wide-column storage
* time-oriented data modeling

## Minimal Functional Scope

The demo includes only the minimum set of features needed to present the HBase workflow:

* create an event through API
* save the event to HBase
* read all events for a user within a date range
* read events for a specific day
* show a simple daily summary

No advanced authentication, complex dashboards, or real-time streaming are included in the minimal version.

## Suggested Data Model

A simple HBase table can be used for storing activity events.

### Table: `user_activity`

Suggested row key format:
`user_id#date#event_id`

Example:
`42#2026-04-20#000001`

Suggested columns:

* `event_type`
* `page_url`
* `target_id`
* `created_at`
* `metadata`

This structure makes it easy to read all events for one user in a given time range and keeps the access pattern aligned with the project goals.

## Main Components

* **Django API**. receives activity events and provides read endpoints
* **HBase storage layer**. stores activity events
* **reporting logic**. builds simple summaries by day or by user

## API Endpoints

The demo can be implemented with just a few endpoints:

* `POST /api/events/` - create a new activity event
* `GET /api/users/{user_id}/events/` - get events for one user
* `GET /api/reports/daily/` - get a daily activity summary

## Epics

### Epic 1. Project Setup

Set up the Django project, configure the environment, and connect the application to HBase. This epic includes basic project structure, settings, and the initial storage integration.

### Epic 2. Event Collection API

Implement the API endpoint for receiving user activity events. The endpoint should accept event type, user identifier, timestamp, and optional metadata.

### Epic 3. HBase Storage Integration

Implement the code that writes received events to HBase. This epic covers table creation, row key design, and writing records in a format that supports the expected read patterns.

### Epic 4. User Activity History

Implement the endpoint for retrieving the event history of a single user. The result should support filtering by date or date range and return the stored events in a readable form.

### Epic 5. Daily Activity Report

Implement a simple daily report that counts user events by date and event type. The goal is to demonstrate a basic aggregation scenario over HBase data.

### Epic 6. Demo Data and Validation

Prepare sample data for the demo and add simple validation rules for request payloads. This epic also includes example requests that can be used during the presentation.

## Expected Demo Outcome

After completing the minimal project, the application should be able to:

* receive user activity events
* store them in HBase
* return user history for a given period
* show a daily summary of activity

This is enough to demonstrate how HBase can be used for high-volume event storage and simple analytical reads.

## Notes for Students

The project is intentionally small so that the focus stays on the architecture and the data model rather than on UI complexity. The main learning goal is to understand how to design row keys and choose an access pattern that matches HBase strengths.

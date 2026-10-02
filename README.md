# Court Registration & Legal Services Assistant

A conversational AI application for supporting court registration and legal-service workflows through natural-language interaction.

The project is built with **Rasa** and Python, with custom action logic, conversational training data, REST integration, and Telegram support. It was developed as part of an AI-enabled digital service workflow for court-related registration and user assistance.

## Overview

The system uses conversational AI to guide users through structured court-service interactions rather than requiring every step to be completed through traditional forms.

The project includes:

* Natural-language intent recognition
* Rule- and form-based conversational workflows
* Custom Python actions
* Structured domain and training data
* Document and attachment handling workflows
* REST/API integration
* Telegram integration
* Automated conversation tests
* Trained Rasa models

## Technology Stack

* **Python**
* **Rasa**
* **Rasa NLU & Dialogue Management**
* **YAML-based conversational configuration**
* **REST APIs**
* **Telegram Bot Integration**
* **Custom Python Actions**
* **Automated Testing**

## Project Structure

```text
CourtRegistration/
├── actions/          # Custom Rasa actions and business logic
├── data/             # NLU, rules, stories and conversational training data
├── models/           # Trained Rasa models
├── restore/          # Supporting restoration/project resources
├── tests/             # Conversation and application tests
├── config.yml        # Rasa NLU and dialogue configuration
├── domain.yml        # Intents, entities, slots, responses and actions
├── endpoints.yml     # Action server and service endpoints
├── custom_telegram.py # Telegram integration
└── testapi.py        # API testing utilities
```

## Conversational Architecture

The application follows the Rasa conversational AI architecture:

```text
User
  │
  ▼
Conversation Interface
  │
  ├── Telegram
  └── API / REST
  │
  ▼
Rasa NLU
  │
  ├── Intent Recognition
  └── Entity Extraction
  │
  ▼
Dialogue Management
  │
  ├── Rules
  ├── Forms
  └── Conversation Flows
  │
  ▼
Custom Python Actions
  │
  ▼
External Services / Application Logic
```

This approach allows conversational workflows to be represented as structured states and business actions while keeping application-specific logic in Python.

## Custom Actions

The `actions/` module contains the project's custom Rasa action implementations.

These actions handle application-specific operations and conversational workflows that go beyond standard Rasa responses, including interaction with external services and processing information collected during conversations.

## Attachment Workflow

The application also contains a conversational attachment workflow designed to allow users to provide supporting documents or files during relevant interactions.

A typical flow can involve:

1. Asking whether supporting documentation is available
2. Detecting the user's response
3. Activating the appropriate conversational form
4. Collecting the uploaded document
5. Processing the attachment
6. Continuing the registration workflow

## Telegram Integration

The project includes a custom Telegram integration implemented in Python, allowing the conversational assistant to be exposed through a messaging interface.

The integration is handled through:

```text
custom_telegram.py
```

## Testing

The repository includes a dedicated `tests/` directory together with API testing utilities.

Conversation behavior can be tested against the project's intents, rules, forms and custom actions to help validate the dialogue flow.

## Running Locally

Install the project's Python dependencies and Rasa environment, then configure the required endpoints.

Start the Rasa action server:

```bash
rasa run actions
```

Start the Rasa server:

```bash
rasa run
```

For development and training:

```bash
rasa train
```

The action endpoint is configured in `endpoints.yml`.

> The exact runtime configuration depends on the external services and deployment environment used with the application.

## Engineering Focus

This project demonstrates practical application of conversational AI to structured digital-service workflows, including:

* Conversational workflow design
* Natural-language understanding
* Rule- and form-based dialogue management
* Python backend/action development
* API integration
* Messaging-platform integration
* Document-handling workflows
* AI-assisted public-service applications

## Project Status

This repository represents a development implementation of a court-service conversational application.

Some configuration and deployment components depend on external infrastructure and services and are therefore environment-specific.

**Author:** Hanan Temam
**Focus:** AI Software Development · Conversational AI · Data & Intelligent Systems

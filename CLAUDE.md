# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based LLM service integration project (nabu_llm_service) that provides a client interface to interact with the LapaLLM model hosted on a remote server. The project is in early development stages as part of the "lapathon_nabu_track" initiative.

The project processes vehicle registration data from NABU (National Anti-Corruption Bureau) and uses the LapaLLM model for analysis. Data is stored in `nabu_data/` directory with subdirectories for different case types (890-ТМ-Д, 891-ТМ-Д, 995-ІБ-Д), containing request/answer pairs in JSON format.

## Environment Setup

The project uses Python 3.13 with a virtual environment:

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (or use pip freeze for exact versions)
pip install openai httpx pydantic python-dotenv tqdm

# Configure environment variables
cp .env.example .env
# Edit .env and add your API key
```

## Running the Application

```bash
# Run the main script
python main.py
```

The main.py file contains a basic client implementation that connects to a LapaLLM model endpoint and sends chat completion requests with Ukrainian language prompts.

## Architecture

**Project Structure**:
- `main.py` - Single entry point with OpenAI client initialization and chat completion logic
- `nabu_data/` - Vehicle registration data organized by case type:
  - `890-ТМ-Д/`, `891-ТМ-Д/`, `995-ІБ-Д/` - Case-specific directories
  - Each case subdirectory contains `request.json` (API request format) and/or `answer.json` (vehicle registration details)
  - `Опис_полів.xlsx` - Field descriptions for data schema
  - `Профіль-зразок.pdf` - Sample profile document
- `.env` - Environment configuration (git-ignored)
- `.env.example` - Template for required environment variables

**Environment Configuration**:
- `OPENAI_API_KEY` - API key for authentication with LapaLLM service
- `OPENAI_BASE_URL` - Custom endpoint URL (default: http://146.59.127.106:4000)

**LLM Configuration**:
- Model: "lapa"
- Default temperature: 0.7
- Default max_tokens: 1000

**Key Architectural Patterns**:
- Uses OpenAI's client library with custom base URL to connect to LapaLLM, providing API compatibility while using a custom model
- Environment variables loaded via `python-dotenv` for secure credential management
- Data is structured as request/answer pairs for vehicle registration information, containing owner details, vehicle specifications, and operation metadata

## Git Workflow

Current branch: `feat/llm-setup`

The repository follows a feature branch workflow. When making commits, follow the existing commit style (lowercase, concise messages like "init commit").

# Financial QA Bot – Project Report

## Introduction
The Financial QA Bot is a Python application that reads structured CSV financial data and answers natural-language questions about key metrics such as Revenue, Net Income, Operating Expenses, and Total Assets. Its goals are to provide fast, reliable insights from tabular data, support simple business reporting, and optionally augment responses with AI-generated explanations via the OpenRouter platform, while maintaining a robust rule-based fallback.

## Design Decisions
- **Data-first approach:** The bot treats the CSV as the single source of truth. It relies on predictable headers (Year, Revenue, Net_Income, Operating_Expenses, Total_Assets) to keep parsing simple and reliable across datasets.
- **Modular architecture:** Core modules include `DataIndexer` (loading/validation), `Retriever` (fuzzy lookup + value access), `QAChain` (answer generation), and `Visualizer` (charts). The `FinancialQABot` orchestrates these components and handles I/O and reporting.
- **LLM integration via OpenRouter:** When enabled, `QAChain` calls OpenRouter (default model: Mistral `mistralai/devstral-2512:free`) for enhanced phrasing and context. All AI calls use a small, explicit prompt with the tabular context and question. This layer is optional and fully decoupled from data handling.
- **Graceful fallback & minimization of API calls:** If the LLM is disabled, unavailable, or rate-limited, the bot falls back to deterministic rule-based answers. An in-memory cache stores answers per query to avoid repeated LLM calls during a run, and `generate_report` reuses computed results instead of re-querying.
- **Simple, reproducible visuals:** Charts are generated with Matplotlib and saved to output files, favoring clarity and portability over interactive features.

## Implementation Overview
- **Data ingestion:** `DataIndexer` validates the CSV, normalizes column names, and exposes helpers to inspect rows and columns. Historical, realistic sample data (1924–2023) is provided for testing.
- **Query parsing & retrieval:** `QAChain` performs lightweight parsing (metric + optional year) and uses `Retriever` to fetch the corresponding values. Answers are formatted consistently, with currency-style numbers and clear metric names.
- **LLM pathway:** When enabled and not rate-limited, `QAChain` builds a compact prompt including a system role (“financial analyst”), the relevant data context, and the user’s question. Responses are returned as-is, trimmed, and cached. A 429 guard disables LLM calls for the remainder of the run to conserve quota.
- **Batch reporting:** `FinancialQABot.generate_report` executes a list of questions, aggregates results, writes a JSON report, and returns both the data and path. The app reuses these results to avoid duplicate processing. Logging records key events (load, answers, charts, file outputs).
- **Visualization:** `Visualizer` produces line or bar charts for metrics, saved under `output/charts`. Defaults prioritize readability and consistent file naming.

## Challenges Faced
- **API model/quotas:** Early attempts with other providers/models led to 404s or privacy constraints. OpenRouter was adopted for reliability, but free-tier rate limits (429) required runtime resilience: caching, prompt minimization, and an immediate fallback to rule-based answers.
- **Dependency and scope cleanup:** The project initially included Google/Gemini and LangChain references. These were removed to reduce surface area and ensure a single, consistent LLM pathway.
- **Data variability:** Ensuring the bot works with any CSV that matches the expected headers demanded strict assumptions and clear error messaging. Sample data was expanded and made historically realistic to validate behavior across longer time series.

## Conclusion
The Financial QA Bot provides a practical, modular solution for answering questions from financial CSVs, with robust behavior across environments and datasets. Key lessons include keeping AI optional, minimizing external calls through caching and reuse, and favoring simple, dependable interfaces. Potential improvements: configurable prompt templates per question type, richer trend analysis (e.g., CAGR), better error diagnostics for malformed CSVs, and optional persistence of the cache between runs. The current design balances clarity, reliability, and cost-efficiency, making it well-suited for lightweight financial reporting workflows.

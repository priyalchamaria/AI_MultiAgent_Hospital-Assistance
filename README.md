# CareBridge AI: Multi-Agent Hospital Assistant

CareBridge AI is an AI-powered multi-agent application that lets hospital staff ask plain-English questions about synthetic patient records and synthetic hospital policy documents.

It uses:

- **Orchestrator Agent** for query classification and routing.
- **SQL Agent** for structured patient-record analysis.
- **RAG Agent** for policy-document retrieval with source citations.
- **SQL safety layer** to block unsafe database operations.
- **Streamlit UI** for a clean evaluator-friendly demo.

All data and policies are synthetic and used only for academic/internship demonstration.

## Why Streamlit?

For internship submission, Streamlit is the best choice here. It is easy for an evaluator to run, needs no separate frontend/backend setup, shows tables and metrics naturally, and makes the multi-agent workflow visible in one browser page.

## Quick Start

```powershell
cd C:\Users\Priyal\Desktop\DS_intern
pip install -r requirements.txt
python scripts\prepare_data.py --archive "C:\Users\Priyal\Downloads_new\archive (1).zip"
python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Project Structure

```text
DS_intern/
├── app.py
├── requirements.txt
├── README.md
├── .env
├── data/
│   ├── healthcare_dataset.csv
│   ├── hospital.db
│   ├── policy_index.pkl
│   └── policies/
├── agents/
│   ├── orchestrator_agent.py
│   ├── sql_agent.py
│   └── rag_agent.py
├── database/
│   ├── create_database.py
│   ├── schema.py
│   └── db_utils.py
├── rag/
│   ├── document_loader.py
│   ├── chunker.py
│   ├── embeddings.py
│   └── vector_store.py
├── services/
│   ├── query_classifier.py
│   ├── sql_validator.py
│   ├── response_formatter.py
│   └── logger.py
├── frontend/
│   └── ui.py
├── tests/
└── evaluation/
```

## Architecture

```text
User Query
    |
    v
Orchestrator Agent
    |
    +--> SQL Agent --> SQL Validator --> SQLite patients table --> formatted answer
    |
    +--> RAG Agent --> document loader --> chunker --> vector store --> cited policy answer
    |
    +--> Both Agents for mixed questions
    |
    +--> Unsupported response for out-of-scope questions
    |
    v
Unified Response + Query Log + Evaluation Metrics
```

## Features

- CSV-to-SQLite conversion
- Data cleaning, date conversion, duplicate removal, missing-value checks
- Patient ID generation
- SQLite indexes on condition, doctor, hospital, admission date, admission type, and test results
- 10 synthetic hospital policy documents
- Hybrid query classifier: keyword rules plus semantic similarity
- SQL, RAG, both-agent, and unsupported routes
- Read-only SQL validation
- Maximum returned rows
- Empty-result and database-error handling
- Limited conversational memory for follow-up questions
- Query logs in `logs/query_logs.json`
- Automated tests
- Evaluation metrics
- Streamlit tabs for chat, database explorer, policy documents, metrics, evaluation, and project overview

## Example Questions

SQL Agent:

- How many female patients have diabetes?
- What is the average billing amount by insurance provider?
- Show the top 5 hospitals with the most cancer patients.
- List patients with abnormal test results.

RAG Agent:

- What is the visitor policy?
- When should privacy incidents be reported?
- What is the medication administration policy?
- What is the emergency response procedure?

Both Agents:

- How many diabetic patients are there and what is the discharge policy?

Unsupported:

- What is the weather today?
- DROP TABLE patients

## Tests

```powershell
pytest
```

## Evaluation

```powershell
python evaluation\evaluate_system.py
```

The evaluation writes:

```text
evaluation/results.json
```

Metrics include routing accuracy, end-to-end success rate, unsafe-query blocking, average latency, agent usage distribution, and confusion rows.

## Important Safety Note

This project is not a medical device and should not be used for real clinical decisions. It uses synthetic data and synthetic policy documents for academic demonstration only.

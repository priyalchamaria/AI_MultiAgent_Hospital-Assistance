# CareBridge AI: Multi-Agent Hospital Assistant

CareBridge AI is an AI-powered multi-agent application that lets hospital staff ask plain-English questions about synthetic patient records and synthetic hospital policy documents.

The system demonstrates a practical multi-agent workflow where an Orchestrator Agent routes each query to the correct specialist:

- **SQL Agent** for structured patient-record questions.
- **RAG Agent** for hospital policy-document questions.
- **Both Agents** for mixed questions involving data and policy.
- **Unsupported route** for out-of-scope or unsafe questions.

All data and policies are synthetic and used only for academic/internship demonstration.

## Implementation Notes

- The SQL Agent is a **rule-based, schema-aware NLP-to-SQL agent** with controlled SQL generation for supported query patterns.
- The RAG Agent is a **lightweight local RAG pipeline** using TF-IDF retrieval and grounded extractive answer generation.
- The project does not require OpenAI API keys, external LLM services, or cloud-hosted vector databases.

## Key Features

- Streamlit-based professional dashboard
- Synthetic healthcare CSV converted into SQLite
- Data cleaning, date conversion, duplicate removal, missing-value checks
- Patient ID generation and database indexing
- Controlled NLP-to-SQL query generation with read-only SQL validation
- RAG pipeline over 10 synthetic hospital policy documents
- Orchestrator Agent with SQL, RAG, both-agent, and unsupported routes
- Source citations for policy answers
- Role-based access control demo for patient-table columns
- Feedback buttons for each answer
- Query logs and validation metrics
- Automated tests for agents and SQL safety
- GitHub Actions workflow for automated test execution

## Tech Stack

- Python
- Streamlit
- SQLite
- Pandas
- Scikit-learn
- Pytest for automated testing

## Project Structure

```text
AI_MultiAgent_Hospital-Assistance/
|-- app.py
|-- requirements.txt
|-- requirements-dev.txt
|-- README.md
|-- data/
|   |-- healthcare_dataset.csv
|   |-- hospital.db
|   |-- policy_index.pkl
|   `-- policies/
|-- agents/
|   |-- orchestrator_agent.py
|   |-- sql_agent.py
|   `-- rag_agent.py
|-- database/
|   |-- create_database.py
|   |-- schema.py
|   `-- db_utils.py
|-- rag/
|   |-- document_loader.py
|   |-- chunker.py
|   |-- embeddings.py
|   `-- vector_store.py
|-- services/
|   |-- query_classifier.py
|   |-- sql_validator.py
|   |-- response_formatter.py
|   `-- logger.py
|-- frontend/
|   `-- ui.py
|-- tests/
|-- evaluation/
`-- docs/
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
Unified Response + Query Log + Feedback + Validation Metrics
```

## How to Run Locally

1. Clone the repository:

```powershell
git clone https://github.com/priyalchamaria/AI_MultiAgent_Hospital-Assistance.git
cd AI_MultiAgent_Hospital-Assistance
```

2. Install runtime dependencies:

```powershell
pip install -r requirements.txt
```

3. Start the app:

```powershell
python -m streamlit run app.py
```

4. Open the browser:

```text
http://localhost:8501
```

## Optional: Rebuild the Data

The repository already includes the prepared dataset, SQLite database, policy documents, and policy index. Evaluators do not need to run this step for normal use.

If you want to rebuild the database and RAG index from the CSV included in this repository, run:

```powershell
python scripts/prepare_data.py --csv data/healthcare_dataset.csv
```

## Demo Questions

SQL Agent:

- How many female patients have diabetes?
- What is the average billing amount by insurance provider?
- Show the top 5 hospitals with the most cancer patients.
- List patients with abnormal test results.

RAG Agent:

- What is the visitor policy?
- What are the visiting hours?
- When should privacy incidents be reported?
- What is the medication administration policy?

Both Agents:

- How many diabetic patients are there and what is the discharge policy?

Unsupported:

- What is the weather today?
- DROP TABLE patients

## Testing

Install development dependencies and run the automated test suite:

```powershell
pip install -r requirements-dev.txt
python -m pytest
```

## Evaluation

Run the evaluation script:

```powershell
python evaluation/evaluate_system.py
```

The evaluation writes:

```text
evaluation/results.json
```

Metrics include routing accuracy, end-to-end success rate, unsafe-query blocking, average latency, agent usage distribution, and confusion rows.

## Important Safety Note

This project is not a medical device and should not be used for real clinical decisions. It uses synthetic data and synthetic policy documents for academic demonstration only.

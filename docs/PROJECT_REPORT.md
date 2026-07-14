# CareBridge AI: AI-Powered Multi-Agent Hospital Knowledge Assistant

## 1. Abstract

CareBridge AI is an AI-powered multi-agent application that allows hospital staff to query synthetic patient records and generated hospital policy documents using plain English. The application uses an Orchestrator Agent to classify every incoming query and route it to the SQL Agent, RAG Agent, both agents for mixed questions, or an unsupported-query response. The project demonstrates how structured and unstructured hospital knowledge can be made accessible through one conversational interface.

## 2. Problem Statement

Hospital staff often need information from two very different knowledge sources:

- Structured data such as admissions, billing values, test results, diagnoses, and insurance providers.
- Unstructured documents such as privacy policies, discharge procedures, escalation rules, and medication reconciliation guidance.

Traditional systems force staff to search databases and document repositories separately. CareBridge AI addresses this gap by using a multi-agent architecture that automatically selects the correct retrieval strategy for each question.

## 3. Objectives

- Build a conversational interface for hospital knowledge access.
- Convert natural-language analytical questions into safe SQL queries.
- Retrieve relevant policy passages using a local RAG pipeline.
- Demonstrate transparent orchestration between specialized agents.
- Use synthetic healthcare data only, avoiding real patient information.

## 4. Dataset

The structured data comes from a synthetic healthcare dataset containing patient admission records. The project normalizes the dataset into a SQLite database with fields such as age, gender, blood type, medical condition, admission date, doctor, hospital, insurance provider, billing amount, room number, admission type, discharge date, medication, and test result.

The unstructured data is a generated set of hospital policy documents covering privacy, discharge planning, medication reconciliation, abnormal test escalation, infection control, and billing documentation.

## 5. System Architecture

### Orchestrator Agent

The Orchestrator Agent inspects the incoming query and assigns it to one of four routes:

- `SQL`: for aggregation, counting, ranking, filtering, and patient-record analysis.
- `RAG`: for policies, procedures, compliance, documentation, escalation, and operational guidance.
- `BOTH`: for mixed questions that need both patient data and policy guidance.
- `UNSUPPORTED`: for out-of-scope or unsafe questions.

The agent returns the route, confidence score, and a short reason. This makes the system explainable during demonstration.

### NLP-to-SQL Agent

The SQL agent converts common analytical patterns into SQLite queries. It supports:

- Counts of matching records.
- Average and total billing.
- Average age and length of stay.
- Grouped breakdowns by hospital, insurance provider, medical condition, admission type, gender, blood type, medication, test result, or doctor.
- Filters for admission type, test result, common conditions, and admission year.

The generated SQL is shown in the interface for transparency.

### RAG Agent

The RAG agent loads local policy documents, splits them into chunks, creates local TF-IDF vectors, and retrieves the most similar chunks for a question. It returns a concise extractive answer and source citations.

## 6. Technology Stack

- Python
- Streamlit
- SQLite
- Pandas
- Scikit-learn TF-IDF retrieval
- Pytest

## 7. Workflow

1. Prepare the dataset using `scripts/prepare_data.py`.
2. Load patient records into SQLite.
3. Generate synthetic policy documents.
4. Start the Streamlit app.
5. Ask a plain-English question.
6. Orchestrator classifies the question.
7. SQL Agent or RAG Agent produces the final answer.

## 8. Example Outputs

Question: “How many emergency admissions were there?”

Expected route: SQL.

Output: A count generated from the patient database, with the SQL query visible.

Question: “What is the discharge planning policy?”

Expected route: RAG.

Output: A summary retrieved from the discharge planning policy document with citation.

## 9. Strengths

- Uses a clear multi-agent design.
- Works locally without external API keys.
- Separates structured and unstructured reasoning.
- Provides explainable routing and visible SQL.
- Uses synthetic data suitable for academic submission.

## 10. Limitations and Future Scope

- The NLP-to-SQL component is rule-guided and supports a controlled set of analytical patterns.
- The offline RAG pipeline uses TF-IDF vectors so evaluators can run the system without downloading large model weights.
- Future work could add an LLM for richer SQL generation and answer synthesis, FAISS or ChromaDB for larger indexes, stronger role-based access control, user authentication, and more advanced evaluation metrics.

## 11. Conclusion

CareBridge AI demonstrates a realistic multi-agent hospital assistant where a single natural-language interface can access both patient database records and policy documents. The project highlights the value of orchestration, specialization, transparency, and retrieval-augmented design in healthcare information systems.

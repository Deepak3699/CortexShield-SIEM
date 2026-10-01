# LogSentinel --- Detailed Project Development Plan

## 1. Project Overview

**Project Name:** LogSentinel\
**Project Type:** AI-powered web/server log analysis and security
monitoring platform\
**Primary Language:** Python\
**Initial Interface:** Streamlit dashboard\
**ML Approach:** Unsupervised anomaly detection\
**AI Approach:** LLM-assisted unknown log format understanding and
parser configuration generation

### Core Objective

Build a system that can accept different web/server log files,
automatically understand their structure, normalize them into a common
schema, perform traffic analytics, detect security threats using
deterministic rules, identify unusual behaviour using machine learning,
calculate an overall risk score, and present the results through a
dashboard.

### Core Pipeline

``` text
Log File
   ↓
File Ingestion
   ↓
Sampling
   ↓
Format Detection
   ↓
Known Format ────────────────┐
   ↓                         │
Known Parser                 │
                             │
Unknown Format               │
   ↓                         │
LLM-Assisted Format Analysis │
   ↓                         │
Parser Configuration         │
   ↓                         │
Configuration Validation ────┘
   ↓
Generic / Format Parser
   ↓
Normalization
   ↓
Normalized Events
   ├── Analytics
   ├── Security Rules
   └── ML Feature Engineering
             ↓
       Anomaly Detection
             ↓
       Risk Scoring
             ↓
          Dashboard
             ↓
      Alerts / Actions
```

------------------------------------------------------------------------

# 2. Problem Statement

Web and application servers generate large volumes of logs. These logs
are useful for:

-   understanding website traffic
-   troubleshooting errors
-   identifying abusive clients
-   detecting brute-force attacks
-   identifying suspicious scanning
-   finding unusual traffic patterns
-   monitoring server behaviour

The problem is that log formats vary significantly between systems.

Examples include:

-   Apache access logs
-   Nginx access logs
-   IIS/W3C logs
-   JSON logs
-   JSONL logs
-   CSV-like logs
-   custom application logs

A traditional parser usually requires a developer to manually write a
parser for every format.

LogSentinel will reduce this dependency by combining:

1.  deterministic format detection
2.  predefined parsers
3.  LLM-assisted parsing for unknown formats
4.  strict Python validation
5.  a universal normalized schema
6.  security rules
7.  machine-learning anomaly detection
8.  explainable risk scoring

------------------------------------------------------------------------

# 3. Project Goals

## Primary Goals

-   Accept multiple log formats.
-   Detect known formats automatically.
-   Use an LLM only when the format is unknown or ambiguous.
-   Generate a parser configuration from a small sample.
-   Validate AI-generated configurations before processing the full
    file.
-   Parse large files using streaming/chunked processing.
-   Normalize different formats into a common event structure.
-   Calculate traffic and endpoint analytics.
-   Detect common security patterns.
-   Generate ML-based anomaly scores.
-   Combine rule-based and ML signals into a risk score.
-   Display results through a usable dashboard.
-   Keep the architecture modular so components can be replaced later.

## Secondary Goals

-   Store analysis results for later inspection.
-   Allow comparison between uploaded log files.
-   Support reusable parser configurations.
-   Provide human-readable explanations for suspicious events.
-   Eventually support live log streams.

## Non-Goals for Version 1

-   Fully autonomous firewall control.
-   Training a large language model from scratch.
-   Building a custom deep-learning model before a baseline ML system
    exists.
-   Processing an entire log file through an LLM.
-   Guaranteeing that every anomaly is a real attack.
-   Replacing a production SIEM/WAF.

------------------------------------------------------------------------

# 4. Product Requirements

## 4.1 Input

The system should accept:

``` text
.log
.txt
.json
.jsonl
.csv
```

Initial version can prioritize:

1.  Apache Combined Log
2.  Nginx access log
3.  JSON/JSONL
4.  Custom delimiter-based logs

## 4.2 User Workflow

``` text
User opens dashboard
      ↓
Uploads log file
      ↓
System reads metadata
      ↓
System creates representative sample
      ↓
Format detector runs
      ↓
Known format?
   /        \
 Yes        No
  ↓          ↓
Parser     LLM Assist
  ↓          ↓
  └────┬─────┘
       ↓
Validation
       ↓
Parse full file
       ↓
Normalize
       ↓
Analyze
       ↓
Detect threats
       ↓
Run ML
       ↓
Calculate risk
       ↓
Display dashboard
```

------------------------------------------------------------------------

# 5. Functional Requirements

## FR-01: File Upload

The application must allow a user to upload a supported log file.

## FR-02: File Sampling

The application must extract a representative sample without loading
unnecessarily large files entirely into memory.

## FR-03: Format Detection

The system must determine whether the file matches a known format.

## FR-04: AI-Assisted Unknown Format Detection

For unknown formats, the system must send only a controlled sample to
the LLM and request a structured parser configuration.

## FR-05: AI Configuration Validation

The system must validate the generated configuration against additional
log samples.

## FR-06: Full Parsing

After validation, the system must process the full file.

## FR-07: Normalization

All supported log formats must map to a common normalized event schema.

## FR-08: Analytics

The system must calculate traffic, endpoint, status-code, method,
user-agent, IP, and time-based statistics.

## FR-09: Security Detection

The system must detect configurable suspicious patterns.

## FR-10: ML Anomaly Detection

The system must calculate anomaly scores from engineered behavioural
features.

## FR-11: Risk Scoring

The system must combine security-rule signals and ML signals into a
final risk score.

## FR-12: Dashboard

The system must display analysis results through an interactive
dashboard.

## FR-13: Explainability

Suspicious events should include understandable reasons rather than only
a numeric score.

------------------------------------------------------------------------

# 6. Non-Functional Requirements

## Performance

-   Avoid loading huge files completely into RAM.
-   Use streaming/chunk processing where possible.
-   Process analytics efficiently with Pandas or database aggregation.
-   Avoid unnecessary LLM calls.

## Reliability

-   Validate AI-generated parser configurations.
-   Handle malformed lines without crashing the complete analysis.
-   Record parsing failures.
-   Keep raw input separate from processed data.

## Security

-   Do not send entire logs to an external LLM.
-   Minimize sensitive information sent to external APIs.
-   Store API keys in environment variables.
-   Never hard-code API keys.
-   Treat uploaded logs as untrusted input.
-   Avoid executing AI-generated code.
-   AI should generate configuration/data, not executable parser code.

## Explainability

The user should be able to understand:

``` text
Why was this IP suspicious?
Why was this request anomalous?
Which rule triggered?
What contributed to the risk score?
```

## Maintainability

Each major component should have a clear responsibility and independent
tests.

------------------------------------------------------------------------

# 7. System Architecture

``` text
                    ┌───────────────────────┐
                    │     Streamlit UI      │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    Application Layer  │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
       ┌────────────┐    ┌─────────────┐   ┌────────────┐
       │ Ingestion  │    │ Detection   │   │ AI Assist  │
       └─────┬──────┘    └──────┬──────┘   └─────┬──────┘
             │                  │                │
             └──────────────────┼────────────────┘
                                ▼
                       ┌────────────────┐
                       │    Parsing     │
                       └───────┬────────┘
                               ▼
                       ┌────────────────┐
                       │ Normalization  │
                       └───────┬────────┘
                               ▼
                     ┌────────────────────┐
                     │ Normalized Events  │
                     └─────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
          ┌──────────┐  ┌───────────┐  ┌──────────┐
          │Analytics │  │ Security  │  │   ML     │
          └────┬─────┘  └─────┬─────┘  └────┬─────┘
               │              │              │
               └──────────────┼──────────────┘
                              ▼
                       ┌──────────────┐
                       │ Risk Engine  │
                       └──────┬───────┘
                              ▼
                       ┌──────────────┐
                       │   Results    │
                       └──────┬───────┘
                              ▼
                       ┌──────────────┐
                       │  Dashboard   │
                       └──────────────┘
```

------------------------------------------------------------------------

# 8. Directory Structure

``` text
LogSentinel/
│
├── app/
│   ├── main.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── file_reader.py
│   │   └── sampler.py
│   │
│   ├── detection/
│   │   ├── __init__.py
│   │   ├── format_detector.py
│   │   ├── format_registry.py
│   │   └── validator.py
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── ai_assistant.py
│   │   ├── prompt_builder.py
│   │   └── config_generator.py
│   │
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base_parser.py
│   │   ├── apache_parser.py
│   │   ├── nginx_parser.py
│   │   ├── json_parser.py
│   │   └── generic_parser.py
│   │
│   ├── normalization/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   └── normalizer.py
│   │
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── traffic.py
│   │   ├── endpoints.py
│   │   ├── users.py
│   │   └── statistics.py
│   │
│   ├── security/
│   │   ├── __init__.py
│   │   ├── rules.py
│   │   ├── sql_detection.py
│   │   ├── brute_force.py
│   │   ├── scanning.py
│   │   ├── bot_detection.py
│   │   └── risk_score.py
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── feature_engineering.py
│   │   ├── anomaly_detector.py
│   │   ├── train.py
│   │   └── predict.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   │
│   └── dashboard/
│       ├── __init__.py
│       ├── overview.py
│       ├── analytics.py
│       ├── security.py
│       ├── anomalies.py
│       └── logs.py
│
├── data/
│   ├── raw/
│   ├── samples/
│   ├── processed/
│   └── features/
│
├── models/
│
├── configs/
│   ├── parser_configs/
│   └── security_rules/
│
├── tests/
│
├── notebooks/
│
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── run.py
```

------------------------------------------------------------------------

# 9. Canonical Normalized Schema

Every parser should eventually produce the same structure.

``` json
{
  "timestamp": "2026-08-20T10:30:21+05:30",
  "ip": "192.168.1.10",
  "method": "POST",
  "url": "/login",
  "protocol": "HTTP/1.1",
  "status": 401,
  "response_size": 1200,
  "referer": null,
  "user_agent": "Mozilla/5.0",
  "host": null,
  "raw_line": "original log line"
}
```

## Required Fields

-   timestamp
-   IP
-   method
-   URL
-   status

## Optional Fields

-   protocol
-   response_size
-   referer
-   user_agent
-   host
-   raw_line
-   query_string
-   response_time
-   username/session identifier if safely available

------------------------------------------------------------------------

# 10. Phase 1 --- Project Setup

## Objective

Create the project skeleton and development environment.

## Tasks

-   [ ] Create project directory.
-   [ ] Create virtual environment.
-   [ ] Create directory structure.
-   [ ] Create `requirements.txt`.
-   [ ] Create `.env.example`.
-   [ ] Create `.gitignore`.
-   [ ] Initialize Git repository.
-   [ ] Create basic README.
-   [ ] Verify Python environment.
-   [ ] Create a minimal Streamlit application.

## Initial Dependencies

``` text
pandas
numpy
scikit-learn
streamlit
plotly
python-dotenv
pydantic
joblib
```

Add an LLM SDK only when Phase 3 begins.

## Completion Criteria

The application should launch with:

``` bash
streamlit run app/main.py
```

------------------------------------------------------------------------

# 11. Phase 2 --- File Ingestion and Sampling

## Objective

Safely read log files and create useful samples.

## Components

### `file_reader.py`

Responsibilities:

-   verify file existence
-   detect extension
-   calculate file size
-   read lines
-   handle encoding
-   report malformed input

### `sampler.py`

Responsibilities:

-   first-N sample
-   middle sample
-   random sample
-   representative sample

## Sample Strategy

For a large file:

``` text
First 50 lines
+
Random 100 lines
+
Last 50 lines
```

This gives the detector a better view of the file than using only the
beginning.

## Completion Criteria

Given a large log file, the system can generate:

``` text
sample
file_size
line_count estimate
encoding
```

without loading the entire file into memory.

------------------------------------------------------------------------

# 12. Phase 3 --- Format Detection

## Objective

Determine whether the file matches a supported format.

## Detection Order

``` text
JSON/JSONL?
   ↓
Apache?
   ↓
Nginx?
   ↓
IIS/W3C?
   ↓
CSV/delimiter?
   ↓
Custom?
   ↓
Unknown
```

## Output

The detector should return structured data such as:

``` json
{
  "format": "apache_combined",
  "confidence": 0.98,
  "parser": "apache_parser"
}
```

For unknown:

``` json
{
  "format": "unknown",
  "confidence": 0.21,
  "parser": null
}
```

## Important Design Rule

Do not make the detector return only a string.

It should return metadata that can be logged, tested, and displayed.

------------------------------------------------------------------------

# 13. Phase 4 --- AI-Assisted Unknown Format Detection

## Objective

Use an LLM to understand unknown formats without sending the full file.

## Input to LLM

Provide:

-   small sample
-   supported canonical fields
-   parser configuration schema
-   strict instructions
-   examples if necessary

## Expected Output

``` json
{
  "format_name": "custom_pipe_log",
  "delimiter": "|",
  "fields": {
    "timestamp": 0,
    "ip": 1,
    "method": 2,
    "url": 3,
    "status": 4,
    "user_agent": 5
  },
  "timestamp_format": "%d-%m-%Y %H:%M:%S"
}
```

## Critical Security Rule

The LLM must **not** be allowed to return executable Python code.

Allowed:

``` text
configuration
field mappings
regular expressions
format metadata
```

Not allowed:

``` text
Python source code to execute
shell commands
database commands
```

------------------------------------------------------------------------

# 14. Phase 5 --- Parser Configuration Validation

## Objective

Prove that the AI-generated configuration actually works.

## Validation Pipeline

``` text
AI Configuration
       ↓
Parse 100–500 unseen lines
       ↓
Validate fields
       ↓
Calculate success rate
       ↓
Accept / Reject
```

## Validation Metrics

Example:

``` text
Timestamp success: 97%
IP success: 100%
Method success: 99%
URL success: 100%
Status success: 100%
Overall: 99.2%
```

Set a configurable minimum threshold.

Example:

``` text
>= 95% → Accept
< 95%  → Reject
```

The threshold should be configurable rather than hard-coded permanently.

------------------------------------------------------------------------

# 15. Phase 6 --- Parsing Engine

## Objective

Parse the entire log efficiently.

## Architecture

``` text
BaseParser
   │
   ├── ApacheParser
   ├── NginxParser
   ├── JSONParser
   └── GenericParser
```

Each parser should expose a consistent interface.

Example conceptual interface:

``` text
parse_line(line)
parse_file(file)
```

## Requirements

-   Process line by line where practical.
-   Handle malformed lines.
-   Count parse failures.
-   Preserve useful raw data.
-   Produce normalized-compatible records.

------------------------------------------------------------------------

# 16. Phase 7 --- Normalization

## Objective

Convert parser output into the canonical schema.

Example:

``` text
Apache
Nginx
JSON
Custom
   ↓
Normalizer
   ↓
Normalized Event
```

## Validation

Check:

-   timestamp format
-   IP validity
-   HTTP method
-   status code
-   URL type
-   numeric fields

Invalid values should be represented consistently, preferably as
null/missing values rather than silently converted into incorrect
values.

------------------------------------------------------------------------

# 17. Phase 8 --- Analytics Engine

## Objective

Generate descriptive statistics.

## Traffic Metrics

-   total requests
-   requests per minute
-   requests per hour
-   requests per day
-   average requests per time period
-   peak traffic time

## Endpoint Metrics

-   top URLs
-   least-used URLs
-   endpoint error rate
-   request method distribution

## Status Metrics

-   2xx count
-   3xx count
-   4xx count
-   5xx count
-   status distribution

## Client Metrics

-   top IPs
-   unique IP count
-   top user agents
-   bot-like user agents

## Error Metrics

-   404 rate
-   401 rate
-   403 rate
-   500 rate

------------------------------------------------------------------------

# 18. Phase 9 --- Security Detection Rules

## Objective

Detect known suspicious patterns.

## Rule Categories

### Brute Force

Indicators:

-   high login attempt frequency
-   repeated 401/403 responses
-   high failure-to-success ratio

### Scanning

Indicators:

-   many unique endpoints
-   requests to administrative paths
-   requests to common sensitive files
-   high 404 frequency

### SQL Injection Patterns

Look for suspicious request patterns such as:

``` text
union select
or 1=1
select from
information_schema
```

These are indicators, not proof of an attack.

### Path Traversal

Patterns such as encoded or plain traversal attempts should be detected
carefully.

### Bot / Automation Behaviour

Indicators:

-   unusually high request rate
-   repeated identical request patterns
-   abnormal endpoint sequence
-   suspicious or missing user-agent behaviour

------------------------------------------------------------------------

# 19. Phase 10 --- Feature Engineering for ML

## Objective

Convert raw events into behavioural features.

The unit of analysis should initially be:

``` text
IP + time window
```

Example:

``` text
192.168.1.10
2026-08-20 10:00–10:05
```

## Features

``` text
request_count
requests_per_second
unique_urls
unique_methods
GET_count
POST_count
PUT_count
DELETE_count
status_2xx_count
status_4xx_count
status_5xx_count
status_401_count
status_403_count
status_404_count
failed_login_count
average_request_interval
url_entropy
unique_user_agents
```

Start with a small reliable feature set before adding advanced features.

------------------------------------------------------------------------

# 20. Phase 11 --- ML Anomaly Detection

## First Model

Use:

``` text
Isolation Forest
```

## Process

``` text
Normalized Events
       ↓
Feature Engineering
       ↓
Feature Matrix
       ↓
Isolation Forest
       ↓
Anomaly Prediction
       ↓
Anomaly Score
```

## Output

Each behavioural window should receive:

``` json
{
  "ip": "192.168.1.10",
  "window": "10:00-10:05",
  "is_anomaly": true,
  "anomaly_score": 0.87
}
```

The score should be normalized into a user-friendly range before being
shown in the dashboard.

------------------------------------------------------------------------

# 21. Phase 12 --- Risk Engine

## Objective

Combine multiple signals.

Potential inputs:

``` text
rule_score
ml_score
request_rate_score
failed_auth_score
scanning_score
error_rate_score
```

## Example

``` text
Rule Score       35
ML Score         25
Brute Force      20
Scanning         10
Error Rate        5
-------------------
Total             95
```

## Risk Levels

``` text
0–29     LOW
30–59    MEDIUM
60–79    HIGH
80–100   CRITICAL
```

These thresholds should be configurable.

## Explainability

For each high-risk entity:

``` text
Risk: HIGH

Reasons:
- 420 requests in 5 minutes
- 38 failed authentication attempts
- 112 unique URLs
- 404 rate significantly above baseline
- ML model classified behaviour as anomalous
```

------------------------------------------------------------------------

# 22. Phase 13 --- Database

## Version 1

Use SQLite.

Suggested entities:

### Analysis

``` text
id
filename
created_at
format
total_lines
parsed_lines
failed_lines
status
```

### Normalized Event

``` text
id
analysis_id
timestamp
ip
method
url
status
user_agent
response_size
```

### Security Finding

``` text
id
analysis_id
ip
timestamp
rule
severity
description
evidence
```

### ML Finding

``` text
id
analysis_id
ip
window_start
window_end
anomaly_score
is_anomaly
```

### Risk Finding

``` text
id
analysis_id
ip
risk_score
risk_level
reasons
```

For very large production workloads, move to PostgreSQL later.

------------------------------------------------------------------------

# 23. Phase 14 --- Dashboard

## Page 1: Overview

Show:

-   total requests
-   unique IPs
-   error rate
-   anomalies
-   high-risk IPs
-   peak traffic time

## Page 2: Traffic Analytics

Charts:

-   requests over time
-   status-code distribution
-   method distribution
-   top URLs
-   top IPs

## Page 3: Security

Show:

-   critical threats
-   high-risk IPs
-   security rule triggers
-   suspicious URLs
-   attack-type distribution

## Page 4: ML Anomalies

Show:

-   anomaly timeline
-   anomaly score distribution
-   anomalous IPs
-   feature contribution/explanation where feasible

## Page 5: Raw Logs

Features:

-   search by IP
-   search by URL
-   filter status
-   filter method
-   time range
-   suspicious-only view

## Page 6: Parser Information

Show:

``` text
Detected Format
Confidence
Parser Used
AI Assistance Used?
Validation Score
Malformed Lines
```

This is particularly valuable because the AI-assisted parser is one of
the project's unique features.

------------------------------------------------------------------------

# 24. Phase 15 --- Testing

Testing is mandatory.

## Unit Tests

Test:

-   file reading
-   sampling
-   format detection
-   each parser
-   normalization
-   validation
-   security rules
-   feature engineering
-   risk scoring

## Test Data

Create small fixtures:

``` text
tests/fixtures/
├── apache.log
├── nginx.log
├── json.log
├── custom.log
├── malformed.log
└── suspicious.log
```

## Security Tests

Test examples for:

-   brute force
-   scanning
-   SQL injection indicators
-   path traversal indicators
-   abnormal request rates

## ML Tests

Test:

-   feature generation
-   missing values
-   model training
-   prediction
-   score conversion

------------------------------------------------------------------------

# 25. Phase 16 --- Evaluation

The system should be measured instead of judged only by whether the UI
looks good.

## Parser Metrics

``` text
Format detection accuracy
Parser success rate
Field extraction accuracy
Malformed line rate
```

## Security Metrics

Where labeled test data exists:

``` text
Precision
Recall
F1-score
False positive rate
False negative rate
```

## ML Metrics

For unsupervised anomaly detection:

-   anomaly stability
-   false-positive investigation rate
-   precision on a manually labeled evaluation set
-   score distribution
-   detection consistency

------------------------------------------------------------------------

# 26. Phase 17 --- Documentation

Create:

``` text
README.md
ARCHITECTURE.md
PRD.md
API.md
DATA_SCHEMA.md
ML.md
SECURITY.md
TESTING.md
DEPLOYMENT.md
```

Documentation should explain both:

``` text
What the system does
```

and:

``` text
Why the system was designed this way
```

------------------------------------------------------------------------

# 27. Phase 18 --- Deployment

## Initial Deployment

``` text
Streamlit
+
SQLite
+
Cloud deployment
```

## Later Production Architecture

``` text
Frontend
   ↓
FastAPI
   ↓
Task Queue
   ↓
Log Processing Workers
   ↓
PostgreSQL
   ↓
ML Service
   ↓
LLM Service
   ↓
Dashboard
```

Possible infrastructure:

``` text
Docker
PostgreSQL
Redis
FastAPI
Streamlit
Cloud hosting
```

------------------------------------------------------------------------

# 28. AI/LLM Design

The LLM should be treated as a specialized assistant, not as the main
processing engine.

## LLM Responsibilities

### Allowed

-   understand unknown log structure
-   suggest field mappings
-   suggest delimiters
-   suggest timestamp formats
-   explain suspicious patterns
-   summarize analysis findings

### Not Allowed

-   execute generated code
-   receive entire huge log files unnecessarily
-   directly decide to block an IP
-   bypass Python validation
-   modify system configuration without validation

------------------------------------------------------------------------

# 29. AI Parser Retry Strategy

If the first configuration fails:

``` text
Sample
 ↓
LLM Attempt 1
 ↓
Validation
 ↓
FAIL
 ↓
LLM Attempt 2
 ↓
Validation
 ↓
FAIL
 ↓
Manual configuration / unsupported format
```

Set a maximum number of attempts.

Example:

``` text
Maximum: 2–3 attempts
```

Do not create an infinite AI retry loop.

------------------------------------------------------------------------

# 30. Risk Architecture

The system should distinguish between:

``` text
Observation
Detection
Anomaly
Risk
Action
```

These are different concepts.

Example:

``` text
Observation:
IP made 500 requests.

Detection:
Request rate rule triggered.

Anomaly:
ML model found the behaviour unusual.

Risk:
Combined score = 87.

Action:
Show CRITICAL alert.
```

This separation will make the architecture much cleaner.

------------------------------------------------------------------------

# 31. Data Flow Example

Suppose the uploaded log contains:

``` text
10.0.0.5 - - [20/Aug/2026:10:10:01 +0530] "POST /login HTTP/1.1" 401 512
10.0.0.5 - - [20/Aug/2026:10:10:02 +0530] "POST /login HTTP/1.1" 401 512
10.0.0.5 - - [20/Aug/2026:10:10:03 +0530] "POST /login HTTP/1.1" 401 512
```

### Step 1

Format detector:

``` text
Apache Combined/Common-like
```

### Step 2

Parser:

``` text
timestamp
ip
method
url
status
response_size
```

### Step 3

Normalizer:

``` json
{
  "ip": "10.0.0.5",
  "method": "POST",
  "url": "/login",
  "status": 401
}
```

### Step 4

Security rule:

``` text
Repeated authentication failures
```

### Step 5

Feature engineering:

``` text
failed_login_count = 3
POST_count = 3
request_count = 3
```

### Step 6

ML:

``` text
possibly normal
```

The ML model does not have to agree with the security rule.

### Step 7

Risk engine:

``` text
Rule signal + ML signal + behaviour
```

### Step 8

Dashboard:

``` text
HIGH RISK

IP: 10.0.0.5

Reason:
Repeated failed authentication attempts.
```

------------------------------------------------------------------------

# 32. Important Architecture Principle

Do **not** build the project like this:

``` text
Log
 ↓
LLM
 ↓
Everything
```

Build it like this:

``` text
Log
 ↓
Python
 ↓
Known?
 ├── Yes → Parser
 └── No → LLM → Config → Validation → Parser
 ↓
Python
 ↓
Analytics + Security + ML
 ↓
Dashboard
```

This will make the system:

-   cheaper
-   faster
-   more deterministic
-   easier to debug
-   safer
-   easier to scale

------------------------------------------------------------------------

# 33. MVP Definition

The first working MVP should contain only:

``` text
1. File upload
2. Sample collection
3. Apache/Nginx/JSON detection
4. At least 2 deterministic parsers
5. Unknown-format AI assistance
6. AI configuration validation
7. Normalized schema
8. Basic analytics
9. Brute-force detection
10. Scanning detection
11. Isolation Forest
12. Risk score
13. Streamlit dashboard
```

Do not add:

``` text
Docker
Redis
PostgreSQL
FastAPI
Auto-blocking
Deep learning
Multi-agent systems
```

until the MVP works.

------------------------------------------------------------------------

# 34. Version Roadmap

## Version 0.1 --- Parsing Prototype

``` text
Upload
 ↓
Sample
 ↓
Detect
 ↓
Parse
 ↓
Print normalized records
```

## Version 0.2 --- AI Parser

``` text
Unknown format
 ↓
LLM
 ↓
Configuration
 ↓
Validation
 ↓
Parse
```

## Version 0.3 --- Analytics

``` text
Traffic
Endpoints
IPs
Status codes
Peak hours
```

## Version 0.4 --- Security

``` text
Brute force
Scanning
SQL indicators
Bots
```

## Version 0.5 --- ML

``` text
Features
 ↓
Isolation Forest
 ↓
Anomalies
```

## Version 0.6 --- Risk Engine

``` text
Rules + ML
 ↓
Risk score
```

## Version 0.7 --- Dashboard

``` text
Professional Streamlit UI
```

## Version 1.0 --- Complete MVP

``` text
Upload
→ Detect
→ AI Assist
→ Validate
→ Parse
→ Normalize
→ Analyze
→ Detect
→ ML
→ Risk
→ Dashboard
```

------------------------------------------------------------------------

# 35. Future Version

After Version 1.0:

``` text
Live log monitoring
        ↓
Kafka / Redis Streams
        ↓
Streaming parser
        ↓
Real-time anomaly detection
        ↓
Real-time alerts
```

Then potentially:

``` text
FastAPI
+
PostgreSQL
+
Redis
+
Celery/RQ
+
Docker
+
Cloud deployment
```

Eventually:

``` text
LogSentinel
     │
     ├── Log Intelligence
     ├── Security Detection
     ├── ML Anomaly Detection
     ├── AI Investigation Assistant
     └── Alerting
```

------------------------------------------------------------------------

# 36. Success Criteria

The project is considered successful when:

-   [ ] A user can upload an unfamiliar log.
-   [ ] The system can create a representative sample.
-   [ ] Known formats are detected without an LLM.
-   [ ] Unknown formats can be analyzed by an LLM.
-   [ ] The LLM returns structured configuration rather than executable
    code.
-   [ ] Python validates that configuration.
-   [ ] The full log can be parsed using the validated configuration.
-   [ ] Different formats produce the same normalized schema.
-   [ ] Analytics are generated.
-   [ ] Security rules identify suspicious patterns.
-   [ ] ML identifies unusual behavioural windows.
-   [ ] A combined risk score is generated.
-   [ ] The dashboard explains important findings.
-   [ ] Unit tests cover the core processing pipeline.
-   [ ] The project can process larger files without unnecessarily
    loading everything into memory.

------------------------------------------------------------------------

# 37. Development Rule

At every phase follow:

``` text
Design
 ↓
Implement
 ↓
Test
 ↓
Validate
 ↓
Document
 ↓
Move to next phase
```

Do not keep adding features while the previous layer is unreliable.

The dependency chain is:

``` text
Parsing
  ↓
Normalization
  ↓
Analytics/Security
  ↓
Feature Engineering
  ↓
ML
  ↓
Risk
  ↓
Dashboard
```

If parsing is wrong, ML will be wrong.

If normalization is wrong, analytics will be wrong.

If feature engineering is weak, ML will be weak.

Therefore the project should be built from the bottom up.

------------------------------------------------------------------------

# 38. Immediate Next Step

After this plan, the next artifact should be:

``` text
PRD.md
```

The PRD should define:

-   users
-   user stories
-   features
-   functional requirements
-   non-functional requirements
-   MVP scope
-   acceptance criteria
-   user workflow
-   product success metrics

After PRD:

``` text
ARCHITECTURE.md
        ↓
DATA_SCHEMA.md
        ↓
AI_PARSER_DESIGN.md
        ↓
SECURITY_DESIGN.md
        ↓
ML_DESIGN.md
        ↓
DATABASE_SCHEMA.md
        ↓
IMPLEMENTATION
```

**We should not start coding before these core decisions are frozen.**

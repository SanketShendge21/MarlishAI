
# 🏗️ Marlish.AI — Enterprise Technology Integration Guide

**Purpose:** Honest analysis of which modern technologies are worth integrating into Marlish.AI, why each one fits (or doesn't), and a concrete implementation plan for the ones that do.  
**Audience:** Sanket & Shreyas — for resume positioning and genuine architectural growth.  
**Last Updated:** May 2026

---

## ⚠️ Honest Framing Before You Start

Not every technology on the list is worth integrating. Adding technologies to a project just to list them on a resume is detectable by any senior engineer who interviews you — and they will ask you to justify every choice. The goal here is to integrate technologies that **solve a real problem in this project** AND build a skill that transfers.

**Technologies recommended for Marlish.AI:** Docker, Kubernetes (minikube), Apache Kafka, Anthropic API  
**Technologies NOT recommended:** C/C++ rewrite of the rule engine (it's already < 5ms — there is nothing to optimize), Java + Angular admin dashboard (pure padding, no user value, two weeks of work for two resume keywords)

The four recommended technologies tell a coherent, defensible story:
> *"I built an event-driven, containerized ML translation system with a generative AI layer for cultural context, orchestrated on Kubernetes."*

That sentence gets you past automated resume screens and holds up in a 30-minute technical interview. The C++ and Java version does not.

---

## Table of Contents

1. [Docker — Containerization](#1-docker--containerization)
2. [Kubernetes — Container Orchestration](#2-kubernetes--container-orchestration)
3. [Apache Kafka — Event Streaming](#3-apache-kafka--event-streaming)
4. [Anthropic Claude API — Generative AI Layer](#4-anthropic-claude-api--generative-ai-layer)
5. [Technologies NOT Recommended — And Why](#5-technologies-not-recommended--and-why)
6. [Combined Architecture](#6-combined-architecture)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Resume Language Guide](#8-resume-language-guide)

---

## 1. Docker — Containerization

### What It Is

Docker is a platform for packaging applications and all their dependencies into a standardized unit called a **container**. A container is a lightweight, portable, isolated environment that runs identically on any machine — your laptop, your teammate's machine, a cloud server, or a CI/CD pipeline.

Think of it as the difference between sharing a recipe (sharing your code) versus sharing a fully cooked meal in a sealed box (sharing a Docker image). The recipient gets exactly what you made, not a approximation that depends on their kitchen setup.

### What It Is Used For

- Packaging an application with its exact runtime environment (Python version, libraries, system dependencies)
- Ensuring "it works on my machine" becomes "it works on every machine"
- Enabling consistent deployments across development, staging, and production
- Making microservices independently deployable
- Being the prerequisite for Kubernetes (K8s orchestrates Docker containers)

### Why We Need It in Marlish.AI

Currently, running the Python ML backend requires:
```
1. Install Python 3.13 exactly
2. Create a virtual environment
3. Install PyTorch with the right CUDA version
4. Install HuggingFace Transformers
5. Install IndicXlit (AI4Bharat)
6. Set up the right directory structure
7. Run export_onnx.py
8. Hope your collaborator's environment matches yours
```

This is fragile. The Shreyas-Sanket collaboration already ran into CUDA version issues. Docker eliminates this entirely.

Additionally, as we add a Kafka consumer service and potentially an API layer, those need to run as separate, isolated processes. Docker is how you do that cleanly.

### The Problem It Solves

| Problem Without Docker | Solution With Docker |
|---|---|
| "Works on my machine, not yours" | Identical container image runs everywhere |
| Environment setup takes hours for new collaborators | `docker pull marlish-ml-backend` → done |
| Python version conflicts | Each container pins its exact Python version |
| Can't run ML backend and frontend without conflicts | Each service has its own container |
| Deploying to a server requires manual environment setup | `docker run` is the deployment |

### What We Containerize in Marlish.AI

**Container 1: `marlish-frontend`**
- The Next.js application
- Node.js 18, npm dependencies, compiled Next.js app
- Exposes port 3000

**Container 2: `marlish-ml-service`**
- The Python ML backend: IndicXlit, opus-mt ONNX inference, transliteration pipeline
- Python 3.11, PyTorch, HuggingFace, AI4Bharat libraries
- FastAPI server that accepts translation requests
- Exposes port 8000

**Container 3: `marlish-kafka-consumer`**
- Python service that reads from Kafka topics
- Processes user feedback events, logs corrections, prepares data for future retraining
- No HTTP port — purely event-driven

### Implementation

**`docker/ml-service/Dockerfile`:**

```dockerfile
FROM python:3.11-slim

# System dependencies for ML libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (Docker layer caching optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/transliterator/ ./scripts/transliterator/
COPY api/ ./api/
COPY public/transliteration_map.json ./public/
COPY public/models/ ./public/models/

# Set environment variables
ENV PYTHONPATH=/app
ENV MODEL_PATH=/app/public/models/opus-mt-mr-en

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`docker/frontend/Dockerfile`:**

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
```

**`docker-compose.yml` (for local development):**

```yaml
version: '3.9'

services:
  frontend:
    build:
      context: .
      dockerfile: docker/frontend/Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_ML_API_URL=http://ml-service:8000
    depends_on:
      ml-service:
        condition: service_healthy

  ml-service:
    build:
      context: .
      dockerfile: docker/ml-service/Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./public/models:/app/public/models  # Mount models to avoid re-downloading
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    depends_on:
      - kafka
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  kafka-consumer:
    build:
      context: .
      dockerfile: docker/kafka-consumer/Dockerfile
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    depends_on:
      - kafka
      - ml-service

  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

**Run the full stack:**

```bash
docker-compose up --build
# Frontend available at http://localhost:3000
# ML API available at http://localhost:8000
# Kafka available at localhost:9092
```

### Resume Claim

> "Containerized a multi-service ML application using Docker, packaging the React frontend and Python ML inference backend (IndicXlit + ONNX runtime) into separate images with Docker Compose orchestration for local development."

---

## 2. Kubernetes — Container Orchestration

### What It Is

Kubernetes (K8s) is a system for automating the deployment, scaling, and management of containerized applications. Where Docker packages and runs containers, Kubernetes answers the question: *how do you manage dozens (or thousands) of containers across multiple machines?*

K8s abstracts infrastructure into a **declarative model** — you describe the desired state of your system in YAML files, and Kubernetes continuously works to make reality match that description.

Core concepts you need to know:
- **Pod:** The smallest deployable unit — one or more containers that run together
- **Deployment:** A controller that manages replicas of a Pod and handles rolling updates
- **Service:** A stable network endpoint that routes traffic to the right Pods
- **ConfigMap / Secret:** External configuration and sensitive data injected into containers
- **Ingress:** HTTP routing from the outside world into the cluster

### What It Is Used For

- Running applications reliably with automatic restarts if a container crashes
- Scaling: run 3 copies of the ML service when traffic is high, scale back when it isn't
- Rolling updates: deploy a new model version with zero downtime
- Load balancing across multiple service instances
- Standardized declarative deployment for any cloud provider (AWS EKS, GCP GKE, Azure AKS)

### Why We Use It in Marlish.AI

In production, the ML inference service is the most resource-intensive component. When multiple users submit complex Marlish sentences simultaneously, inference queues up. Kubernetes lets you:

1. Run 2–3 replicas of `marlish-ml-service` in parallel during high-traffic periods
2. Automatically restart the ML service if it crashes (model loading failures happen)
3. Deploy a new version of the transliteration pipeline without taking the app offline
4. Use the same deployment configuration locally (minikube) and in the cloud

For a portfolio project, you don't need a real cloud cluster. **minikube** runs a single-node Kubernetes cluster entirely on your laptop. You get all the YAML, all the kubectl commands, all the operational experience — on your local machine, for free.

### The Problem It Solves

| Problem Without K8s | Solution With K8s |
|---|---|
| ML service crashes → whole app is down | K8s auto-restarts crashed containers |
| High traffic → translations queue and timeout | Scale ML service to multiple replicas |
| Deploy new model → manually stop and restart | Rolling update with zero downtime |
| Different deployment configs per environment | Same YAML across local/staging/prod |
| "It works in Docker Compose" ≠ "It works in production" | K8s manifests are the production standard |

### Kubernetes Manifests for Marlish.AI

**`k8s/ml-service-deployment.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: marlish-ml-service
  labels:
    app: marlish-ml-service
    version: v1
spec:
  replicas: 2                          # Run 2 copies for redundancy
  selector:
    matchLabels:
      app: marlish-ml-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1                      # Max extra pods during update
      maxUnavailable: 0                # Never kill a pod before a new one is ready
  template:
    metadata:
      labels:
        app: marlish-ml-service
    spec:
      containers:
        - name: ml-service
          image: marlish-ml-service:latest
          ports:
            - containerPort: 8000
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "2Gi"            # ML models need memory headroom
              cpu: "1000m"
          env:
            - name: KAFKA_BOOTSTRAP_SERVERS
              valueFrom:
                configMapKeyRef:
                  name: marlish-config
                  key: kafka.bootstrap.servers
          readinessProbe:              # Only send traffic when model is loaded
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 60   # Give time for model to load
            periodSeconds: 10
          livenessProbe:               # Restart if the container hangs
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 90
            periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: marlish-ml-service
spec:
  selector:
    app: marlish-ml-service
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: ClusterIP                      # Internal only — frontend calls this
```

**`k8s/frontend-deployment.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: marlish-frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: marlish-frontend
  template:
    metadata:
      labels:
        app: marlish-frontend
    spec:
      containers:
        - name: frontend
          image: marlish-frontend:latest
          ports:
            - containerPort: 3000
          env:
            - name: NEXT_PUBLIC_ML_API_URL
              value: "http://marlish-ml-service:8000"
---
apiVersion: v1
kind: Service
metadata:
  name: marlish-frontend
spec:
  selector:
    app: marlish-frontend
  ports:
    - port: 80
      targetPort: 3000
  type: LoadBalancer                   # Exposes to external traffic
```

**`k8s/configmap.yaml`:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: marlish-config
data:
  kafka.bootstrap.servers: "kafka-service:9092"
  model.path: "/app/public/models/opus-mt-mr-en"
  confidence.threshold: "0.70"
```

**`k8s/hpa.yaml` — Horizontal Pod Autoscaler (the impressive part):**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: marlish-ml-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: marlish-ml-service
  minReplicas: 1
  maxReplicas: 5                       # Scale up to 5 pods under load
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70       # Scale when CPU hits 70%
```

**Deploy to minikube:**

```bash
# Start local cluster
minikube start --cpus 4 --memory 8192

# Point Docker to minikube's registry
eval $(minikube docker-env)

# Build images into minikube's Docker
docker build -t marlish-frontend:latest -f docker/frontend/Dockerfile .
docker build -t marlish-ml-service:latest -f docker/ml-service/Dockerfile .

# Apply all manifests
kubectl apply -f k8s/

# Check everything is running
kubectl get pods
kubectl get services

# Open the frontend
minikube service marlish-frontend
```

### Resume Claim

> "Designed a scalable microservices architecture for a multilingual ML system, writing Kubernetes manifests for multi-replica deployment with rolling updates, readiness probes, and a Horizontal Pod Autoscaler configured to scale the ML inference service from 1 to 5 replicas under CPU load. Validated locally using minikube."

---

## 3. Apache Kafka — Event Streaming

### What It Is

Apache Kafka is a distributed event streaming platform. At its core, it is a high-throughput, fault-tolerant, ordered log of events (messages) organized into **topics**. Producers write events to topics; consumers read from those topics, independently and at their own pace.

The key distinction from a normal message queue (like RabbitMQ): **Kafka retains all messages for a configurable period (default 7 days)**. This means multiple consumers can independently process the same events, you can replay events from any point in time, and no data is lost if a consumer is temporarily offline.

Core concepts:
- **Topic:** A named, ordered log of events (e.g., `translation-events`, `user-feedback`)
- **Producer:** Code that writes events to a topic
- **Consumer:** Code that reads events from a topic
- **Consumer Group:** Multiple consumer instances that share the work of processing a topic
- **Partition:** Topics are split into partitions for parallelism
- **Broker:** A single Kafka server; a cluster has multiple brokers

### What It Is Used For

- Real-time analytics pipelines (log every user action as an event)
- Decoupling services: producer doesn't know or care who consumes its events
- Async processing: fire an event and move on; consumer processes it in the background
- Data pipeline for ML retraining: collect production data continuously for model improvement
- Event sourcing: the event log is the source of truth

### Why We Use It in Marlish.AI

Marlish.AI has a fundamental data problem: **the best training data for improving the model is the translations users actually make, corrected by users who found them wrong.** Right now, none of this is captured. Every corrected translation is lost.

Kafka creates the data flywheel:

```
User translates "udya kay scene ahe"
    → ML outputs "What's happening tomorrow?" (confidence 0.71)
    → User manually edits to "What's the plan for tomorrow?"
    → This correction is GOLD DATA — it's a real Marlish sentence with a human-verified translation

Without Kafka: this correction disappears
With Kafka:    it flows into a topic → consumer processes it → stored for retraining
```

Additionally, Kafka lets us capture translation telemetry without blocking the user experience. When a user translates, we fire an event asynchronously — the event doesn't need to complete before the translation appears on screen.

### The Problem It Solves

| Problem Without Kafka | Solution With Kafka |
|---|---|
| User corrections are lost forever | Every correction flows into `user-feedback` topic |
| No data on which translations fail | Every translation fires a `translation-events` event |
| Retraining requires manual data collection | Consumer continuously builds the retraining dataset |
| Analytics requires synchronous DB calls (slows the app) | Fire-and-forget async events, processed in background |
| Can't replay past data to debug model behavior | Kafka retains all events for 7 days by default |

### What Events We Fire

**Topic 1: `translation-events`**
Fired on every translation — regardless of confidence level.

```python
# Event payload schema
{
  "event_id":      "uuid-v4",
  "timestamp":     "2026-05-26T10:30:00Z",
  "session_id":    "anon-hash-of-session",   # Anonymous — no PII
  "input_text":    "udya kay scene ahe",
  "direction":     "marlish_to_english",
  "tier_used":     2,                         # 1 = rule engine, 2 = ML
  "output_text":   "What's the plan for tomorrow?",
  "confidence":    0.84,
  "transliteration_intermediate": "उद्या काय scene आहे",
  "latency_ms":    423
}
```

**Topic 2: `user-feedback`**
Fired when a user corrects a translation or rates it thumbs down.

```python
{
  "event_id":         "uuid-v4",
  "timestamp":        "2026-05-26T10:30:45Z",
  "original_event_id": "uuid-of-translation-event",
  "input_text":       "udya kay scene ahe",
  "rejected_output":  "What's happening tomorrow?",
  "corrected_output": "What's the plan for tomorrow?",   # Null if thumbs-down only
  "direction":        "marlish_to_english",
  "feedback_type":    "correction"  # or "thumbs_down"
}
```

### Implementation

**Producer (in `api/app.py` — fires on every translation):**

```python
from confluent_kafka import Producer
import json, os, uuid
from datetime import datetime, timezone

KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
}
producer = Producer(KAFKA_CONFIG)

def fire_translation_event(input_text: str, output_text: str, direction: str,
                            tier: int, confidence: float, latency_ms: float,
                            devanagari_intermediate: str = None):
    event = {
        "event_id":                     str(uuid.uuid4()),
        "timestamp":                    datetime.now(timezone.utc).isoformat(),
        "input_text":                   input_text,
        "direction":                    direction,
        "tier_used":                    tier,
        "output_text":                  output_text,
        "confidence":                   confidence,
        "transliteration_intermediate": devanagari_intermediate,
        "latency_ms":                   round(latency_ms, 2)
    }
    # Fire-and-forget — doesn't block the API response
    producer.produce(
        'translation-events',
        key=direction,
        value=json.dumps(event).encode('utf-8'),
        callback=lambda err, msg: print(f"Kafka delivery error: {err}") if err else None
    )
    producer.poll(0)  # Non-blocking flush

def fire_feedback_event(original_event_id: str, input_text: str,
                         rejected_output: str, corrected_output: str,
                         direction: str, feedback_type: str):
    event = {
        "event_id":            str(uuid.uuid4()),
        "timestamp":           datetime.now(timezone.utc).isoformat(),
        "original_event_id":   original_event_id,
        "input_text":          input_text,
        "rejected_output":     rejected_output,
        "corrected_output":    corrected_output,
        "direction":           direction,
        "feedback_type":       feedback_type
    }
    producer.produce(
        'user-feedback',
        key=direction,
        value=json.dumps(event).encode('utf-8')
    )
    producer.poll(0)
```

**Consumer (`scripts/kafka_consumer.py` — runs as a separate Docker container):**

```python
from confluent_kafka import Consumer
import json, csv, os
from pathlib import Path

KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    'group.id':          'marlish-data-pipeline',
    'auto.offset.reset': 'earliest'   # Process all events from beginning on first start
}

OUTPUT_DIR = Path("data/collected")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

consumer = Consumer(KAFKA_CONFIG)
consumer.subscribe(['translation-events', 'user-feedback'])

print("Kafka consumer started. Waiting for events...")

# Rolling CSV files for retraining data
with (
    open(OUTPUT_DIR / "translation_log.csv", "a", newline="") as trans_f,
    open(OUTPUT_DIR / "corrections.csv", "a", newline="") as corr_f
):
    trans_writer = csv.DictWriter(trans_f, fieldnames=[
        "timestamp", "input_text", "output_text", "direction",
        "confidence", "tier_used", "latency_ms"
    ])
    corr_writer = csv.DictWriter(corr_f, fieldnames=[
        "timestamp", "input_text", "corrected_output", "direction"
    ])

    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        topic = msg.topic()
        event = json.loads(msg.value().decode('utf-8'))

        if topic == 'translation-events':
            trans_writer.writerow({
                "timestamp":   event["timestamp"],
                "input_text":  event["input_text"],
                "output_text": event["output_text"],
                "direction":   event["direction"],
                "confidence":  event["confidence"],
                "tier_used":   event["tier_used"],
                "latency_ms":  event["latency_ms"]
            })
            trans_f.flush()

        elif topic == 'user-feedback' and event.get("corrected_output"):
            # Only write corrections with actual corrected text — these are training gold
            corr_writer.writerow({
                "timestamp":       event["timestamp"],
                "input_text":      event["input_text"],
                "corrected_output": event["corrected_output"],
                "direction":       event["direction"]
            })
            corr_f.flush()
            print(f"✅ Correction captured: '{event['input_text']}' → '{event['corrected_output']}'")
```

**Adding the thumbs-down UI (in `app/components/TranslatorPanel.jsx`):**

```javascript
// After displaying a translation result, show a feedback row
{translationResult && (
  <div className="feedback-row">
    <button
      onClick={() => submitFeedback('thumbs_up')}
      aria-label="Good translation"
    >👍</button>
    <button
      onClick={() => submitFeedback('thumbs_down')}
      aria-label="Bad translation"
    >👎</button>
    <button
      onClick={() => setEditingCorrection(true)}
      aria-label="Suggest correction"
    >✏️ Correct this</button>
  </div>
)}
```

### Kafka in Kubernetes

**`k8s/kafka.yaml`:**

```yaml
apiVersion: apps/v1
kind: StatefulSet           # StatefulSet (not Deployment) — Kafka needs persistent identity
metadata:
  name: kafka
spec:
  serviceName: kafka
  replicas: 1               # Single broker for dev/portfolio; 3+ for real production
  selector:
    matchLabels:
      app: kafka
  template:
    metadata:
      labels:
        app: kafka
    spec:
      containers:
        - name: kafka
          image: confluentinc/cp-kafka:7.4.0
          ports:
            - containerPort: 9092
          env:
            - name: KAFKA_BROKER_ID
              value: "1"
            - name: KAFKA_ZOOKEEPER_CONNECT
              value: "zookeeper:2181"
            - name: KAFKA_ADVERTISED_LISTENERS
              value: "PLAINTEXT://kafka:9092"
            - name: KAFKA_AUTO_CREATE_TOPICS_ENABLE
              value: "true"
          volumeMounts:
            - name: kafka-storage
              mountPath: /var/lib/kafka/data
  volumeClaimTemplates:
    - metadata:
        name: kafka-storage
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 5Gi
```

### Resume Claim

> "Implemented an asynchronous event-streaming pipeline using Apache Kafka to capture translation telemetry and user corrections as real-time events. Wrote a Python Kafka consumer that continuously builds a gold correction dataset for future model retraining, decoupling data collection from the inference path."

---

## 4. Anthropic Claude API — Generative AI Layer

### What It Is

Anthropic's Claude API is a programmatic interface to Claude — a large language model (LLM) capable of understanding context, generating natural language, and reasoning about complex topics. Unlike opus-mt (which does one thing: translate from language A to language B), an LLM like Claude can explain, compare, contextualize, and reason about language.

You send Claude a text prompt and it returns a generated response. The API is stateless — each call is independent unless you pass conversation history.

### What It Is Used For

- Text generation, summarization, question-answering
- Code generation and explanation
- Contextual analysis and reasoning tasks where rules would be too complex to write manually
- Augmenting specialized ML pipelines with general-purpose intelligence

### Why We Use It in Marlish.AI

opus-mt and IndicXlit handle the mechanical task: *take this Marlish sentence, output this English sentence.* But Hinglish and Marlish are rich with **cultural context** that translation alone cannot capture.

Consider:
- `"kya scene hai"` → opus-mt translates "What is the scene?" (technically correct, culturally wrong — it means "What's the plan?")
- `"jhol"` → no clean translation; it means a messy, complicated situation with unclear motives — and there is no English word for it
- `"bakwas band kar"` → literally "stop nonsense" but culturally equivalent to "shut up / cut it out" with a specific register
- `"jugaad"` → a resourceful improvised solution; entire concept untranslatable to English

This is exactly where an LLM adds value that a translation model cannot. Claude can explain the **cultural layer** behind the translation: what the word actually means to the people who use it, when it's used, what emotional tone it carries.

**The feature: "Cultural Context" side panel**

When the translation result appears, a small expandable panel shows:
- What the slang/phrase actually means beyond the literal translation
- The cultural context in which it's used
- The emotional register (casual/aggressive/affectionate/sarcastic)
- An analogous phrase in English if one exists

This is a genuine product feature that a language learner, a developer building Indian chat apps, or a non-native speaker would actually use. It is not forced.

### The Problem It Solves

| Gap in Translation-Only System | Solution with Claude API |
|---|---|
| `kya scene hai` → "What is the scene?" (wrong meaning) | Claude explains: "This is casual Hinglish for 'what's the plan?' — common in urban Indian youth culture" |
| `jhol` has no English equivalent | Claude explains the concept: messy/sketchy situation, untranslatable nuance |
| Regional slang changes meaning by tone | Claude explains register: "used affectionately between friends vs. sarcastically" |
| Non-native speakers don't understand why the translation is what it is | Claude provides the cultural reasoning |

### Implementation

**`api/cultural_explainer.py`:**

```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """You are a cultural linguist specializing in Indian languages,
specifically Hinglish (Hindi-English code-mix) and Marlish (Marathi-English code-mix).

When given an input phrase and its English translation, provide a concise cultural
explanation covering:
1. What the phrase actually means in context (beyond the literal translation)
2. When and how it is typically used (social context, relationship type)
3. The emotional register or tone (casual/formal, affectionate/aggressive/neutral)
4. A close English equivalent if one exists, or explain why none does

Be concise — 2-4 sentences maximum. Write for someone learning Indian culture,
not an academic. Use plain language."""

def get_cultural_explanation(
    input_phrase: str,
    translation: str,
    direction: str
) -> str:
    """
    Returns a 2-4 sentence cultural explanation of the input phrase.
    Only called for low-confidence translations or phrases flagged as slang.
    """
    prompt = f"""Input phrase: "{input_phrase}"
Translation: "{translation}"
Language direction: {direction}

Explain the cultural context and meaning of this phrase."""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,            # Short explanations only
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text
```

**Integration in `api/app.py`:**

```python
from .cultural_explainer import get_cultural_explanation

@app.post("/translate")
async def translate(request: TranslationRequest):
    # ... existing translation logic ...

    response = TranslationResponse(
        translation=translation,
        devanagari_intermediate=devanagari,
        confidence=confidence,
        latency_ms=latency
    )

    # Add cultural explanation for slang or low-confidence results
    # Only call the LLM when it adds value — not for every translation
    is_slang = any(word in request.text.lower() for word in SLANG_INDICATORS)
    should_explain = confidence < 0.80 or is_slang

    if should_explain and request.include_cultural_context:
        try:
            response.cultural_explanation = get_cultural_explanation(
                input_phrase=request.text,
                translation=translation,
                direction=request.direction
            )
        except Exception as e:
            # Non-critical — never fail a translation because the LLM is unavailable
            print(f"Cultural explainer failed: {e}")
            response.cultural_explanation = None

    return response
```

**Frontend side panel (`app/components/CulturalContext.jsx`):**

```javascript
export function CulturalContext({ explanation, isLoading }) {
  if (!explanation && !isLoading) return null;

  return (
    <div className="cultural-context-panel">
      <div className="panel-header">
        <span className="icon">🌏</span>
        <span>Cultural Context</span>
      </div>
      {isLoading ? (
        <div className="loading-pulse">Analyzing cultural nuance...</div>
      ) : (
        <p className="explanation-text">{explanation}</p>
      )}
    </div>
  );
}
```

**Example output for `"kya scene hai"`:**

> *"Kya scene hai" is casual Hinglish slang meaning "what's the plan?" or "what's going on?" — equivalent to asking "what's up?" in American English. It's used between close friends in informal urban settings, typically among Indian youth aged 15–30. There's no single English equivalent; the closest would be "what's the vibe?" or "what are we doing?"*

### Cost Management

The Claude API charges per token. For a portfolio project:

- Average explanation: ~150–200 output tokens
- Cost: approximately $0.003 per explanation (claude-sonnet-4-5 pricing)
- If 100 users trigger explanations daily: ~$0.30/day — negligible

For cost control:
1. Only call the API when `confidence < 0.80 OR is_slang == True` (not every translation)
2. Cache explanations for repeated phrases in Redis or a simple JSON file
3. Add a rate limit: max 20 API calls per user session

### Resume Claim

> "Integrated the Anthropic Claude API to build a 'Cultural Context' feature that provides LLM-generated semantic and cultural explanations for Indian slang and code-mixed phrases, filling the gap where traditional NLP translation models cannot capture cultural nuance. Implemented conditional invocation logic to call the LLM only for slang-flagged or low-confidence translations, minimizing API cost while maximizing user value."

---

## 5. Technologies NOT Recommended — And Why

### ❌ C/C++ Rewrite of the Rule Engine

**The claim:** "Rewrite the 8-layer rule engine in C++ to reduce latency."

**The reality:** The rule engine already runs in < 5ms. This is faster than human perception (the eye can't perceive differences below ~16ms). There is no user-facing latency problem to solve. Rewriting it in C++ would reduce it to < 1ms — a difference nobody will notice.

Any senior engineer who interviews you will ask: "What was the latency before and after? How did you measure it? What was the bottleneck?" If the answer is "it went from 3ms to 0.8ms," they will know you solved a problem that didn't exist. That is worse than not doing it.

**What to say instead:** The correct performance optimization story is the two-tier architecture itself — routing 80% of inputs to a < 5ms rule engine instead of sending everything to a 500–1500ms ML model. That's a real, defensible performance decision.

### ❌ Java + Spring Boot Analytics Service

**The claim:** "Build a Java Spring Boot service as a Kafka consumer to aggregate analytics."

**The reality:** The Kafka consumer (`scripts/kafka_consumer.py`) is already 50 lines of Python and does exactly what a Spring Boot service would do — consume events, write to a file, log corrections. Spring Boot would be 400 lines of Java boilerplate to accomplish the same thing.

Adding Java here serves only one purpose: adding "Java" to the resume. Interviewers know this. You'd spend two weeks learning Spring Boot to check a box, adding a service that duplicates functionality you already built in Python.

**What to say instead:** If Java is specifically required for a job you're targeting, build a separate standalone project (a Java Spring Boot API for a different purpose). Don't shoehorn it into Marlish.AI where it doesn't fit.

### ❌ Angular Admin Dashboard

**The same argument applies:** Angular exists for large-scale single-page applications with complex component hierarchies and enterprise-grade dependency injection. A simple analytics dashboard showing translation counts and correction rates is better built in 1 hour with React (which you already know) than in 2 weeks with Angular (which you'd be learning from scratch).

Adding a framework you just learned for the purpose of listing it is detectable in an interview. "Why did you choose Angular over React here?" is a question you need a real answer for.

---

## 6. Combined Architecture

With all four technologies integrated, the full system looks like this:

```
┌─────────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER (minikube)                 │
│                                                                 │
│  ┌──────────────────┐    HTTP     ┌───────────────────────┐     │
│  │  marlish-frontend│ ──────────► │  marlish-ml-service   │     │
│  │  (Next.js)       │             │  (FastAPI)            │     │
│  │  Pod × 1         │             │  Pod × 2 (HPA: 1-5)   │     │
│  └──────────────────┘             │                       │     │
│           │                       │  IndicXlit            │     │
│           │                       │  + opus-mt ONNX       │     │
│           │                       │  + Anthropic API call │     │
│           │                       └───────────┬───────────┘     │
│           │                                   │                  │
│           │                          Kafka Producer              │
│           │                                   │                  │
│           │                    ┌──────────────▼──────────────┐   │
│           │                    │       Apache Kafka           │   │
│           │                    │  topic: translation-events  │   │
│           │                    │  topic: user-feedback       │   │
│           │                    └──────────────┬──────────────┘   │
│           │                                   │                  │
│           │ (feedback UI)            ┌─────────▼──────────┐      │
│           └─────────────────────────►  kafka-consumer     │      │
│                                      │  (Python)          │      │
│                                      │  Writes to:        │      │
│                                      │  - translation_log │      │
│                                      │  - corrections.csv │      │
│                                      └────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘

External:
  Anthropic Claude API ←── ml-service calls this for cultural context
```

**Request flow for a complex Marlish sentence:**

```
1. User types "udya kay scene ahe bro" in browser (Next.js)
2. Adaptive debounce fires after 500ms
3. Browser sends POST /translate to Frontend
4. Frontend proxies to ml-service (Kubernetes Service DNS: marlish-ml-service:8000)
5. ml-service runs 8-layer rule engine → confidence 0.68 (below threshold)
6. ml-service runs IndicXlit transliteration → "उद्या काय scene आहे bro"
7. ml-service runs opus-mt ONNX inference → "What's the plan for tomorrow, bro?"
8. ml-service fires Kafka event to `translation-events` topic (async, non-blocking)
9. ml-service calls Anthropic API → "kya scene hai is casual Hinglish..."
10. Response returned to browser: translation + cultural explanation
11. Kafka consumer picks up the translation-events message, logs to CSV
12. User sees result, clicks 👎, types correction
13. Browser sends POST /feedback
14. ml-service fires Kafka event to `user-feedback` topic
15. Kafka consumer picks it up, writes to corrections.csv (future training gold)
```

---

## 7. Implementation Roadmap

These phases happen **after** the core IndicXlit + opus-mt pipeline from the main architecture plan is complete and working.

| Phase | Task | Estimated Days | Outcome |
|---|---|---|---|
| **A** | Dockerize frontend + ml-service + Kafka consumer | 2 | `docker-compose up` runs the full stack |
| **B** | Anthropic API cultural explainer feature | 1.5 | Side panel shows cultural context for slang |
| **C** | Kafka producer in ml-service + consumer script | 2 | Events flowing, corrections captured |
| **D** | Kubernetes manifests + minikube deploy | 2 | Full stack running in K8s locally |
| **E** | HPA demo + rolling update demo | 0.5 | Proof of scalability story |
| **Total** | | **~8 days** | Enterprise-grade portfolio piece |

**Prerequisites before starting Phase A:**
- v1 pipeline from the main plan is complete (IndicXlit + opus-mt working in browser)
- Demo video of v1 is recorded (record this before adding complexity)
- All Phase 0–5 from the architecture plan are done

---

## 8. Resume Language Guide

Use these exact formulations. Each claim is specific, technical, and fully defensible.

### One-Line Project Description

> "Built an enterprise-grade multilingual NLP system for Indian code-mixed languages (Hinglish/Marlish), featuring a containerized microservices architecture with Kubernetes orchestration, Apache Kafka event streaming, and a generative AI cultural context layer powered by the Anthropic Claude API."

### Bullet Points by Technology

**Docker:**
> Containerized a multi-service ML application (React frontend, Python FastAPI inference backend, Kafka consumer) using Docker, enabling reproducible ML environments and eliminating dependency management across collaborators.

**Kubernetes:**
> Designed Kubernetes deployment manifests for a multi-replica ML inference service with readiness probes, rolling update strategy, and a Horizontal Pod Autoscaler configured to scale from 1 to 5 replicas under CPU load. Validated on minikube.

**Apache Kafka:**
> Implemented an asynchronous event-streaming pipeline using Apache Kafka (topics: translation-events, user-feedback) to capture translation telemetry and user corrections, building a continuous gold-standard correction dataset for future model retraining without blocking the inference path.

**Anthropic API:**
> Integrated the Anthropic Claude API to generate cultural context explanations for Indian slang and code-mixed phrases, augmenting traditional NLP translation with LLM-powered semantic analysis. Implemented conditional invocation (triggered only for slang-flagged or low-confidence results) to minimize API cost.

**Full ML Stack:**
> Built a two-tier hybrid translation system: an 8-layer rule-based NLP engine (< 5ms, handles ~80% of inputs) backed by an ONNX-quantized Helsinki opus-mt model with a custom AI4Bharat IndicXlit transliteration preprocessing pipeline (Marlish → Devanagari → English), achieving BLEU ~12–16 on real WhatsApp-style input.

### What to Say in Interviews

**"Why Kafka for this scale?"**
> "You're right that Kafka is overkill for the current user count. The decision was architectural — I wanted to demonstrate the correct pattern for a system that collects user corrections for continuous ML retraining. The feedback loop is the entire value of a self-improving translation system. A direct DB write would work at this scale, but it couples the feedback mechanism to the inference path. The Kafka pattern keeps them independent, which matters when you scale."

**"Why Kubernetes and not just Docker Compose?"**
> "Docker Compose is fine for local development, which is what I use it for. The Kubernetes manifests exist to demonstrate that I know how to write production deployment specs — HPA, readiness probes, rolling update strategy. I validated them locally on minikube. The point was to prove I can write infra that scales, not that I actually needed to scale this demo."

**"Why the Anthropic API and not fine-tuning an open model for this?"**
> "Cultural explanation of slang is a reasoning task, not a translation task. Fine-tuning a model to explain cultural nuance would require a dataset of cultural explanations that doesn't exist at the scale we'd need. Claude already has the cultural knowledge from pretraining. I'm calling it for what it's genuinely good at and using opus-mt for what translation models are good at. Each tool in its right place."

---

*This document is a companion to `ARCHITECTURE_ANALYSIS_AND_PLAN.md`. Implement the core IndicXlit + opus-mt pipeline first. Then add these technologies in the order shown in Section 7.*
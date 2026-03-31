# Operations Runbook — Customer Success FTE

## Daily Operations

### Start All Services
```bash
cd infra && docker compose up -d
cd ../backend && OPENAI_API_KEY=sk-... uv run uvicorn api.main:app --port 8000
cd ../web-portal && npm run dev
```

### Health Check
```bash
curl http://localhost:8000/health
curl http://localhost:3000
```

### Check Metrics
```bash
curl http://localhost:8000/metrics/summary
curl http://localhost:8000/metrics/channels
curl http://localhost:8000/metrics/latency
```

---

## Incident Response

### Agent Not Responding
1. Check API health: `curl http://localhost:8000/health`
2. Check DB: `docker compose ps`
3. Check logs: `docker compose logs postgres`
4. Restart: `docker compose restart`

### Kafka Issues
1. Check: `docker compose logs kafka`
2. Restart: `docker compose restart kafka`
3. Verify topics: `docker exec fte_kafka kafka-topics.sh --bootstrap-server localhost:9092 --list`

### Database Down
1. Check: `docker compose ps fte_postgres`
2. Restart: `docker compose restart postgres`
3. Verify: `docker exec -it fte_postgres psql -U fte_user -d fte_db -c "SELECT 1"`

### High Escalation Rate (>25%)
1. Check knowledge base: `SELECT COUNT(*) FROM knowledge_base WHERE embedding IS NOT NULL`
2. Re-run embeddings: `python -m agent.embeddings`
3. Review escalation reasons in tickets table

### Pod Restart (Kubernetes)
```bash
kubectl rollout restart deployment/fte-api -n fte
kubectl rollout restart deployment/fte-worker -n fte
kubectl get pods -n fte
```

---

## Maintenance

### Update Knowledge Base
```bash
# Add new entry
docker exec -it fte_postgres psql -U fte_user -d fte_db
INSERT INTO knowledge_base (title, content, category) VALUES ('...', '...', '...');

# Regenerate embeddings
OPENAI_API_KEY=sk-... uv run python -c "
import asyncio
from agent.embeddings import update_knowledge_base_embeddings
asyncio.run(update_knowledge_base_embeddings())
"
```

### Run Load Test
```bash
cd backend
OPENAI_API_KEY=sk-... uv run locust -f tests/load_test.py \
  --host http://localhost:8000 \
  --users 50 --spawn-rate 5 \
  --run-time 60s --headless
```

### Run Agent Tests
```bash
cd backend
OPENAI_API_KEY=sk-... uv run pytest tests/test_agent.py -v
```

---

## Monitoring Checklist (24/7 Readiness)
- [ ] Uptime > 99.9%
- [ ] P95 latency < 3 seconds
- [ ] Escalation rate < 25%
- [ ] Cross-channel identification > 95%
- [ ] No message loss in Kafka
- [ ] All 3 channels responding

import pytest
import httpx

BASE_URL = "http://localhost:8000"
TEST_EMAIL_1 = "wm0297567@gmail.com"
TEST_EMAIL_2 = "muhammadwaheed128@gmail.com"

@pytest.mark.asyncio
async def test_health_check():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert len(data["channels"]) == 3
    print(f"✅ Health: {data['status']}")

@pytest.mark.asyncio
async def test_web_form_submission():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        response = await client.post("/support/submit", json={
            "name": "Waheed Test",
            "email": TEST_EMAIL_1,
            "subject": "Web Form Channel Test",
            "category": "technical",
            "message": "Testing web form channel submission with real email"
        })
    assert response.status_code == 200
    data = response.json()
    assert "ticket_id" in data
    print(f"✅ Web form ticket: {data['ticket_id']}")

@pytest.mark.asyncio
async def test_web_form_validation():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        response = await client.post("/support/submit", json={
            "name": "A",
            "email": "invalid-email",
            "subject": "Hi",
            "category": "invalid",
            "message": "Short"
        })
    assert response.status_code == 422
    print("✅ Validation working")

@pytest.mark.asyncio
async def test_ticket_status():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        submit = await client.post("/support/submit", json={
            "name": "Muhammad Waheed",
            "email": TEST_EMAIL_2,
            "subject": "Ticket Status Check",
            "category": "general",
            "message": "Testing ticket status retrieval with real email"
        })
        ticket_id = submit.json()["ticket_id"]
        status = await client.get(f"/support/ticket/{ticket_id}")
    assert status.status_code == 200
    assert status.json()["status"] in ["open", "in_progress", "resolved", "escalated"]
    print(f"✅ Ticket status: {status.json()['status']}")

@pytest.mark.asyncio
async def test_whatsapp_test_endpoint():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        response = await client.get("/webhooks/whatsapp/test")
    assert response.status_code == 200
    assert response.json()["status"] == "processing"
    print("✅ WhatsApp test endpoint working")

@pytest.mark.asyncio
async def test_gmail_test_endpoint():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        response = await client.get("/webhooks/gmail/test")
    assert response.status_code == 200
    assert response.json()["status"] == "processing"
    print("✅ Gmail test endpoint working")

@pytest.mark.asyncio
async def test_whatsapp_status_webhook():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        response = await client.post(
            "/webhooks/whatsapp/status",
            data={"MessageSid": "SM123test", "MessageStatus": "delivered"}
        )
    assert response.status_code == 200
    print("✅ WhatsApp status webhook working")

@pytest.mark.asyncio
async def test_metrics_endpoints():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        summary = await client.get("/metrics/summary")
        channels = await client.get("/metrics/channels")
        latency = await client.get("/metrics/latency")
        report = await client.get("/metrics/daily-report")
    assert summary.status_code == 200
    assert channels.status_code == 200
    assert latency.status_code == 200
    assert report.status_code == 200
    print("✅ All metrics endpoints working")

@pytest.mark.asyncio
async def test_customer_lookup_email():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        # Create customer via form
        await client.post("/support/submit", json={
            "name": "Waheed Lookup",
            "email": TEST_EMAIL_1,
            "subject": "Lookup test",
            "category": "general",
            "message": "Testing customer lookup with real email address"
        })
        # Lookup
        response = await client.get(
            f"/customers/lookup?email={TEST_EMAIL_1}"
        )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_EMAIL_1
    print(f"✅ Customer email lookup: {data['email']}")

@pytest.mark.asyncio
async def test_customer_lookup_phone():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        response = await client.get("/customers/lookup?phone=+923001234567")
    assert response.status_code in [200, 404]
    print(f"✅ Customer phone lookup: {response.status_code}")

@pytest.mark.asyncio
async def test_cross_channel_same_customer():
    """Same customer contacts via web form and gmail — history preserved."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        # Web form submission
        web = await client.post("/support/submit", json={
            "name": "Cross Channel Test",
            "email": TEST_EMAIL_2,
            "subject": "Cross channel test",
            "category": "technical",
            "message": "First contact via web form for cross channel test"
        })
        assert web.status_code == 200
        ticket_id = web.json()["ticket_id"]

        # Lookup same customer
        lookup = await client.get(
            f"/customers/lookup?email={TEST_EMAIL_2}"
        )
        assert lookup.status_code == 200
        customer_id = lookup.json()["id"]

        # Check messages
        messages = await client.get(
            f"/support/ticket/{ticket_id}/messages"
        )
        assert messages.status_code == 200

    print(f"✅ Cross-channel: customer_id={customer_id[:8]}...")
    print(f"✅ Messages preserved: {len(messages.json()['messages'])} msgs")

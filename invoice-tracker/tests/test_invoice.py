def test_invoice_pdf_requires_login(client):
    response = client.get("/invoices/1/pdf")
    assert response.status_code == 302

def test_invoice_pdf_download(client):
    client.post("/signup", data={
        "name": "Test User",
        "email": "test@example.com",
        "password": "StrongPass123"
    })
    client.post("/clients", data={"name": "Client One", "email": "client@example.com"})
    response = client.post("/invoices", data={
        "client_id": "1",
        "description": "Website work",
        "amount": "1000",
        "due_date": "2030-01-01"
    })
    response = client.get("/invoices/1/pdf")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")

def signup(client, email, name):
    client.post("/signup", data={"name": name, "email": email, "password": "StrongPass123"})

def test_users_cannot_see_each_others_clients(app, client):
    signup(client, "a@example.com", "A")
    client.post("/clients", data={"name": "A Client", "email": "a@example.com"})
    client.post("/logout")

    signup(client, "b@example.com", "B")
    response = client.get("/clients")
    assert b"A Client" not in response.data

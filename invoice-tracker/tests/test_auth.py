from app import db, User

def test_signup_hashes_password(client, app):
    response = client.post("/signup", data={
        "name": "Test User",
        "email": "test@example.com",
        "password": "StrongPass123"
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        assert user is not None
        assert user.password_hash != "StrongPass123"
        assert user.check_password("StrongPass123")

def test_login_rejects_wrong_password(client):
    client.post("/signup", data={
        "name": "Test User",
        "email": "test@example.com",
        "password": "StrongPass123"
    })

    client.post("/logout")  
    
    response = client.post("/login", data={
        "email": "test@example.com",
        "password": "wrong-password"
    })
    assert b"Invalid email or password" in response.data

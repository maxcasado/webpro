def test_login_unauthorized():
    response = client.post("/api/v1/auth/login", data={"username": "fake", "password": "wrong"})
    assert response.status_code == 401 or response.status_code == 400

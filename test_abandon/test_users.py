def test_get_users_unauthenticated():
    response = client.get("/api/v1/users/")
    assert response.status_code == 401

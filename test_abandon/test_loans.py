def test_get_loans_admin_required():
    response = client.get("/api/v1/loans/")
    assert response.status_code == 401  # car non authentifié

def test_create_loan_unauthorized():
    response = client.post("/api/v1/loans/?user_id=1&book_id=1")
    assert response.status_code == 401

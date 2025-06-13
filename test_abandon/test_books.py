def test_get_books_unauthenticated():
    response = client.get("/api/v1/books/")
    assert response.status_code == 401  # non authentifié

def test_upload(client):
    client.post("/register")
    
    file = {"file": ("test.txt", b"test file, hello world", "text/plain")}

    response = client.post(
        "/upload/", 
        files=file)

    assert response.status_code == 200
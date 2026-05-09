import app

def test_home():
    client = app.app.test_client()
    res = client.get("/")
    assert res.status_code == 200
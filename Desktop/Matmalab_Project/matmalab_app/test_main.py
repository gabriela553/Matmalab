from fastapi.testclient import TestClient

from matmalab_app.main import app

client = TestClient(app)


def test_add_math_problem_to_db():

    response = client.post("/matmalab")
    assert response.status_code == 200



"""
For now doesn't matter
def test_get_math_problems_from_db():
    math_problem = {
        "question": "What is the sum of 4 and 10",
        "answer": "14",
    }

    response = client.post("/matmalab", json=math_problem)
    assert response.status_code == 200

    response = client.get("/matmalab")
    result = response.json()
    assert response.status_code == 200
    assert result[0]["question"] == "What is the sum of 4 and 10"
    assert result[0]["answer"] == "14"
    client.delete("/matmalab")
"""
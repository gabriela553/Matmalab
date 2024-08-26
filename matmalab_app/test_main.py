
import json
from types import SimpleNamespace
from unittest.mock import call, patch

from fastapi.testclient import TestClient

from matmalab_app.main import app

client = TestClient(app)

HTTP_OK = 200


@patch("requests.post")
@patch("matmalab_app.main.generate_math_problem")
def test_add_math_problem_to_db(generate_mock, post_mock):

    generate_mock.return_value = json.dumps({
        "question": "What is 2 multiplied by 7?",
        "answer": "14",
    })

    post_mock.return_value = SimpleNamespace(
        status_code=200,
        json=lambda: {"response": {"question": "What is 2 multiplied by 7?", "answer": "14"}},
    )

    response = client.post("/matmalab")
    response_data = response.json()
    assert response.status_code == HTTP_OK
    assert response_data["question"] == "What is 2 multiplied by 7?"
    assert response_data["answer"] == "14"
    assert post_mock.call_args_list == [
        call(
            "http://ollama:11434/api/pull",
            json={"model": "mathstral"},
        ),
        call(
            "http://ollama:11434/api/generate",
            json={
                "model": "mathstral",
                "prompt": (
                    "Generate a basic math problem and return it in a JSON "
                    "format with these keys: 'question' and 'answer'. The "
                    "'question' should describe the problem, and 'answer' "
                    'should be the solution. For example:\n{\n  "question" '
                    ': "What is 9 divided by 3?",\n  "answer": "3"\n}\n'
                ),
                "format": "json",
                "stream": False,
            },
        ),
    ]


"""
Testy bez mockowania
def test_add_math_problem_to_db():


    response = client.post("/matmalab")

    assert response.status_code == 200
    client.delete("/matmalab")
def test_get_math_problems_from_db():

    response = client.post("/matmalab")

    response = client.get("/matmalab")
    result = response.json()
    assert response.status_code == 200
    client.delete("/matmalab")

"""

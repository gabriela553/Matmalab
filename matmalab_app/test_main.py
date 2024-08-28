from types import SimpleNamespace
from unittest.mock import call, patch

from fastapi.testclient import TestClient

from matmalab_app.main import app

client = TestClient(app)

HTTP_OK = 200


@patch("requests.post")
def test_add_math_problem_to_db(post_mock):

    post_mock.return_value = SimpleNamespace(
        status_code=200,
        json=lambda: {
            "response": '{"question": "What is 2 multiplied by 7?", "answer": "14"}',
        },
    )
    response = client.post("/matmalab")
    response_data = response.json()
    assert response.status_code == HTTP_OK
    assert response_data["question"] == "What is 2 multiplied by 7?"
    assert response_data["answer"] == "14"
    assert post_mock.call_args_list == [
        call("http://ollama:11434/api/pull", json={"model": "mathstral"}, timeout=30),
        call(
            "http://ollama:11434/api/generate",
            json={
                "model": "mathstral",
                "prompt": (
                    "Generate a basic math problem and return it in a JSON format with these keys: 'question' and 'answer'.\n"
                    "    The 'question' should describe the problem, and 'answer' should be the solution. For example:\n"
                    "{\n"
                    '  "question": "What is 9 divided by 3?",\n'
                    '  "answer": "3"\n'
                    "}\n"
                ),
                "format": "json",
                "stream": False,
            },
            timeout=60,
        ),
    ]


def test_get_math_problems_from_db():

    response = client.get("/matmalab")
    assert response.status_code == HTTP_OK

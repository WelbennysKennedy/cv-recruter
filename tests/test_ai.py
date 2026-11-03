from analyze.ai import GroqClient


def test_groq_client() -> None:
    client = GroqClient()

    result = client.generate_response("Whats is the capital of France?")

    assert "Paris" in result
region = "eu-central-1"
model_name = "anthropic.claude-3-haiku-20240307-v1:0"
model_kwargs = {
    "temperature": 0.7,  # Low temperature for more deterministic, focused responses
    "max_tokens": 2048,  # Sufficient tokens for complex SQL queries and explanations
}

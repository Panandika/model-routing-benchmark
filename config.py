# Configuration for model routing
# Refer to OpenRouter Model Routing documentation: https://openrouter.ai/docs/features/model-routing

# A single list of models for OpenRouter to route through.
# When "openrouter/auto" is used, OpenRouter dynamically selects the best model
# from its internal pool based on factors like availability, performance, and cost.
# This simplifies model management on the client side as explicit model fallbacks
# are handled by OpenRouter's internal logic.
MODELS_FOR_ROUTING = [
    "openrouter/auto"
    # "anthropic/claude-3.5-sonnet",
    # "openai/gpt-4o",
    # "google/gemini-2.5-flash-preview-05-20",
    # "mistralai/mistral-7b-instruct-v0.2"
]

# Output file name for the benchmark results
OUTPUT_FILE_NAME = "questions_benchmark_results.json"

# Number of concurrent requests to make
# Adjust based on your rate limits and desired speed to avoid overwhelming the API.
CONCURRENT_REQUESTS = 5
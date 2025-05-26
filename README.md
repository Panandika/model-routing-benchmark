# OpenRouter Model Routing Benchmark Tester

This project provides a simple framework to benchmark different language models available through OpenRouter's API, specifically leveraging its model routing capabilities. It allows you to test how various models perform on a set of questions and provides insights into which models are used for different queries.

## Project Structure

- `router.py`: Contains the `OpenRouterClient` class, which is responsible for interacting with the OpenRouter API. It handles sending chat completion requests, including retry logic for rate limits and API errors. It's configured to use OpenRouter's `openrouter/auto` feature for automatic model selection.
- `main.py`: The main script that orchestrates the benchmarking process. It loads questions from a JSON file, uses the `OpenRouterClient` to get completions for each question concurrently, and saves the results and a summary to an output JSON file.
- `config.py`: Stores configuration variables such as the list of models to be used for routing (currently set to `openrouter/auto`), the output file name for results, and the number of concurrent API requests.
- `questions-benchmark-easy-hard-opt.json`: (Assumed) This file is expected to contain the benchmark questions in a JSON format. Each entry should ideally have an `id`, `difficulty`, and `question` field.

## How it Works

1.  **Configuration**: The `config.py` file defines the models OpenRouter should consider for routing. By default, it uses `"openrouter/auto"`, which delegates model selection to OpenRouter's internal algorithms based on factors like cost, performance, and availability.
2.  **API Interaction**: The `OpenRouterClient` in `router.py` makes asynchronous calls to the OpenRouter API. It includes robust error handling and retry mechanisms for common API issues like rate limits.
3.  **Benchmarking Execution**: The `main.py` script reads questions from a specified JSON file. For each question, it initiates an asynchronous call to the `OpenRouterClient`. To prevent overwhelming the API, it uses a semaphore to limit the number of concurrent requests.
4.  **Results and Summary**: After processing all questions, `main.py` compiles the results, including which model was used for each question, and a summary of model usage and any failed questions. This data is then saved to a JSON file specified in `config.py`.

## Key Features

-   **Asynchronous API Calls**: Utilizes `asyncio` and `httpx` for efficient, non-blocking API requests.
-   **Retry Mechanism**: Implements exponential backoff for `RateLimitError` and `APIConnectionError` to improve reliability.
-   **OpenRouter Auto-Routing**: Leverages OpenRouter's `openrouter/auto` model to allow OpenRouter to dynamically select the best available model, simplifying client-side model management.
-   **Concurrent Processing**: Processes multiple questions concurrently to speed up the benchmarking process.
-   **Detailed Output**: Generates a JSON file with individual question results and an overall summary of model usage.
import asyncio
import json
import logging
import os
from datetime import datetime

from router import OpenRouterClient
from config import MODELS_FOR_ROUTING, OUTPUT_FILE_NAME, CONCURRENT_REQUESTS

from dotenv import load_dotenv



# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def process_question(client: OpenRouterClient, question_data: dict, results: list, summary_data: dict):
    """
    Processes a single question by calling the OpenRouter API and stores the result.

    Args:
        client (OpenRouterClient): An instance of the OpenRouterClient to make API calls.
        question_data (dict): A dictionary containing question details (id, difficulty, question).
        results (list): A list to append the processed result entry.
        summary_data (dict): A dictionary to update with model usage and failed questions.
    """
    question_id = question_data.get("id")
    difficulty = question_data.get("difficulty")
    question_text = question_data.get("question")

    logging.info(f"Processing Question ID: {question_id} (Difficulty: {difficulty})")

    model_used, answer = await client.get_completion(prompt=question_text)

    if model_used and answer:
        result_entry = {
            "id": question_id,
            "difficulty": difficulty,
            "question": question_text,
            "model_used": model_used,
            "answer": answer
        }
        results.append(result_entry)
        
        # Update summary data
        summary_data["model_usage"][model_used] = summary_data["model_usage"].get(model_used, 0) + 1
        logging.info(f"Question ID {question_id} completed. Model used: {model_used}")
    else:
        logging.error(f"Failed to get answer for Question ID: {question_id}. Skipping.")
        summary_data["failed_questions"].append(question_id)

async def main():
    """
    Main function to run the question benchmarking process.

    It loads questions, processes them concurrently using the OpenRouterClient,
    and saves the results and a summary to a JSON file.
    """
    # Ensure the API key is set
    if not os.getenv("OPEN_ROUTER_API_KEY"):
        logging.error("OPEN_ROUTER_API_KEY environment variable not set. Please set it before running.")
        return

    # Load questions from the benchmark file
    try:
        with open("questions-benchmark.json", "r", encoding="utf-8") as f:
            questions = json.load(f)
        logging.info(f"Loaded {len(questions)} questions from questions-benchmark.json")
    except FileNotFoundError:
        logging.error("questions-benchmark.json not found. Please ensure it's in the same directory.")
        return
    except json.JSONDecodeError:
        logging.error("Error decoding questions-benchmark.json. Please check its format.")
        return

    client = OpenRouterClient()
    
    # Data structures to store results and summary
    benchmark_results = []
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_questions": len(questions),
        "models_configured_for_routing": MODELS_FOR_ROUTING,
        "model_usage": {}, # To count how many times each model was used
        "failed_questions": [],
        "routing_insights": "OpenRouter's model routing dynamically selects the best model from the configured list based on factors like availability, performance, and cost. The primary model is attempted first, with others serving as fallbacks or chosen by OpenRouter's internal logic if 'route: fallback' was used (though here we're explicitly listing fallbacks). The 'model_used' field in each result indicates which model ultimately provided the answer."
    }

    # Create a semaphore to limit concurrent tasks
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async def semaphored_process_question(question_data):
        """
        A wrapper function to process a question under the semaphore's control.
        """
        async with semaphore:
            await process_question(client, question_data, benchmark_results, summary)

    # Create tasks for all questions
    tasks = [semaphored_process_question(q) for q in questions]

    # Run tasks concurrently
    await asyncio.gather(*tasks)

    # Sort results by ID for consistent output
    benchmark_results.sort(key=lambda x: x.get("id", 0))

    # Combine results and summary into a single output structure
    final_output = {
        "results": benchmark_results,
        "summary": summary
    }

    # Save the results to a JSON file
    try:
        with open(OUTPUT_FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2)
        logging.info(f"Benchmark results saved to {OUTPUT_FILE_NAME}")
    except IOError as e:
        logging.error(f"Error saving results to file: {e}")

    logging.info("Benchmark process completed.")
    logging.info(f"Total questions processed: {summary['total_questions']}")
    logging.info(f"Models used and their counts: {summary['model_usage']}")
    if summary['failed_questions']:
        logging.warning(f"Failed to answer {len(summary['failed_questions'])} questions: {summary['failed_questions']}")

if __name__ == "__main__":
    asyncio.run(main())

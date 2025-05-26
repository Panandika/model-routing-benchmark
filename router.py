import os
import asyncio
import httpx
from openai import OpenAI, AsyncOpenAI
from openai import APIStatusError, APIConnectionError, RateLimitError
import logging

# Import the models list from config.py
from config import MODELS_FOR_ROUTING

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OpenRouterClient:
    """
    A client for interacting with the OpenRouter API.

    This class handles asynchronous requests to the OpenRouter chat completions endpoint,
    including retry logic for rate limits and API errors.
    """
    def __init__(self):
        self.client = AsyncOpenAI( # Use AsyncOpenAI here
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPEN_ROUTER_API_KEY"),
            http_client=httpx.AsyncClient(timeout=60.0) # This is correct for AsyncOpenAI
        )

    async def get_completion(self, prompt: str, retries: int = 3, delay: int = 2):
        """
        Sends a chat completion request to the OpenRouter API.

        Uses "openrouter/auto" as the model, allowing OpenRouter to handle
        internal model selection and routing. Includes retry logic with
        exponential backoff for transient errors like rate limits or connection issues.

        Args:
            prompt (str): The user's prompt for which to get a completion.
            retries (int): The maximum number of attempts to make if an error occurs.
                           Defaults to 3.
            delay (int): The initial delay in seconds before retrying.
                         This delay doubles with each subsequent retry (exponential backoff).
                         Defaults to 2.

        Returns:
            tuple[str | None, str | None]: A tuple containing the name of the model used
                                           and the generated answer. Returns (None, None)
                                           if the completion fails after all retries.
        """
        messages = [{"role": "user", "content": prompt}]
        
        # When using "openrouter/auto", OpenRouter handles the internal model selection.
        # We only need to specify "openrouter/auto" as the model.
        auto_router_model = MODELS_FOR_ROUTING[0] # This will now be "openrouter/auto"


        for attempt in range(retries):
            try:
                logging.info(f"Attempt {attempt + 1} for prompt (model: {auto_router_model})")
                
                # Use extra_body for model routing as per OpenRouter documentation
                # https://openrouter.ai/docs/features/model-routing
                completion = await self.client.chat.completions.create(
                    model=auto_router_model,
                    messages=messages,
                    # The 'extra_body' with 'models' is not used when 'model' is "openrouter/auto"
                )
                
                # OpenRouter returns the actual model used in the response
                model_used = completion.model
                answer = completion.choices[0].message.content
                logging.info(f"Successfully got completion using model: {model_used}")
                return model_used, answer
            
            except RateLimitError as e:
                logging.warning(f"Rate limit hit: {e}. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2 # Exponential backoff
            except (APIConnectionError, APIStatusError) as e:
                logging.error(f"API error: {e}. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2 # Exponential backoff
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                break # Do not retry for unexpected errors

        logging.error(f"Failed to get completion after {retries} attempts for prompt: {prompt[:50]}...")
        return None, None

from openai import OpenAI
import openai
import os


def message_openAI(conversation_history):
    """
    Arguments:
    conversation_history (list): A list of past chatgpt convasations

    Returns:
    conversation_history: A list of past chatgpt convasations or None if an error occures
    reply: A chatgpt reply message

    Description:
    Uses Chatgpt API message chatgpt
    """
    try:
        client = OpenAI(
            api_key=os.environ.get("CHATGPT_API_KEY"),
        )

        response = client.chat.completions.create(
            model=os.environ.get("CHATGPT_VERSION"), messages=[*conversation_history]
        )

        reply = response.choices[0].message.content
        return reply, conversation_history
    except openai.APIError as e:
        return f"OpenAI API returned an API Error: {e}", None
    except openai.APIConnectionError as e:
        return f"Failed to connect to OpenAI API: {e}", None
    except openai.RateLimitError as e:
        return f"OpenAI API request exceeded rate limit: {e}", None
    except Exception as e:
        return f"An error occurred: {e}", None

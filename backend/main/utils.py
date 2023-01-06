from django.conf import settings
import openai
from .models import OpenAIAnswer

def get_ai_answer(prompt, number_of_tokens=256):
    openai.api_key = settings.OPENAI_KEY

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=str(prompt),
        temperature=0.7,
        max_tokens=int(number_of_tokens),
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    output = {}
    output["text"] = response["choices"][0]["text"]
    output["id"] = response["id"]
    output["model"] = response["model"]
    output["object"] = response["object"]
    output["completion_tokens"] = response["usage"]["completion_tokens"]
    output["prompt_tokens"] = response["usage"]["prompt_tokens"]
    output["total_tokens"] = response["usage"]["total_tokens"]

    OpenAIAnswer(input_text = str(prompt), output_text = output["text"], openai_id = output["id"], openai_model = output["model"], openai_object = output["object"], completion_tokens = output["completion_tokens"], prompt_tokens = output["prompt_tokens"], total_tokens = output["total_tokens"])

    return output
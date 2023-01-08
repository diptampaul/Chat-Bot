import os
import openai

PROMPT = "portrain of a girl inside coffee"

openai.api_key = "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"

response = openai.Image.create(
    prompt=PROMPT,
    n=1,
    size="512x512",
)

print(response["data"][0]["url"])
import os
import openai

response = openai.Completion.create(
  model="text-davinci-003",
  prompt="Who are you? Are you friendly?",
  temperature=0.7,
  max_tokens=256,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

print(response)
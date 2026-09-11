from openai import OpenAI

client = OpenAI(api_key="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")
response= client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role":"system", "content":"You are a helpful assistant"}, ]
)
print(response.choices[0].message.content)
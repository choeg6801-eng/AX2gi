from openai import OpenAI

# client = OpenAI(api_key="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")
# response= client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {"role":"system", "content":"You are a helpful assistant"}, ]
# )
# print(response.choices[0].message.content)

def ask_llm(api_key,model, questions): 
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
           {"role":"system","content":"친절한 도우미"},
           {"role":"user","content": questions}
        ]
    )
    return response.choices[0].message.content,response.usage

my_api_key="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"
answer, usage= ask_llm (my_api_key, "gpt-4o-mini", "안녕하세요. 오늘 날씨가 어떤가요?")

print("Answer:", answer)
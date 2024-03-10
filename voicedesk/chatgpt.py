from openai import OpenAI
import base64
import requests
def summrize(txt):
    secret_key = ""
    if secret_key is None:
        raise ValueError("No SECRET_KEY found in environment variables")

    client = OpenAI(api_key = secret_key)
    messages = [
        {"role": "system", "content": "너는 최고의 요약도우미야"},
        {"role": "user", "content": f"[{txt}] + 이거 요약해줘"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    response_content = response.choices[0].message.content
    return response_content


def describe_image_with_openai(image_path, txt):

    api_key =""
    if api_key is None:
        raise ValueError("No SECRET_KEY found in environment variables")
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": f"[{txt}]이게 이미지에 있는 글 내용인데 이거 참고해서, 이 책에 있는 표, 그래프, 그림등의 자료를 정확하게 특수문자 쓰지 말고 글로 설명해줘"
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}"
                }
              }
            ]
          }
        ],
        "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    content = response.json()['choices'][0]['message']['content']

    return content
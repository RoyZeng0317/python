import requests

response = requests.get(
    "https://dummyjson.com/comments"
)
reply = requests.post(
    "https://dummyjson.com/comments/add",
    headers={"Content-Type": "application/json"},
    json={"body": "這期看懂了", "postId": 3, "userId": 5},
)
data = response.json()
print(data)
print(reply.json())

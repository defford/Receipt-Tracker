from openai import OpenAI
import os
import base64
import csv
import json

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

client = OpenAI()

images = []
imageEncodings = []

image_folder = "images"
for filename in os.listdir(image_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        images.append(os.path.join(image_folder, filename))

for image in images:
    image_path = f"{image}"

    base64_image = encode_image(image_path)
    imageEncodings.append(base64_image)

for image in imageEncodings:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant specialized in retrieving and analyzing data from photos of receipts."},
            {
                "role": "user",
                "content": [
                        {
            "type": "text",
            "text": """Retrieve the date of purchase, the total amount for this receipt, name the company it was purchased from, and provide a short summary of the items purchased. 
                        Output into the following format:
                        {
                        date: MM/DD/YYYY
                        total: $float
                        store: str
                        items: {{itemName:str : price: $float}}
                        }"""
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image}"
            }
            }
                ]
            }
        ]
    )

    response = completion.choices[0].message.content

    if response.find("```") != -1:
        response = response.split("```")
    if response[1].find("json") != -1:
        response = response[1].strip("json")
# Extract values from response

    print(response)
    response = json.loads(response)
    date = response['date']
    total = response['total']
    store = response['store']
    items = response['items']

    # Write values to CSV
    with open("receipts.csv", "a") as r:
        writer = csv.writer(r)
        writer.writerow([date, total, store, items])
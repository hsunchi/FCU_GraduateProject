def read(x):
    import io
    import os
    from google.cloud import vision
    from google.cloud.vision import types
    client = vision.ImageAnnotatorClient.from_service_account_json("C:\\inetpub\\wwwroot\\test-vision-api-f989a5d4665e.json")

    with io.open(x, 'rb') as image_file:
         content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    text = texts[0].description  #text 是圖片裡面的文字內容
    return text

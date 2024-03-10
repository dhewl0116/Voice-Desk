import os
from google.cloud import vision
def detect_text(path):
    """Detects text in the file."""
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join("/home/jimin/voicedesk/google_api.json")
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        full_text_annotation = response.full_text_annotation
        if full_text_annotation:
            full_text = full_text_annotation.text
        else:
            return "No text found in the image."
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        full_text = full_text.replace("\n", "")
        return full_text
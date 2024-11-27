import os
from flask import Flask, request, jsonify
from PIL import Image
import psd_tools

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    name = request.form['name']
    photo = request.files['photo']
    photo_path = os.path.join('static', photo.filename)
    photo.save(photo_path)

    psd_path = os.path.join('static', 'your_image.psd')
    psd = psd_tools.PSDImage.open(psd_path)

    # Replace text
    for layer in psd.descendants():
        if layer.kind == 'type' and 'name_layer' in layer.name:
            layer.text = name

    # Replace image
    for layer in psd.descendants():
        if layer.kind == 'smartobject' and 'photo_layer' in layer.name:
            with Image.open(photo_path) as img:
                img = img.resize(layer.size, Image.ANTIALIAS)
                layer.image = psd_tools.user_api.pil_io.encode_as_PIL(img)

    # Save as JPG
    jpg_output = os.path.join('static', 'output.jpg')
    psd.composite().save(jpg_output)

    response = {'success': True, 'imagePath': jpg_output}
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)

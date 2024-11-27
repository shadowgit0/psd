import os
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    name = request.form['name']
    photo = request.files['photo']
    photo_path = os.path.join('static', photo.filename)
    photo.save(photo_path)

    # Update PSD File using Photoshop Script
    psd_script = f"""
    var psdFile = new File("{os.path.abspath('static/your_image.psd')}");
    var jpgOutput = "{os.path.abspath('static')}/output.jpg";
    var nameText = "{name}";
    var photoFile = new File("{os.path.abspath(photo_path)}");

    app.open(psdFile);

    // Update text layer
    var textLayer = app.activeDocument.artLayers.getByName("name_layer");
    textLayer.textItem.contents = nameText;

    // Update photo layer
    var photoLayer = app.activeDocument.artLayers.getByName("photo_layer");
    app.open(photoFile);
    var photoDoc = app.activeDocument;
    photoDoc.selection.selectAll();
    photoDoc.selection.copy();
    app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
    app.activeDocument = app.documents.getByName("your_image.psd");
    photoLayer.kind = LayerKind.SMARTOBJECT;
    photoLayer.smartObject.resizeContent();
    app.activeDocument.paste();

    // Save as JPG
    var jpgSaveOptions = new JPEGSaveOptions();
    jpgSaveOptions.quality = 12;
    app.activeDocument.saveAs(new File(jpgOutput), jpgSaveOptions, true, Extension.LOWERCASE);
    app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
    """.strip()

    with open('update_psd.jsx', 'w') as f:
        f.write(psd_script)

    subprocess.run(['osascript', '-e', 'tell application "Adobe Photoshop" to do javascript file POSIX file "{os.path.abspath("update_psd.jsx")}"'])

    response = {'success': True, 'imagePath': f'static/output.jpg'}
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)

import io
import qrcode
from flask import Flask, request, send_file, jsonify, render_template_string

app = Flask(__name__)

# UI route to display the form
@app.route('/')
def index():
    # Using render_template_string for simplicity.
    # In a larger project, you might use separate HTML template files.
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>QR Code Generator</title>
    </head>
    <body>
        <h1>QR Code Generator</h1>
        <form id="qrForm">
            <input type="text" id="urlInput" placeholder="Enter URL here" required style="width:300px;">
            <button type="submit">Generate QR Code</button>
        </form>
        <br>
        <div id="qrContainer" style="display: none;">
            <h2>Your QR Code:</h2>
            <img id="qrImage" src="" alt="QR Code">
        </div>
        <script>
            document.getElementById('qrForm').addEventListener('submit', function(event) {
                event.preventDefault();
                const url = document.getElementById('urlInput').value;
                if(url) {
                    // Update the image src with the /generate endpoint and the URL as query parameter
                    const qrImage = document.getElementById('qrImage');
                    qrImage.src = '/generate?url=' + encodeURIComponent(url);
                    document.getElementById('qrContainer').style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    ''')

# QR generation endpoint (same as before, with customization options if needed)
@app.route('/generate', methods=['GET'])
def generate_qr():
    # Extract URL from query parameters
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL parameter'}), 400

    # Optional customization parameters (using defaults)
    fill_color = request.args.get('fill_color', 'black')
    back_color = request.args.get('back_color', 'white')
    try:
        box_size = int(request.args.get('box_size', 10))
        border = int(request.args.get('border', 4))
    except ValueError:
        return jsonify({'error': 'box_size and border must be integers'}), 400

    error_correction_param = request.args.get('error_correction', 'H').upper()
    error_correction_levels = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H,
    }
    error_correction = error_correction_levels.get(error_correction_param, qrcode.constants.ERROR_CORRECT_H)

    # Create the QR Code instance with the provided customization options
    qr = qrcode.QRCode(
        version=1,
        error_correction=error_correction,
        box_size=box_size,
        border=border
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create the QR code image
    img = qr.make_image(fill_color=fill_color, back_color=back_color)

    # Save the image to an in-memory bytes buffer
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    # Return the image as a response
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)

import io
import qrcode
from flask import Flask, request, send_file, jsonify, render_template_string
import webbrowser
from threading import Timer

app = Flask(__name__)

# UI route to display the form with a nicer GUI using Bootstrap
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>QR Code Generator</title>
      <!-- Bootstrap CSS -->
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
      <style>
        body { background-color: #f8f9fa; }
        .container { max-width: 600px; margin-top: 50px; }
        .qr-code { margin-top: 20px; }
      </style>
    </head>
    <body>
      <div class="container text-center">
        <h1 class="mb-4">QR Code Generator</h1>
        <form id="qrForm" class="mb-4">
          <div class="input-group">
            <input type="text" id="urlInput" class="form-control" placeholder="Enter URL here" required>
            <button type="submit" class="btn btn-primary">Generate QR Code</button>
          </div>
        </form>
        <div id="qrContainer" class="qr-code" style="display: none;">
          <h2>Your QR Code:</h2>
          <img id="qrImage" src="" alt="QR Code" class="img-fluid">
        </div>
      </div>
      <!-- JavaScript to handle form submission -->
      <script>
        document.getElementById('qrForm').addEventListener('submit', function(event) {
            event.preventDefault();
            const url = document.getElementById('urlInput').value;
            if(url) {
                const qrImage = document.getElementById('qrImage');
                qrImage.src = '/generate?url=' + encodeURIComponent(url);
                document.getElementById('qrContainer').style.display = 'block';
            }
        });
      </script>
      <!-- Bootstrap Bundle with Popper -->
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''')

# QR generation endpoint
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
    # Function to open the browser after a short delay
    def open_browser():
        webbrowser.open("http://127.0.0.1:5000")
    
    # Start a timer to open the browser 1 second after the server starts
    Timer(1, open_browser).start()
    
    app.run(debug=True)

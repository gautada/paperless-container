import datetime
import os

from flask import Flask
from flask import request

app = Flask(__name__)

# from fpdf import FPDF
# pdf = FPDF()

try:
    from PIL import Image
except ImportError:
    import Image

# requires apt-get install tesseract-ocr
import pytesseract

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

import ocrmypdf

import PyPDF2

@app.route('/')
def hello_world():
    return 'Hello, World!'

ROOT = "/home/paperless/cache"
# @to-do: Need to create a unique folder in uploads to hold scans    
# @to-do: after post redirect to get
# @to-do: add get filters
@app.route('/pdf', methods=['GET', 'POST'])
def create_pdf():
    path = None
    while path is None:
        now = datetime.datetime.now()
        key = "%s" % str(now)
        path = "%s/%s" % (ROOT, key)
        if not os.path.isdir(path):
            os.mkdir(path)
        else:
            path = None

    if request.method == 'POST':
        scans = request.files.getlist("scans[]")
        images = []
        txt = ""
        i = 0
        for scan in scans:
            fimg = '%s/image-%05d' % (path, i)
            scan.save(fimg)
            img = Image.open(fimg)
            txt = "%s\n%s" % (txt, pytesseract.image_to_string(img))
            images.append(img)
            i += 1
        pdf = "%s/combined.pdf" % path
        if 1 == len(images):
            images[0].save(pdf, "PDF", resolution=100.0, save_all=True)
        else:
            images[0].save(pdf, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
        ocr = "%s/ocr.pdf" % path
        ocrmypdf.ocr(pdf, ocr, deskew=True, rotate_pages=True)
        raw = open("%s/raw" % path, "w")
        raw.write(txt)
        raw.close()
    return "OK"

@app.route('/ocr', methods=['GET', 'POST'])
def ocr():
    fpdf = ""
    filename = "test.pdf"
    root = '/home/python/src/'
    if request.method == 'POST':
        f = request.files['pdf']
        filename = f.filename
        fpdf = '%s/pdfs/%s' % (root, filename)
        f.save(fpdf)
    elif request.method == 'GET':
        return "Meh"
    else:
        return "NOT POST"
    output = '%s/ocrs/ocr-%s' % (root, filename)
    print(output)
    ocrmypdf.ocr(fpdf, output, deskew=True, rotate_pages=True)
    return 'OK'


@app.route('/name', methods=['GET', 'POST'])
def name_pdf():
    if request.method == 'POST':
        f = request.files['pdf']
        pdf = PyPDF2.PdfFileReader(f)
        pages = pdf.numPages
        txt = ""
        for p in range(pages):
            print("page: %s" % p)
            page = pdf.getPage(p)
            txt = "%s\n\n%s" % (txt, page.extractText())
        print(txt)
        return txt
    elif request.method == 'GET':
        return "Meh"
    else:
        return "NOT POST"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

# Usage - $ curl -F 'the_file=@requirements.txt' http://127.0.0.1:8080/upload
# curl -F 'scans[]=@requirements.txt' -F 'scans[]=@scans.py' http://127.0.0.1:8080/upload
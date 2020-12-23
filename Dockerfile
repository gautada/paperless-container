FROM development:build

EXPOSE 8080

RUN useradd -ms /bin/bash paperless \
 && echo 'paperless:paperless' | chpasswd \
 && usermod -aG sudo paperless \
 && ln -s /opt/paperless-data /home/paperless/data

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ghostscript qpdf tesseract-ocr pngquant unpaper libtesseract-dev

RUN git clone https://github.com/agl/jbig2enc jbig2enc \
 && cd /jbig2enc \
 && ./autogen.sh \
 && ./configure \
 && make \
 && make install 

USER paperless
WORKDIR /home/paperless

COPY requirements.txt /home/paperless/requirements.txt 
COPY paperless.py /home/paperless/paperless.py

RUN  mkdir -p /home/paperless/cache \
 && pip3 install wheel \
 && echo "export PATH=$PATH:/home/paperless/.local/bin" >> /home/paperless/bash.bashrc \
 && . /home/paperless/bash.bashrc \
 && pip3 install -r /home/paperless/requirements.txt 

CMD ["python3", "paperless.py"]

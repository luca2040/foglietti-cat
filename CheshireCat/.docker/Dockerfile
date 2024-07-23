FROM ghcr.io/cheshire-cat-ai/core:latest

RUN apt-get update && \
    apt-get install -y default-jre tesseract-ocr libtesseract-dev

RUN cd /usr/share/tesseract-ocr/4.00/tessdata && \
    curl -H 'Accept: application/vnd.github.v3.raw' -O -L https://api.github.com/repos/tesseract-ocr/tessdata/contents/ita.traineddata

VOLUME [ "/app/cat/data/models" ]

COPY plugins/cc_ask_stella/requirements.txt /app/cat/plugins/cc_ask_stella/requirements.txt
RUN pip install -r /app/cat/plugins/cc_ask_stella/requirements.txt

COPY .docker/metadata.json /app/cat/data/metadata.json
COPY wordlist/wordlist.txt /app/cat/wordlist/wordlist.txt
COPY plugins/cc_ask_stella /app/cat/plugins/cc_ask_stella

CMD ["python3", "-m", "cat.main"]

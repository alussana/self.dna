FROM debian:bookworm-20241016-slim

RUN apt-get update && \
        apt-get upgrade -y && \
        apt-get install -y wget zip python3

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN wget -O get-pip.py "https://bootstrap.pypa.io/get-pip.py"
RUN python get-pip.py --break-system-packages

RUN pip install --break-system-package dash dash-bootstrap-components pysam pandas

COPY app app

WORKDIR /app/

ENTRYPOINT [ "./app.py" ]
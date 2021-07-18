FROM python:3.8.1

COPY requirements.txt /app/

RUN python -m venv /app/venv

RUN /app/venv/bin/python -m pip install --upgrade pip && \
    /app/venv/bin/python -m pip install -r /app/requirements.txt

COPY src /app/src

WORKDIR /app/src

EXPOSE 5000

ENTRYPOINT [ "/app/venv/bin/python", "main.py" ]

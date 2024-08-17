FROM python:3.12

WORKDIR /root

COPY requirements.txt ./
ENV PYTHONPATH=/root
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install "uvicorn[standard]"

COPY matmalab_app /root/matmalab_app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
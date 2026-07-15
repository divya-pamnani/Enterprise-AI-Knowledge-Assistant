FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y curl

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ollama serve & \
    sleep 10 && \
    ollama pull llama3.2 && \
    streamlit run app.py --server.port=8501 --server.address=0.0.0.0
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copia dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY app ./app
COPY tests ./tests

# Por padrão, o container executa o main (ENTRYPOINT).
# Você passa os argumentos no docker run.
ENTRYPOINT ["python", "-m", "app.main"]

# Dica: se rodar sem args, vai mostrar erro de args obrigatórios.

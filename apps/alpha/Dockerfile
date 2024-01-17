FROM python:3.9

WORKDIR /app

COPY ./ /app

RUN pip install fastapi uvicorn httpx

ENV BETA_URL="http://beta:8000"
ENV CHARLIE_URL="http://charlie:8000"

HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

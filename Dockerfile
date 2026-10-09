FROM python:3.12-slim

WORKDIR /app

ARG BUILD_NUMBER=local
ARG GIT_COMMIT=unknown
ARG BRANCH_NAME=unknown

ENV BUILD_NUMBER=${BUILD_NUMBER}
ENV GIT_COMMIT=${GIT_COMMIT}
ENV BRANCH_NAME=${BRANCH_NAME}
ENV APP_VERSION=${BUILD_NUMBER}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY tests ./tests

EXPOSE 8080

CMD ["python", "app.py"]
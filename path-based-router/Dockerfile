FROM nginx:alpine

COPY --from=golang:1.17-alpine /usr/local/go/ /usr/local/go/
ENV PATH="/usr/local/go/bin:${PATH}"

RUN apk update && apk add build-base

RUN mkdir -p /app
WORKDIR /app
COPY . /app

RUN go build -o main && chmod 777 main && cp main /docker-entrypoint.d/ && cat "/docker-entrypoint.d/main" >> /docker-entrypoint.d/setup.sh && chmod 777 /docker-entrypoint.d/setup.sh

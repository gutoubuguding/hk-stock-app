# syntax=docker/dockerfile:1

FROM maven:3.9.9-eclipse-temurin-17 AS build
WORKDIR /build
COPY backend/pom.xml ./pom.xml
RUN mvn -q -DskipTests dependency:go-offline
COPY backend/src ./src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:17-jre-jammy
WORKDIR /app

# The Spring scheduler calls Python sync scripts. Keep Python inside the
# backend image so `docker compose up -d` works without host Python.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/local/bin/python

COPY requirements-sync.txt /app/scripts/requirements-sync.txt
RUN pip3 install --no-cache-dir -r /app/scripts/requirements-sync.txt

COPY --from=build /build/target/*.jar /app/app.jar
COPY sync_daily_kline.py sync_ipo_futu.py sync_market_overview.py sync_calendar_aastocks.py sync_ipo_detail_aastocks.py sync_ipo_kline_metrics.py update_ipo_metrics.py /app/scripts/

ENV SERVER_PORT=8080 \
    SERVER_ADDRESS=0.0.0.0 \
    PYTHON_EXECUTABLE=python3 \
    APP_SCRIPT_ROOT=/app/scripts

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]

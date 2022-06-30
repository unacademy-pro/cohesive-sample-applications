FROM maven:3.8.6-openjdk-8-slim as builder

# Set up args
ARG build_libs

# Install packages
RUN apt-get update && apt-get install -y --no-install-recommends git

# Copy the code
RUN mkdir -p /app
COPY . /app

# Build the libraries
WORKDIR /app/libraries/utils
RUN if [ "$build_libs" = "true" ]; then mvn clean install; else echo "Skipping library build"; fi
RUN if [ "$build_libs" = "true" ]; then git clone https://github.com/jenkins-docs/simple-java-maven-app.git && cd simple-java-maven-app && mvn clean install; else echo "Skipping library build"; fi

# Build the application
WORKDIR /app
RUN mvn clean install

FROM openjdk:8-jdk-alpine

# Set up args
ARG app_name

# Copy the jar file
COPY --from=builder /app/target/*.jar .

# Run the jar
CMD ["java", "-DappName=$app_name", "-jar", "spring-boot-application-1.0-SNAPSHOT.jar"]
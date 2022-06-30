# Spring Boot sample app (using Maven)

This app shows how to set up a Dockerfile for a Spring Boot application and also demonstrates the following:

* How to send arguments to Java app
* How to send parameters to build
* How to do builds for other modules within the same repository
* How to do builds for other modules with source code on Git repository

# Build and Run

## Without Docker

```shell
cd libraries/utils
mvn clean install
cd ../..
mvn clean install
java -DappName=SBA -jar target/spring-boot-application-1.0-SNAPSHOT.jar
```

## With Docker

```shell
docker build . -t sba:latest --build-arg build_libs=true --build-arg app_name=SBA
docker run -d -p 8081:8080 sba:latest
```
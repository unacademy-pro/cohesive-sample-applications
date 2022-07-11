package main

import (
	"flag"
	"log"
	"os"
	"strings"
	"text/template"
)

const (
	ConfigPath        = "/etc/nginx/nginx.conf"
)

func main() {
	setupFlags()
	run()
}

func setupFlags() {
	flag.Parse()
}

func run() {
	envVars := parseEnv()
	renderConfig(envVars)
	log.Printf("Successfully generated routing config")
}

func parseEnv() map[string]string {
	rawEnvVars := os.Environ()
	envVars := make(map[string]string)
	for _, r := range rawEnvVars {
		parts := strings.SplitN(r, "=", 2)
		envVars[parts[0]] = parts[1]
	}
	return envVars
}

func renderConfig(env map[string]string) {
	tmpl, err := template.New("nginx.conf.tmpl").ParseFiles("nginx.conf.tmpl")
	if err != nil {
		log.Fatalf("could not read template: %s", err)
	}

	file, err := os.Create(ConfigPath)
	if err != nil {
		log.Fatalf("could not create config file: %s", err)
	}

	err = tmpl.Execute(file, env)
	if err != nil {
		file.Close()
		log.Fatalf("could not render template: %s", err)
	}

	err = file.Close()
	if err != nil {
		log.Printf("could not close config file: %s", err)
	}
}

package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
	"text/template"
)

const (
	ConfigPath        = "/etc/nginx/nginx.conf"
	PathPrefix        = "ROUTER_PATH_"
	DestinationPrefix = "ROUTER_DESTINATION_"
	RewriteHostPrefix = "ROUTER_REWRITE_HOST_"
)

type renderCtx struct {
	Routes   map[string]string
	Rewrites map[string]bool
}

func main() {
	setupFlags()
	run()
}

func setupFlags() {
	flag.Parse()
}

func run() {
	envVars := parseEnv()
	routes, rewrites := parseRoutes(envVars)
	renderConfig(routes, rewrites)
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

func parseRoutes(envVars map[string]string) (map[string]string, map[string]bool) {
	routes := make(map[string]string)
	rewrites := make(map[string]bool)
	for k, v := range envVars {
		if strings.HasPrefix(k, PathPrefix) {
			path := v
			entry := strings.Replace(k, PathPrefix, "", 1)

			// Find the destination
			destinationEnvVar := fmt.Sprintf("%s%s", DestinationPrefix, entry)
			destination := envVars[destinationEnvVar]
			if destination == "" {
				log.Fatalf("destination cannot be empty: %s", destinationEnvVar)
			}

			// Check if Host header rewrite is required
			var rewrite bool
			rewriteEnvVar := fmt.Sprintf("%s%s", RewriteHostPrefix, entry)
			rewriteValue := envVars[rewriteEnvVar]
			if rewriteValue == "true" {
				rewrite = true
			}

			_, ok := routes[path]
			if ok {
				log.Fatalf("path cannot be duplicate: %s", path)
			}
			routes[path] = destination
			rewrites[path] = rewrite
		}
	}
	return routes, rewrites
}

func renderConfig(routes map[string]string, rewrites map[string]bool) {
	tmpl, err := template.New("nginx.conf.tmpl").ParseFiles("nginx.conf.tmpl")
	if err != nil {
		log.Fatalf("could not read template: %s", err)
	}

	file, err := os.Create(ConfigPath)
	if err != nil {
		log.Fatalf("could not create config file: %s", err)
	}

	ctx := renderCtx{
		Routes:   routes,
		Rewrites: rewrites,
	}
	err = tmpl.Execute(file, ctx)
	if err != nil {
		file.Close()
		log.Fatalf("could not render template: %s", err)
	}

	err = file.Close()
	if err != nil {
		log.Printf("could not close config file: %s", err)
	}
}

Notes App - End-to-End DevOps Project

This project evolved through 5 Phases to demonstrate the complete DevOps lifecycle on AWS. 
  1. Phase 1 - Linux
   
    - Created dedicated user and system user following the Principle of Least Privilege
    - Configured SSH key-based authentication, disabled root login and password auth
    - Installed and configured Nginx as a reverse proxy, MariaDB, Python, and Gunicorn
    - Deployed the Flask app as a systemd service for automatic restarts on reboot
    - Wrote a bash backup script scheduled via cron for daily database snapshots

  2. Phase 2 - GIT
   
    - Initialised a bare repository on the server (/opt/git/devops-project.git)
    - Wrote a post-receive hook that automatically pulls code and restarts the Flask service on every git push
    - Configured a second Git remote (production) pointing directly at the EC2 server
    - Secured passwordless sudo for the deploy user scoped to only the systemctl restart command

  3. Phase 3 - Docker

    -  Wrote a Dockerfile for the Flask web UI and a separate Dockerfile.api for the REST API
    - Built a docker-compose.yml orchestrating five containers: Flask web, Flask API, Nginx, MariaDB, Redis
    - Implemented a Redis caching layer on the API with cache invalidation on writes
    -  Configured a Docker named volume for MariaDB data persistence across container restarts  
    - Used Docker bridge networking with service-name DNS resolution between containers
     
  4. Phase 4 - Kubernetes

Create following manifest files:

     1. namespace.yaml-Isolated notes-app namespace

     2.configmap.yaml-Non-sensitive config (hostnames, DB name)

     3.secret.yaml-Base64-encoded passwords

     4.mariadb-pvc.yaml-1Gi PersistentVolumeClaim for database storage

     5.mariadb.yaml-Deployment + ClusterIP Service

     6.redis.yaml-Deployment + ClusterIP Service

     7.flask-web.yaml-Deployment + ClusterIP Service

     8.flask-api.yaml-Deployment + ClusterIP Service

     9.nginx-config.yaml-ConfigMap holding Nginx routing config

     10.nginx.yaml-Deployment + NodePort Service (port 30362)
     
  5. Phase 5 - CICD

git push origin main
        │
        ▼
Job 1: build-and-push
  → Build notes-web Docker image
  → Build notes-api Docker image
  → Push both to Docker Hub (tagged with git SHA + latest)
        │
        │ needs: build-and-push
        ▼
Job 2: deploy
  → SSH into K8s server
  → kubectl set image (web + API deployments)
  → kubectl rollout status (waits for healthy pods)



Repository Structure

<img width="345" height="614" alt="image" src="https://github.com/user-attachments/assets/1b534cbd-e954-4dc3-96f6-0f1f9e92e3c8" />


Things I learned extra:
    
    1. Microservices
    2. API services
    3. RestAPI
    4. Python Virtual Environment
    5. Redis Cache
      

pipeline {
    agent { label 'scott' }

    stages {

        stage("Code") {
            steps {
                echo "Cloning the repository"
                git url: "https://github.com/prasadpingale24/task-manager-backend.git", branch: "main"
                echo "Code cloned successfully"
            }
        }

        stage("Build") {
            steps {
                echo "Building the Docker image"
                sh 'docker build -t task-manager-backend:latest .'
                echo "Docker image built successfully"
            }
        }

        stage("Test") {
            steps {
                echo "Starting Postgres test container"
                sh '''
                    docker rm -f pg_test || true
                    docker run -d \
                        --name pg_test \
                        -e POSTGRES_USER=postgres \
                        -e POSTGRES_PASSWORD=postgres \
                        -e POSTGRES_DB=task_manager_test \
                        -p 5433:5432 \
                        postgres:15-alpine
                '''

                echo "Waiting for Postgres to be ready"
                sh '''
                    for i in $(seq 1 15); do
                        docker exec pg_test pg_isready -U postgres && break
                        echo "Waiting... attempt $i"
                        sleep 2
                    done
                '''

                echo "Running backend tests"
                sh '''
                    docker run --rm \
                    --name backend_test \
                    --link pg_test:postgres \
                    -e POSTGRES_HOST=postgres \
                    -e POSTGRES_PORT=5432 \
                    -e POSTGRES_USER=postgres \
                    -e POSTGRES_PASSWORD=postgres \
                    -e POSTGRES_DB=task_manager_test \
                    -e SECRET_KEY="jenkins-ci-test-key" \
                    -e ENVIRONMENT="test" \
                    -e PYTHONPATH=/app \
                    -v $(pwd):/app \
                    -w /app \
                    python:3.13-slim \
                    sh -c "pip install uv --quiet && \
                           uv sync --group dev && \
                           uv run pytest tests/ \
                               --junitxml=results.xml \
                               --cov=app \
                               --cov-report=xml \
                               -v"
                '''

            }
            post {
                always {
                    echo "Stopping Postgres test container"
                    sh 'docker rm -f pg_test || true'
                    junit allowEmptyResults: true, testResults: 'results.xml'
                }
                failure {
                    echo "Backend tests FAILED — check the report above"
                }
            }
        }

        stage("Push to DockerHub") {
            steps {
                echo "Pushing the image to Docker Hub"
                withCredentials([usernamePassword(credentialsId: 'dockerHubCred', 
                                               passwordVariable: 'dockerHubPass', 
                                               usernameVariable: 'dockerHubUser')]) {
                    sh 'echo "$dockerHubPass" | docker login -u "$dockerHubUser" --password-stdin'
                    sh "docker image tag task-manager-backend:latest ${dockerHubUser}/task-manager-backend:latest"
                    sh "docker push ${dockerHubUser}/task-manager-backend:latest"
                }
            }
        }
        stage("Deploy") {
            steps {
                echo "Deploying the application with Docker Compose"
                // Using Docker Compose ensures the 'db' and 'backend' are in the same network
                // Jenkins environment variables are automatically picked up by Docker Compose
                sh """
                    docker compose down --remove-orphans
                    docker compose up -d
                """
                
                echo "Waiting for backend to start..."
                sh "sleep 10 && docker compose ps"
            }
        }

    }
}

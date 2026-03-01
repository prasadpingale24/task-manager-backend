pipeline {
    agent { label 'scott' }

    environment {
        DOCKER_USER = "prasadpingale24"
        IMAGE_NAME = "task-manager-backend"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Environment') {
            steps {
                prepareEnv()
            }
        }

        stage('Build Image') {
            steps {
                buildImage(DOCKER_USER, IMAGE_NAME)
            }
        }

        stage('Push Image') {
            steps {
                pushImage(DOCKER_USER, IMAGE_NAME)
            }
        }

        stage('Deploy') {
            steps {
                deployBackend()
            }
        }
    }
}
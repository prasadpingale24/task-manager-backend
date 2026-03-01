pipeline {
    agent { label 'scott' }

    environment {
        DOCKER_USER = "prasadpingale24"
        IMAGE_NAME = "task-manager-backend"
        IMAGE_TAG = "latest"
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
                docker_build(DOCKER_USER, IMAGE_NAME, IMAGE_TAG)
            }
        }

        stage('Push Image') {
            steps {
                docker_push(IMAGE_NAME, IMAGE_TAG)
            }
        }

        stage('Deploy') {
            steps {
                docker_deploy()
            }
        }
    }
}
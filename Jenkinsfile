@Library("Shared") _

def DOCKER_USER = "prasadpingale24"
def IMAGE_NAME = "task-manager-backend"
def IMAGE_TAG = "latest"

def projectConfig = [
    projectName: 'Backend',
    vars: [
        'POSTGRES_USER': 'postgres',
        'POSTGRES_DB': 'task_manager',
        'POSTGRES_HOST': 'db',
        'POSTGRES_PORT': '5432',
        'ALGORITHM': 'HS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '1440',
        'BACKEND_CORS_ORIGINS': '["https://crewflow.pspworks.cloud", "http://localhost:3000", "http://localhost:5173"]',
        'PROJECT_NAME': 'Team Tasks Manager',
        'BACKEND_BIND_ADDR': '127.0.0.1',
        'BACKEND_PORT': '8000',
        'IMAGE_TAG': "${IMAGE_TAG}",
        'ENVIRONMENT': 'development'
    ],
    secrets: [
        [id: 'taskManagerBackendSecretKey', var: 'SECRET_KEY'],
        [id: 'taskManagerBackendPassword', var: 'POSTGRES_PASSWORD']
    ]
]

pipeline {

    agent { label 'scott' }

    stages {

        stage('Prepare Environment') {
            steps {
                prepareEnv(projectConfig)
            }
        }

        stage('Test') {
            steps {
                docker_test('backend')
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

        stage('Health Check') {
            steps {
                healthCheck(url: "http://127.0.0.1:8000/health", maxRetries: 12, retryInterval: 10)
            }
        }
    }
}

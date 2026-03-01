@Library("Shared") _
pipeline {
    agent { label 'scott' }

    stages {

        stage("Hello"){
            steps{
                script{
                    hello()
                }
            }
        }
        stage("Code") {
            steps {
                script{
                    clone("https://github.com/prasadpingale24/task-manager-backend.git", "main")
                }
            }
        }

        stage("Build") {
            steps {
                script{
                    docker_build("task-manager-backend", "latest", "prasadpingale24")
                }
            }
        }

        stage("Test") {
            steps {
                script {
                    docker_test("task-manager-backend")
                }
            }
            post {
                always {
                    echo "Cleaning up Postgres test container"
                    sh 'docker rm -f pg_test || true'
                    junit allowEmptyResults: true, testResults: 'results.xml'
                }
                failure {
                    echo "Backend tests FAILED — check report"
                }
            }
        }

         stage("Push to DockerHub") {
            steps {
                script{
                    docker_push("task-manager-backend", "latest")
                }
            }
        }
        
        stage("Deploy") {
            steps {
                script{
                    docker_deploy()
                }
            }
        }

    }
}

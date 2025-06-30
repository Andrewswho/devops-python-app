pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "devops-python-app"
        CONTAINER_NAME = "python-app-container"
        APP_PORT = "5000"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Pulling code from GitHub...'
                checkout scm
            }
        }
        
        stage('Stop Old Container') {
            steps {
                script {
                    echo 'Stopping and removing old container if exists...'
                    sh '''
                        if docker ps -q -f name=${CONTAINER_NAME}; then
                            echo "Stopping running container..."
                            docker stop ${CONTAINER_NAME} || true
                        fi
                        
                        if docker ps -aq -f name=${CONTAINER_NAME}; then
                            echo "Removing old container..."
                            docker rm ${CONTAINER_NAME} || true
                        fi
                        
                        echo "Cleanup completed"
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image...'
                    sh "docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} ."
                    sh "docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest"
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    echo 'Deploying new container...'
                    sh '''
                        docker run -d \
                            --name ${CONTAINER_NAME} \
                            -p ${APP_PORT}:${APP_PORT} \
                            ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    echo 'Checking application health...'
                    sleep 10
                    sh 'curl -f http://localhost:5000/health || exit 1'
                    echo 'Application is healthy!'
                }
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
            sh 'docker logs ${CONTAINER_NAME} || true'
        }
    }
}

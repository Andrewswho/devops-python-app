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
        
        stage('Clean Docker Resources') {
            steps {
                script {
                    echo 'Cleaning up Docker resources to free memory...'
                    sh '''
                        # Remove unused containers, networks, images
                        docker system prune -f --volumes || true
                        
                        # Remove old versions of our image (keep only latest 2)
                        docker images ${DOCKER_IMAGE} --format "table {{.Repository}}:{{.Tag}}" | tail -n +3 | xargs -r docker rmi || true
                    '''
                }
            }
        }
        
        stage('Stop Old Container') {
            steps {
                script {
                    echo 'Stopping and removing old container if exists...'
                    sh '''
                        # Check if container is running and stop it
                        if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
                            echo "Stopping running container..."
                            docker stop ${CONTAINER_NAME}
                        else
                            echo "No running container found"
                        fi
                        
                        # Check if container exists (stopped) and remove it
                        if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
                            echo "Removing old container..."
                            docker rm ${CONTAINER_NAME}
                        else
                            echo "No container to remove"
                        fi
                        
                        echo "Cleanup completed"
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image with memory limits for t3.micro...'
                    sh """
                        docker build \\
                            --memory=400m \\
                            --memory-swap=800m \\
                            -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                    """
                    sh "docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest"
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    echo 'Deploying new container with memory limits...'
                    sh '''
                        docker run -d \\
                            --name ${CONTAINER_NAME} \\
                            --memory=300m \\
                            -p ${APP_PORT}:${APP_PORT} \\
                            ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    echo 'Checking application health...'
                    sleep 15  // Più tempo per container con risorse limitate
                    sh '''
                        # Verifica che il container sia in esecuzione
                        if ! docker ps | grep ${CONTAINER_NAME}; then
                            echo "Container not running!"
                            docker logs ${CONTAINER_NAME}
                            exit 1
                        fi
                        
                        # Test health endpoint
                        curl -f http://localhost:5000/health || exit 1
                        echo "Application is healthy!"
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo "Application available at: http://YOUR_EC2_IP:5000"
        }
        failure {
            echo '❌ Pipeline failed!'
            script {
                sh '''
                    echo "=== Container Logs ==="
                    docker logs ${CONTAINER_NAME} || true
                    
                    echo "=== System Resources ==="
                    free -h || true
                    df -h || true
                    
                    echo "=== Docker Status ==="
                    docker ps -a || true
                '''
            }
        }
        always {
            echo 'Pipeline execution completed.'
        }
    }
}

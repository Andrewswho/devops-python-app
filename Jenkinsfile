pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "devops-python-app"
        CONTAINER_NAME = "python-app-container"
        APP_PORT = "5000"

        DOCKER_HUB_USERNAME = "andrewswho"
        DOCKER_HUB_IMAGE = "${DOCKER_HUB_USERNAME}/devops-python-app"
        PRODUCTION_SERVER = "56.228.27.133"
        DEPLOY_KEY = "/home/ubuntu/.ssh/id_rsa"
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
                    
                    // Tag per Docker Hub
                    sh "docker tag ${DOCKER_IMAGE}:latest ${DOCKER_HUB_IMAGE}:latest"
                    sh "docker tag ${DOCKER_IMAGE}:latest ${DOCKER_HUB_IMAGE}:${BUILD_NUMBER}"
                }
            }
        }

        // NUOVO STAGE: Push to Docker Hub
        stage('Push to Docker Hub') {
            steps {
                script {
                    echo 'Pushing image to Docker Hub...'
                    docker.withRegistry('', 'dockerhub-credentials') {
                        sh "docker push ${DOCKER_HUB_IMAGE}:latest"
                        sh "docker push ${DOCKER_HUB_IMAGE}:${BUILD_NUMBER}"
                    }
                }
            }
        }

        // MODIFICATO: Deploy to Production Server (invece di locale)
        stage('Deploy to Production') {
            steps {
                script {
                    echo 'Deploying to production server...'
                    sh '''
                        ssh -i ${DEPLOY_KEY} -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER}"
                            echo 'Connected to production server'
                            
                            # Clean up Docker resources on production
                            docker system prune -f --volumes || true
                            
                            # Stop old container (usando la tua logica esistente)
                            if [ \\$(docker ps -q -f name=${CONTAINER_NAME}) ]; then
                                echo 'Stopping running container...'
                                docker stop ${CONTAINER_NAME}
                            else
                                echo 'No running container found'
                            fi

                            if [ \\$(docker ps -aq -f name=${CONTAINER_NAME}) ]; then
                                echo 'Removing old container...'
                                docker rm ${CONTAINER_NAME}
                            else
                                echo 'No container to remove'
                            fi

                            # Pull new image from Docker Hub
                            echo 'Pulling latest image from Docker Hub...'
                            docker pull ${DOCKER_HUB_IMAGE}:latest

                            # Deploy new container (usando i tuoi parametri di memoria)
                            echo 'Starting new container...'
                            docker run -d \\
                                --name ${CONTAINER_NAME} \\
                                --memory=300m \\
                                -p ${APP_PORT}:${APP_PORT} \\
                                ${DOCKER_HUB_IMAGE}:latest
                        "
                    '''
                }
            }
        }

        // MODIFICATO: Health Check su Production Server
        stage('Health Check') {
            steps {
                script {
                    echo 'Checking application health on production server...'
                    sleep 15  // Più tempo per container con risorse limitate
                    sh '''
                        # Verifica che il container sia in esecuzione sul production server
                        ssh -i ${DEPLOY_KEY} -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER}"
                            if ! docker ps | grep ${CONTAINER_NAME}; then
                                echo 'Container not running on production server!'
                                docker logs ${CONTAINER_NAME}
                                exit 1
                            fi
                        "

                        # Test health endpoint sul production server
                        curl -f http://${PRODUCTION_SERVER}:${APP_PORT}/health || exit 1
                        echo "Application is healthy on production server!"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo "Application available at: http://${PRODUCTION_SERVER}:${APP_PORT}"
        }
        failure {
            echo '❌ Pipeline failed!'
            script {
                sh '''
                    echo "=== Checking Production Server Status ==="
                    ssh -i ${DEPLOY_KEY} -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER}"
                        echo '=== Container Logs ==='
                        docker logs ${CONTAINER_NAME} || true

                        echo '=== System Resources ==='
                        free -h || true
                        df -h || true

                        echo '=== Docker Status ==='
                        docker ps -a || true
                    " || true
                '''
            }
        }
        always {
            echo 'Pipeline execution completed.'
        }
    }
}


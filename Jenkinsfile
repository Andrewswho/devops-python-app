pipeline {
  agent any
  stages {
    stage('Checkout') {
      steps {
        echo 'Cloning repository...'
        git(branch: 'main', url: 'https://github.com/AndrewsWho/devops-python-app.git')
      }
    }

    stage('Build Docker Image') {
      steps {
        echo 'Building Docker image...'
        sh 'docker build -t devops-python-app .'
      }
    }

    stage('Run Container') {
      steps {
        echo 'Starting container...'
        sh 'docker run -d -p 5000:5000 --name devops-app devops-python-app'
      }
    }

  }
}
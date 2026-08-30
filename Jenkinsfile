pipeline {
  agent any

  environment {
    IMAGE      = "prady200545/healthapp"
    TAG        = "${env.BUILD_NUMBER}"
    KUBECONFIG = "/var/lib/jenkins/.kube/config"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Docker Image') {
      steps {
        sh 'docker build -t $IMAGE:$TAG -t $IMAGE:latest .'
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub',
            usernameVariable: 'DU', passwordVariable: 'DP')]) {
          sh 'echo $DP | docker login -u $DU --password-stdin'
          sh 'docker push $IMAGE:$TAG'
          sh 'docker push $IMAGE:latest'
        }
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        sh 'kubectl apply -f k8s/'
        sh 'kubectl set image deployment/healthapp healthapp=$IMAGE:$TAG'
        sh 'kubectl rollout status deployment/healthapp --timeout=180s'
      }
    }

    stage('Verify') {
      steps {
        sh 'kubectl get pods -o wide'
        sh 'kubectl get svc'
      }
    }
  }

  post {
    success {
      echo "Deployed $IMAGE:$TAG successfully"
    }
    failure {
      echo "Build failed - check the stage above"
    }
  }
}

pipeline {
    agent { label 'small' }
    environment {
      imagename_producer_dev = "10.3.7.221:5000/queue-producer"
      imagename_consumer_dev = "10.3.7.221:5000/queue-consumer"
      imagename_producer_staging = "10.3.7.241:5000/queue-producer"
      imagename_consumer_staging = "10.3.7.241:5000/queue-consumer"
      registryCredential = 'docker-registry'
      dockerImage = ''
    }

    stages {

    stage('Git clone for dev') {
        when {branch "k8s-dev"}
        steps{
          script {
          git branch: "k8s-dev",
              url: 'https://git.indocresearch.org/platform/service_queue.git',
              credentialsId: 'lzhao'
            }
        }
    }

    stage('DEV Build and push producer image') {
      when {
          allOf {
              changeset "producer/**"
              branch "k8s-dev"
            }
      }
      steps{
        script {
            docker.withRegistry('http://10.3.7.221:5000', registryCredential) {
                customImage = docker.build("10.3.7.221:5000/queue-producer:${env.BUILD_ID}",  "./producer")
                customImage.push()
            }
        }
      }
    }
    stage('DEV Remove producer image') {
      when {
          allOf {
              changeset "producer/**"
              branch "k8s-dev"
            }
      }
      steps{
        sh "docker rmi $imagename_producer_dev:$BUILD_NUMBER"
      }
    }

    stage('DEV Deploy producer') {
      when {
          allOf {
              changeset "producer/**"
              branch "k8s-dev"
            }
      }
      steps{
        sh "sed -i 's/<VERSION>/${BUILD_NUMBER}/g' kubernetes/dev-producer-deployment.yaml"
        sh "kubectl config use-context dev"
        sh "kubectl apply -f kubernetes/dev-producer-deployment.yaml"
      }
    }

    stage('DEV Building and push consumer') {
      when {
          allOf {
              changeset "consumer/**"
              branch "k8s-dev"
            }
      }
      steps{
        script {
            docker.withRegistry('http://10.3.7.221:5000', registryCredential) {
                customImage = docker.build("10.3.7.221:5000/queue-consumer:${env.BUILD_ID}", "./consumer")
                customImage.push()
            }
        }
      }
    }

    stage('DEV Remove consumer image') {
      when {
          allOf {
              changeset "consumer/**"
              branch "k8s-dev"
            }
      }
      steps{
        sh "docker rmi $imagename_consumer_dev:$BUILD_NUMBER"
      }
    }

    stage('DEV Deploy consumer') {
      when {
          allOf {
              changeset "consumer/**"
              branch "k8s-dev"
            }
      }
      steps{
        sh "sed -i 's/<VERSION>/${BUILD_NUMBER}/g' kubernetes/dev-consumer-deployment.yaml"
        sh "kubectl config use-context dev"
        sh "kubectl apply -f kubernetes/dev-consumer-deployment.yaml"
      }
    }

    stage('Git clone staging') {
        when {branch "k8s-staging"}
        steps{
          script {
          git branch: "k8s-staging",
              url: 'https://git.indocresearch.org/platform/service_queue.git',
              credentialsId: 'lzhao'
            }
        }
    }

    stage('STAGING Building and push producer image') {
      when {
          allOf {
              changeset "producer/**"
              branch "k8s-staging"
            }
      }
      steps{
        script {
            docker.withRegistry('http://10.3.7.241:5000', registryCredential) {
                customImage = docker.build("10.3.7.241:5000/queue-producer:${env.BUILD_ID}", "./producer")
                customImage.push()
            }
        }
      }
    }

    stage('STAGING Remove producer image') {
      when {
          allOf {
              changeset "producer/**"
              branch "k8s-staging"
            }
      }
      steps{
        sh "docker rmi $imagename_producer_staging:$BUILD_NUMBER"
      }
    }

    stage('STAGING Deploy producer') {
      when {
          allOf {
              changeset "producer/**"
              branch "k8s-staging"
            }
      }
      steps{
        sh "sed -i 's/<VERSION>/${BUILD_NUMBER}/g' kubernetes/staging-producer-deployment.yaml"
        sh "kubectl config use-context staging"
        sh "kubectl apply -f kubernetes/staging-producer-deployment.yaml"
      }
    }

    stage('STAGING Building and push consumer image') {
      when {
          allOf {
              changeset "consumer/**"
              branch "k8s-staging"
            }
      }
      steps{
        script {
            docker.withRegistry('http://10.3.7.241:5000', registryCredential) {
                customImage = docker.build("10.3.7.241:5000/queue-consumer:${env.BUILD_ID}", "./consumer")
                customImage.push()
            }
        }
      }
    }

    stage('STAGING Remove consumer image') {
      when {
          allOf {
              changeset "consumer/**"
              branch "k8s-staging"
            }
      }
      steps{
        sh "docker rmi $imagename_consumer_staging:$BUILD_NUMBER"
      }
    }

    stage('STAGING Deploy consumer') {
      when {
          allOf {
              changeset "consumer/**"
              branch "k8s-staging"
            }
      }
      steps{
        sh "sed -i 's/<VERSION>/${BUILD_NUMBER}/g' kubernetes/staging-consumer-deployment.yaml"
        sh "kubectl config use-context staging"
        sh "kubectl apply -f kubernetes/staging-consumer-deployment.yaml"
      }
    }
  }
}

pipeline {
  agent any
  stages {
    stage('Print hello world') {
      steps {
        echo 'Hello world!'
      }
    }
    stage('Build') {
      steps {
        sh 'docker build . -t pybot'
      }
    }
  }
}
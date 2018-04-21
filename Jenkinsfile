pipeline {
  agent any
  stages {
    stage('Print hello world') {
      steps {
        echo 'Hello world!'
        sh 'ls -lat'
      }
    }
    stage('Build') {
      steps {
        sh 'docker build . -t pybot'
      }
    }
  }
}
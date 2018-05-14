pipeline {
  agent {
    docker {
      image 'alpine'
    }

  }
  stages {
    stage('Print hello world') {
      steps {
        echo 'Hello world!'
        sh 'ls -lat'
        sh 'pwd'
      }
    }
    stage('asd') {
      steps {
        sh 'whoami'
      }
    }
  }
}
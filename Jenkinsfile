//Jenkinsfile (Declarative Pipeline)
pipeline { 
    agent any 
    options {
        skipStagesAfterUnstable()
    }
    stages {
        stage('Build') { 
            steps { 
                sh 'make' 
            }
        }
        stage('build'){
            steps {
                sh 'make build'
            }
        }
        stage('run') {
            steps {
                sh 'make run'
            }          
        }
        
    }

    }
}
pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    environment {
        IMAGE = "mycompany/payment"
        TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Build') {
            steps {
                script {
                    env.GIT_COMMIT = bat(
                        script: '@git rev-parse HEAD',
                        returnStdout: true
                    ).trim()

                    env.BRANCH_NAME = bat(
                        script: '@git branch --show-current',
                        returnStdout: true
                    ).trim()
                }

                bat '''
                    docker build ^
                      --build-arg BUILD_NUMBER=%BUILD_NUMBER% ^
                      --build-arg GIT_COMMIT=%GIT_COMMIT% ^
                      --build-arg BRANCH_NAME=%BRANCH_NAME% ^
                      -t %IMAGE%:%TAG% .
                '''
            }
        }

        stage('Test') {
            steps {
                bat 'docker run --rm %IMAGE%:%TAG% pytest -q'
            }
        }

        stage('Tag') {
            steps {
                bat 'docker tag %IMAGE%:%TAG% %IMAGE%:%TAG%'
            }
        }

        stage('Push') {
            steps {
                echo 'Configure registry login and push in the next step.'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deployment will be enabled after registry configuration.'
            }
        }
    }
}
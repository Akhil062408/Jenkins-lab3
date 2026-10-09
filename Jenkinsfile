pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        IMAGE = "YOUR_DOCKERHUB_USERNAME/payment"
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

                    env.DOCKER_IMAGE = "${IMAGE}:${TAG}"
                }

                bat '''
                    docker build ^
                      --build-arg BUILD_NUMBER=%BUILD_NUMBER% ^
                      --build-arg GIT_COMMIT=%GIT_COMMIT% ^
                      --build-arg BRANCH_NAME=%BRANCH_NAME% ^
                      -t %DOCKER_IMAGE% .
                '''
            }
        }

        stage('Test') {
            steps {
                bat 'docker run --rm %DOCKER_IMAGE% pytest -q'
            }
        }

        stage('Tag') {
            steps {
                echo "Deployable immutable tag: ${DOCKER_IMAGE}"
                bat 'docker image inspect %DOCKER_IMAGE%'
            }
        }

        stage('Push') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_TOKEN'
                    )
                ]) {
                    bat '''
                        @echo off
                        echo %DOCKER_TOKEN% | docker login -u %DOCKER_USER% --password-stdin
                        if errorlevel 1 exit /b 1
                        docker push %DOCKER_IMAGE%
                        if errorlevel 1 exit /b 1
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                bat '''
                    @echo off
                    docker pull %DOCKER_IMAGE%
                    if errorlevel 1 exit /b 1

                    docker stop payment || exit /b 0
                '''
                bat '''
                    @echo off
                    docker rm payment 2>NUL
                    docker run -d ^
                      --name payment ^
                      -p 8080:8080 ^
                      -e APP_VERSION=%BUILD_NUMBER% ^
                      -e BUILD_NUMBER=%BUILD_NUMBER% ^
                      -e GIT_COMMIT=%GIT_COMMIT% ^
                      -e BRANCH_NAME=%BRANCH_NAME% ^
                      -e DOCKER_IMAGE=%DOCKER_IMAGE% ^
                      %DOCKER_IMAGE%
                    if errorlevel 1 exit /b 1
                '''
                bat 'curl --fail http://localhost:8080/version'
            }
        }
    }

    post {
        always {
            echo "Jenkins build: ${BUILD_NUMBER}"
            echo "Git commit: ${GIT_COMMIT}"
            echo "Branch: ${BRANCH_NAME}"
            echo "Docker image: ${IMAGE}:${TAG}"
        }
    }
}

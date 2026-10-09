pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        // Replace with your actual Docker Hub username (lowercase)
        IMAGE = "your_actual_dockerhub_username/payment"
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

                    // Works with Jenkins multibranch and regular Pipeline jobs
                    def detectedBranch = env.BRANCH_NAME?.trim()

                    if (!detectedBranch) {
                        detectedBranch = bat(
                            script: '@git branch --show-current',
                            returnStdout: true
                        ).trim()
                    }

                    if (!detectedBranch) {
                        detectedBranch = bat(
                            script: '@git rev-parse --abbrev-ref HEAD',
                            returnStdout: true
                        ).trim()
                    }

                    env.BRANCH_NAME = detectedBranch ?: 'unknown'
                    env.DOCKER_IMAGE = "${IMAGE}:${TAG}"

                    echo "Building image: ${env.DOCKER_IMAGE}"
                    echo "Git commit: ${env.GIT_COMMIT}"
                    echo "Branch: ${env.BRANCH_NAME}"
                }

                bat '''
                    docker build ^
                      --build-arg BUILD_NUMBER=%BUILD_NUMBER% ^
                      --build-arg GIT_COMMIT=%GIT_COMMIT% ^
                      --build-arg BRANCH_NAME=%BRANCH_NAME% ^
                      -t %DOCKER_IMAGE% .
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Test') {
            steps {
                bat '''
                    docker run --rm %DOCKER_IMAGE% pytest -q
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Tag') {
            steps {
                echo "Deployable image: ${env.DOCKER_IMAGE}"
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
                        echo %DOCKER_TOKEN%| docker login -u %DOCKER_USER% --password-stdin
                        if errorlevel 1 exit /b 1

                        docker push %DOCKER_IMAGE%
                        set PUSH_RESULT=%ERRORLEVEL%

                        docker logout

                        if not "%PUSH_RESULT%"=="0" exit /b 1
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

                    docker stop payment 2>NUL
                    docker rm -f payment 2>NUL
                '''

                bat '''
                    @echo off
                    docker run -d ^
                      --name payment ^
                      --restart unless-stopped ^
                      -p 8080:8080 ^
                      -e APP_VERSION=%BUILD_NUMBER% ^
                      -e BUILD_NUMBER=%BUILD_NUMBER% ^
                      -e GIT_COMMIT=%GIT_COMMIT% ^
                      -e BRANCH_NAME=%BRANCH_NAME% ^
                      -e DOCKER_IMAGE=%DOCKER_IMAGE% ^
                      %DOCKER_IMAGE%

                    if errorlevel 1 exit /b 1
                '''

                bat '''
                    @echo off
                    curl --fail --retry 10 --retry-delay 2 ^
                      http://localhost:8080/version
                    if errorlevel 1 exit /b 1
                '''
            }
        }
    }

    post {
        always {
            echo "Jenkins build: ${env.BUILD_NUMBER}"
            echo "Git commit: ${env.GIT_COMMIT ?: 'unknown'}"
            echo "Branch: ${env.BRANCH_NAME ?: 'unknown'}"
            echo "Docker image: ${env.IMAGE}:${env.TAG}"
        }
    }
}
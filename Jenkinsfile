pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        PROJECT_DIR = 'C:\\Users\\Tiago.Silva\\documents\\projects\\STM-LOCAL\\stm32f407-cicd-template'
    }

        stage('Source Information') {
            steps {
                bat '''
                    @echo off

                    echo ========================================
                    echo Jenkins workspace
                    echo ========================================
                    echo %WORKSPACE%

                    echo.
                    echo Workspace commit:
                    git -C "%WORKSPACE%" rev-parse HEAD

                    echo.
                    echo Workspace status:
                    git -C "%WORKSPACE%" status --short

                    echo.
                    echo ========================================
                    echo Local STM32 project
                    echo ========================================
                    echo %PROJECT_DIR%

                    echo.
                    echo Local project commit:
                    git -C "%PROJECT_DIR%" rev-parse HEAD

                    echo.
                    echo Local project status:
                    git -C "%PROJECT_DIR%" status --short
                '''
            }
        }

        stage('Validate Source Consistency') {
            steps {
                script {
                    def workspaceCommit = bat(
                        script: '@git -C "%WORKSPACE%" rev-parse HEAD',
                        returnStdout: true
                    ).trim()

                    def localCommit = bat(
                        script: '@git -C "%PROJECT_DIR%" rev-parse HEAD',
                        returnStdout: true
                    ).trim()

                    def workspaceStatus = bat(
                        script: '@git -C "%WORKSPACE%" status --porcelain',
                        returnStdout: true
                    ).trim()

                    def localStatus = bat(
                        script: '@git -C "%PROJECT_DIR%" status --porcelain',
                        returnStdout: true
                    ).trim()

                    echo "Workspace commit: ${workspaceCommit}"
                    echo "Local commit:     ${localCommit}"

                    if (workspaceCommit != localCommit) {
                        error(
                            "Source mismatch: Jenkins workspace and local " +
                            "STM32 project are on different commits."
                        )
                    }

                    if (workspaceStatus) {
                        error(
                            "Jenkins workspace contains uncommitted changes:\n" +
                            workspaceStatus
                        )
                    }

                    if (localStatus) {
                        error(
                            "Local STM32 project contains uncommitted changes:\n" +
                            localStatus
                        )
                    }

                    echo 'Source consistency validated successfully'
                }
            }
        
            stages {
                stage('Environment') {
                    steps {
                        bat '''
                            @echo off

                            echo === Python ===
                            python --version

                            echo.
                            echo === GNU Make ===
                            make --version

                            echo.
                            echo === GNU Arm GCC ===
                            arm-none-eabi-gcc --version
                        '''
                    }
                }
            }

        stage('Build') {
            steps {
                dir("${env.PROJECT_DIR}") {
                    bat '''
                        @echo off

                        echo Starting STM32 firmware build...

                        python Automation\\build.py ^
                            --config Debug ^
                            --clean
                    '''
                }
            }
        }

        stage('Validate Artifacts') {
            steps {
                dir("${env.PROJECT_DIR}") {
                    bat '''
                        @echo off

                        echo Validating firmware artifacts...

                        if not exist Debug\\stm32f407-cicd-template.elf (
                            echo ERROR: ELF file was not generated
                            exit /b 1
                        )

                        if not exist Debug\\stm32f407-cicd-template.hex (
                            echo ERROR: HEX file was not generated
                            exit /b 1
                        )

                        if not exist Debug\\stm32f407-cicd-template.bin (
                            echo ERROR: BIN file was not generated
                            exit /b 1
                        )

                        if not exist Debug\\stm32f407-cicd-template.map (
                            echo ERROR: MAP file was not generated
                            exit /b 1
                        )

                        if not exist Debug\\stm32f407-cicd-template.list (
                            echo ERROR: LIST file was not generated
                            exit /b 1
                        )

                        echo.
                        echo === Firmware memory usage ===
                        arm-none-eabi-size Debug\\stm32f407-cicd-template.elf

                        echo.
                        echo All firmware artifacts were validated
                    '''
                }
            }
        }
        
        stage('Publish Artifacts') {
            steps {
                bat '''
                    @echo off
                    
                    if exist artifacts (
                        rmdir /s /q artifacts
                        )
                        
                    mkdir artifacts
                    copy "%PROJECT_DIR%\\Debug\\stm32f407-cicd-template.elf" artifacts\\
                    copy "%PROJECT_DIR%\\Debug\\stm32f407-cicd-template.hex" artifacts\\
                    copy "%PROJECT_DIR%\\Debug\\stm32f407-cicd-template.bin" artifacts\\
                    copy "%PROJECT_DIR%\\Debug\\stm32f407-cicd-template.map" artifacts\\
                    copy "%PROJECT_DIR%\\Debug\\stm32f407-cicd-template.list" artifacts\\
                    '''
                archiveArtifacts(
                    artifacts: 'artifacts/*',
                    fingerprint: true
                    )
            }
        }
        
        stage('Flash') {
            steps {
                dir("${env.PROJECT_DIR}") {
                    bat '''
                        @echo off

                        echo Starting STM32 firmware flashing...

                        python Automation\\flash.py ^
                            --config Debug ^
                            --erase-all
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'STM32 firmware build completed successfully'
        }

        failure {
            echo 'STM32 firmware build failed'
        }

        always {
            echo "Final result: ${currentBuild.currentResult}"
        }
    }
}
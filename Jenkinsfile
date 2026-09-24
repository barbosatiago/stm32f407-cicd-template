pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    triggers {
        pollSCM('* * * * *')
    }

    parameters {
        choice(
            name: 'BUILD_CONFIG',
            choices: ['Debug', 'Release'],
            description: 'Firmware build configuration'
        )

        booleanParam(
            name: 'CLEAN_BUILD',
            defaultValue: true,
            description: 'Remove previous build objects before compilation'
        )

        booleanParam(
            name: 'RUN_FLASH',
            defaultValue: true,
            description: 'Program the firmware after build'
        )

        string(
            name: 'STLINK_SERIAL_NUMBER',
            defaultValue: '066EFF353055423143241415',
            description: 'ST-LINK serial number'
        )
    }

    environment {
        PROJECT_DIR = 'C:\\Users\\Tiago.Silva\\documents\\projects\\STM-JENKINS\\stm32f407-cicd-template'
        FIRMWARE_NAME = 'stm32f407-cicd-template'
    }

    stages {

        stage('Build') {
            steps {
                dir("${env.PROJECT_DIR}") {

                    bat '''
                        @echo off

                        echo ========================================
                        echo Synchronizing repository
                        echo ========================================

                        git fetch origin main || exit /b 1
                        git reset --hard origin/main || exit /b 1

                        echo ========================================
                        echo Toolchain information
                        echo ========================================

                        python --version
                        git --version
                        make --version
                        arm-none-eabi-gcc --version

                        echo ========================================
                        echo Building firmware
                        echo ========================================

                        python Automation\\build.py ^
                            --config %BUILD_CONFIG% ^
                            --clean
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                dir("${env.PROJECT_DIR}") {

                    bat '''
                        @echo off

                        echo ========================================
                        echo Validating artifacts
                        echo ========================================

                        if not exist %BUILD_CONFIG%\\%FIRMWARE_NAME%.elf exit /b 1
                        if not exist %BUILD_CONFIG%\\%FIRMWARE_NAME%.hex exit /b 1
                        if not exist %BUILD_CONFIG%\\%FIRMWARE_NAME%.bin exit /b 1
                        if not exist %BUILD_CONFIG%\\%FIRMWARE_NAME%.map exit /b 1
                        if not exist %BUILD_CONFIG%\\%FIRMWARE_NAME%.list exit /b 1

                        echo.
                        echo Firmware memory usage:
                        arm-none-eabi-size %BUILD_CONFIG%\\%FIRMWARE_NAME%.elf

                        echo.
                        echo Artifact validation successful
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {

                bat '''
                    @echo off

                    if exist artifacts (
                        rmdir /s /q artifacts
                    )

                    mkdir artifacts

                    copy "%PROJECT_DIR%\\%BUILD_CONFIG%\\%FIRMWARE_NAME%.elf" artifacts\\
                    copy "%PROJECT_DIR%\\%BUILD_CONFIG%\\%FIRMWARE_NAME%.hex" artifacts\\
                    copy "%PROJECT_DIR%\\%BUILD_CONFIG%\\%FIRMWARE_NAME%.bin" artifacts\\
                    copy "%PROJECT_DIR%\\%BUILD_CONFIG%\\%FIRMWARE_NAME%.map" artifacts\\
                    copy "%PROJECT_DIR%\\%BUILD_CONFIG%\\%FIRMWARE_NAME%.list" artifacts\\
                '''

                archiveArtifacts(
                    artifacts: 'artifacts/*',
                    fingerprint: true
                )

                script {
                    if (params.RUN_FLASH) {
                        dir("${env.PROJECT_DIR}") {
                            bat '''
                                @echo off

                                echo ========================================
                                echo Flashing STM32
                                echo ========================================

                                python Automation\\flash.py ^
                                    --config %BUILD_CONFIG% ^
                                    --under-reset ^
                                    --serial-number %STLINK_SERIAL_NUMBER%
                            '''
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Build, test and deploy completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Check console output.'
        }

        always {
            echo "Final result: ${currentBuild.currentResult}"
        }
    }
}
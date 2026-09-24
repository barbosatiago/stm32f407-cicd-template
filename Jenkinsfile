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
            choices: [
                'Debug',
                'Release'
            ],
            description: 'Firmware build configuration'
        )

        booleanParam(
            name: 'CLEAN_BUILD',
            defaultValue: true,
            description: 'Remove previous build objects before compilation'
        )

        string(
            name: 'BUILD_JOBS',
            defaultValue: '4',
            description: 'Number of parallel Make jobs'
        )

        booleanParam(
            name: 'RUN_FLASH',
            defaultValue: true,
            description: 'Program the firmware after a successful build'
        )

        booleanParam(
            name: 'UNDER_RESET',
            defaultValue: true,
            description: 'Connect to the STM32 under hardware reset'
        )

        booleanParam(
            name: 'ERASE_ALL',
            defaultValue: false,
            description: 'Perform a full Flash erase before programming'
        )

        string(
            name: 'STLINK_SERIAL_NUMBER',
            defaultValue: '066EFF353055423143241415',
            description: 'ST-LINK serial number'
        )

        string(
            name: 'FIRMWARE_IMAGE',
            defaultValue: '',
            description: 'Optional custom HEX, ELF or BIN path'
        )
    }

    environment {
        PROJECT_DIR = 'C:\\Users\\Tiago.Silva\\documents\\projects\\STM-JENKINS\\stm32f407-cicd-template'
        STLINK_SERIAL_NUMBER = '066EFF353055423143241415'
        FIRMWARE_NAME = 'stm32f407-cicd-template'
    }
    

    stages {
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
                    echo Dedicated STM32 build repository
                    echo ========================================
                    echo %PROJECT_DIR%

                    echo.
                    echo Build repository commit before sync:
                    git -C "%PROJECT_DIR%" rev-parse HEAD

                    echo.
                    echo Build repository status before sync:
                    git -C "%PROJECT_DIR%" status --short
                '''
            }
        }

        stage('Synchronize Build Repository') {
            steps {
                dir("${env.PROJECT_DIR}") {
                    bat '''
                        @echo off

                        echo ========================================
                        echo Synchronizing build repository
                        echo ========================================

                        git fetch origin main

                        if errorlevel 1 (
                            echo ERROR: Git fetch failed
                            exit /b 1
                        )

                        git reset --hard origin/main

                        if errorlevel 1 (
                            echo ERROR: Git reset failed
                            exit /b 1
                        )

                        echo.
                        echo Build repository commit after sync:
                        git rev-parse HEAD

                        echo.
                        echo Build repository status after sync:
                        git status --short
                    '''
                }
            }
        }

        stage('Validate Source Consistency') {
            steps {
                script {
                    def workspaceCommit = bat(
                        script: '@git -C "%WORKSPACE%" rev-parse HEAD',
                        returnStdout: true
                    ).trim()

                    def buildCommit = bat(
                        script: '@git -C "%PROJECT_DIR%" rev-parse HEAD',
                        returnStdout: true
                    ).trim()

                    def workspaceStatus = bat(
                        script: '@git -C "%WORKSPACE%" status --porcelain',
                        returnStdout: true
                    ).trim()

                    def buildStatus = bat(
                        script: '@git -C "%PROJECT_DIR%" status --porcelain',
                        returnStdout: true
                    ).trim()

                    echo "Workspace commit: ${workspaceCommit}"
                    echo "Build commit:     ${buildCommit}"

                    if (workspaceCommit != buildCommit) {
                        error(
                            'Source mismatch: the Jenkins workspace and ' +
                            'dedicated build repository are on different commits.'
                        )
                    }

                    if (workspaceStatus) {
                        error(
                            "Jenkins workspace contains uncommitted changes:\n" +
                            workspaceStatus
                        )
                    }

                    if (buildStatus) {
                        error(
                            "Build repository contains uncommitted changes:\n" +
                            buildStatus
                        )
                    }

                    echo 'Source consistency validated successfully'
                }
            }
        }

        stage('Environment') {
            steps {
                bat '''
                    @echo off

                    echo ========================================
                    echo Python
                    echo ========================================
                    where python
                    python --version

                    echo.
                    echo ========================================
                    echo Git
                    echo ========================================
                    where git
                    git --version

                    echo.
                    echo ========================================
                    echo GNU Make
                    echo ========================================
                    where make
                    make --version

                    echo.
                    echo ========================================
                    echo GNU Arm GCC
                    echo ========================================
                    where arm-none-eabi-gcc
                    arm-none-eabi-gcc --version

                    echo.
                    echo ========================================
                    echo STM32CubeProgrammer and ST-LINK
                    echo ========================================
                    where STM32_Programmer_CLI.exe
                    STM32_Programmer_CLI.exe -l stlink
                '''
            }
        }

        stage('Build') {
            steps {
                dir("${env.PROJECT_DIR}") {
                    bat '''
                        @echo off

                        echo ========================================
                        echo Building STM32 firmware
                        echo ========================================

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

                        echo ========================================
                        echo Validating firmware artifacts
                        echo ========================================

                        if not exist Debug\\%FIRMWARE_NAME%.elf (
                            echo ERROR: ELF artifact was not generated
                            exit /b 1
                        )

                        if not exist Debug\\%FIRMWARE_NAME%.hex (
                            echo ERROR: HEX artifact was not generated
                            exit /b 1
                        )

                        if not exist Debug\\%FIRMWARE_NAME%.bin (
                            echo ERROR: BIN artifact was not generated
                            exit /b 1
                        )

                        if not exist Debug\\%FIRMWARE_NAME%.map (
                            echo ERROR: MAP artifact was not generated
                            exit /b 1
                        )

                        if not exist Debug\\%FIRMWARE_NAME%.list (
                            echo ERROR: LIST artifact was not generated
                            exit /b 1
                        )

                        echo.
                        echo Firmware memory usage:
                        arm-none-eabi-size Debug\\%FIRMWARE_NAME%.elf

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

                    echo ========================================
                    echo Copying artifacts into Jenkins workspace
                    echo ========================================

                    if exist artifacts (
                        rmdir /s /q artifacts
                    )

                    mkdir artifacts

                    copy "%PROJECT_DIR%\\Debug\\%FIRMWARE_NAME%.elf" artifacts\\
                    copy "%PROJECT_DIR%\\Debug\\%FIRMWARE_NAME%.hex" artifacts\\
                    copy "%PROJECT_DIR%\\Debug\\%FIRMWARE_NAME%.bin" artifacts\\
                    copy "%PROJECT_DIR%\\Debug\\%FIRMWARE_NAME%.map" artifacts\\
                    copy "%PROJECT_DIR%\\Debug\\%FIRMWARE_NAME%.list" artifacts\\

                    if errorlevel 1 (
                        echo ERROR: Failed to copy one or more artifacts
                        exit /b 1
                    )
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

                        echo ========================================
                        echo Programming STM32F407
                        echo ========================================

                        python Automation\\flash.py ^
                            --config Debug ^
                            --under-reset ^
                            --serial-number %STLINK_SERIAL_NUMBER%
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'STM32 firmware build, publication and flash completed successfully'
        }

        failure {
            echo 'STM32 pipeline failed. Check the failing stage and console output.'
        }

        always {
            echo "Final result: ${currentBuild.currentResult}"
        }
    }
}
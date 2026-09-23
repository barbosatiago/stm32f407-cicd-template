pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        PROJECT_DIR = 'C:\\Users\\Tiago.Silva\\documents\\projects\\STM-LOCAL\\stm32f407-cicd-template'
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

        stage('Source Information') {
            steps {
                bat '''
                    @echo off
                    echo Workspace: %WORKSPACE%
                    git rev-parse HEAD
                    git status --short
                '''
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
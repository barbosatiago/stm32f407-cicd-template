pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()

        buildDiscarder(
            logRotator(
                numToKeepStr: '20',
                artifactNumToKeepStr: '10'
            )
        )
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
        REPOSITORY_URL = 'https://github.com/barbosatiago/stm32f407-cicd-template.git'

        PROJECT_ROOT = 'C:\\Users\\Tiago.Silva\\Documents\\Projects\\STM-JENKINS'

        PROJECT_DIR = 'C:\\Users\\Tiago.Silva\\Documents\\Projects\\STM-JENKINS\\stm32f407-cicd-template'

        BUILD_SEED_DIR = 'C:\\Users\\Tiago.Silva\\Documents\\Projects\\STM-BUILD-SEED'

        FIRMWARE_NAME = 'stm32f407-cicd-template'
    }

    stages {
        stage('Source Information') {
            steps {
                script {
                    env.SOURCE_COMMIT = bat(
                        script: '@git -C "%WORKSPACE%" rev-parse HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Workspace:     ${env.WORKSPACE}"
                    echo "Source commit: ${env.SOURCE_COMMIT}"
                    echo "Build config:  ${params.BUILD_CONFIG}"
                    echo "Clean build:   ${params.CLEAN_BUILD}"
                    echo "Run flash:     ${params.RUN_FLASH}"
                }
            }
        }

        stage('Validate Parameters') {
            steps {
                script {
                    if (
                        !(params.STLINK_SERIAL_NUMBER ==~
                          /^[A-Za-z0-9]+$/)
                    ) {
                        error(
                            'STLINK_SERIAL_NUMBER contains invalid characters.'
                        )
                    }

                    if (
                        params.BUILD_CONFIG != 'Debug' &&
                        params.BUILD_CONFIG != 'Release'
                    ) {
                        error(
                            "Invalid BUILD_CONFIG: " +
                            params.BUILD_CONFIG
                        )
                    }
                }
            }
        }

        stage('Bootstrap Repository') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $projectRoot = $env:PROJECT_ROOT
                    $projectDir = $env:PROJECT_DIR
                    $repositoryUrl = $env:REPOSITORY_URL
                    $buildConfig = $env:BUILD_CONFIG
                    $seedDir = Join-Path `
                        $env:BUILD_SEED_DIR `
                        $buildConfig

                    Write-Host "========================================"
                    Write-Host "Bootstrapping dedicated build repository"
                    Write-Host "========================================"

                    Write-Host "Project directory: $projectDir"
                    Write-Host "Repository URL:    $repositoryUrl"
                    Write-Host "Build config:      $buildConfig"

                    New-Item `
                        -ItemType Directory `
                        -Path $projectRoot `
                        -Force |
                        Out-Null

                    $savedBuildDirectory = $null
                    $existingBuildDirectory = Join-Path `
                        $projectDir `
                        $buildConfig

                    if (
                        (Test-Path $projectDir) -and
                        -not (Test-Path (Join-Path $projectDir ".git"))
                    ) {
                        Write-Host ""
                        Write-Host "WARNING: Project directory exists but"
                        Write-Host "is not a Git repository."

                        if (Test-Path $existingBuildDirectory) {
                            $savedBuildDirectory = Join-Path `
                                $env:TEMP `
                                "stm32-$buildConfig-$env:BUILD_NUMBER"

                            Write-Host "Preserving generated build directory:"
                            Write-Host $savedBuildDirectory

                            if (Test-Path $savedBuildDirectory) {
                                Remove-Item `
                                    $savedBuildDirectory `
                                    -Recurse `
                                    -Force
                            }

                            Copy-Item `
                                $existingBuildDirectory `
                                $savedBuildDirectory `
                                -Recurse `
                                -Force
                        }

                        Write-Host "Removing invalid project directory..."

                        Remove-Item `
                            $projectDir `
                            -Recurse `
                            -Force
                    }

                    if (-not (Test-Path (Join-Path $projectDir ".git"))) {
                        Write-Host ""
                        Write-Host "Cloning repository..."

                        git clone `
                            $repositoryUrl `
                            $projectDir

                        if ($LASTEXITCODE -ne 0) {
                            throw "Git clone failed with exit code $LASTEXITCODE"
                        }
                    }

                    $destinationBuildDirectory = Join-Path `
                        $projectDir `
                        $buildConfig

                    if (
                        $savedBuildDirectory -and
                        -not (Test-Path $destinationBuildDirectory)
                    ) {
                        Write-Host ""
                        Write-Host "Restoring preserved build directory..."

                        Copy-Item `
                            $savedBuildDirectory `
                            $destinationBuildDirectory `
                            -Recurse `
                            -Force
                    }

                    $makefile = Join-Path `
                        $destinationBuildDirectory `
                        "makefile"

                    if (
                        -not (Test-Path $makefile) -and
                        (Test-Path (Join-Path $seedDir "makefile"))
                    ) {
                        Write-Host ""
                        Write-Host "Restoring build directory from seed:"
                        Write-Host $seedDir

                        Copy-Item `
                            $seedDir `
                            $destinationBuildDirectory `
                            -Recurse `
                            -Force
                    }

                    Write-Host ""
                    Write-Host "Git repository:"
                    git -C $projectDir status --short

                    if ($LASTEXITCODE -ne 0) {
                        throw "Repository bootstrap validation failed"
                    }
                '''
            }
        }

        stage('Synchronize Repository') {
            steps {
                retry(2) {
                    dir("${env.PROJECT_DIR}") {
                        bat """
                            @echo off

                            echo ========================================
                            echo Synchronizing repository
                            echo ========================================

                            echo Target commit:
                            echo ${env.SOURCE_COMMIT}

                            git fetch origin ^
                                +refs/heads/*:refs/remotes/origin/* ^
                                --prune ^
                                --tags

                            if errorlevel 1 (
                                echo ERROR: Git fetch failed
                                exit /b 1
                            )

                            git cat-file -e ${env.SOURCE_COMMIT}^{commit}

                            if errorlevel 1 (
                                echo ERROR: Target commit was not found.
                                echo Commit: ${env.SOURCE_COMMIT}
                                exit /b 1
                            )

                            git reset --hard ${env.SOURCE_COMMIT}

                            if errorlevel 1 (
                                echo ERROR: Git reset failed
                                exit /b 1
                            )

                            echo.
                            echo Build repository commit:
                            git rev-parse HEAD

                            echo.
                            echo Build repository status:
                            git status --short
                        """
                    }
                }
            }
        }

        stage('Preflight') {
            steps {
                dir("${env.PROJECT_DIR}") {
                    bat '''
                        @echo off

                        echo ========================================
                        echo Repository preflight
                        echo ========================================

                        if not exist ".git" (
                            echo ERROR: Missing Git metadata.
                            echo Expected: %PROJECT_DIR%\\.git
                            exit /b 1
                        )

                        if not exist "Automation\\build.py" (
                            echo ERROR: Automation\\build.py is missing.
                            exit /b 1
                        )

                        if not exist "Automation\\flash.py" (
                            echo ERROR: Automation\\flash.py is missing.
                            exit /b 1
                        )

                        if not exist "%BUILD_CONFIG%\\makefile" (
                            echo ERROR: Generated Makefile is missing.
                            echo Expected:
                            echo %PROJECT_DIR%\\%BUILD_CONFIG%\\makefile
                            echo.
                            echo Generate this configuration once with
                            echo STM32CubeIDE or update BUILD_SEED_DIR.
                            exit /b 1
                        )

                        echo.
                        echo ========================================
                        echo Toolchain preflight
                        echo ========================================

                        where python
                        if errorlevel 1 exit /b 1

                        python --version
                        if errorlevel 1 exit /b 1

                        where git
                        if errorlevel 1 exit /b 1

                        git --version
                        if errorlevel 1 exit /b 1

                        where make
                        if errorlevel 1 exit /b 1

                        make --version
                        if errorlevel 1 exit /b 1

                        where arm-none-eabi-gcc
                        if errorlevel 1 exit /b 1

                        arm-none-eabi-gcc --version
                        if errorlevel 1 exit /b 1

                        where arm-none-eabi-size
                        if errorlevel 1 exit /b 1

                        if "%RUN_FLASH%" == "true" (
                            where STM32_Programmer_CLI.exe
                            if errorlevel 1 exit /b 1

                            STM32_Programmer_CLI.exe -l stlink
                            if errorlevel 1 exit /b 1
                        )

                        echo.
                        echo Preflight completed successfully.
                    '''
                }
            }
        }

        stage('Validate Source Revision') {
            steps {
                script {
                    def buildCommit = bat(
                        script:
                            '@git -C "%PROJECT_DIR%" rev-parse HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Workspace commit: ${env.SOURCE_COMMIT}"
                    echo "Build commit:     ${buildCommit}"

                    if (env.SOURCE_COMMIT != buildCommit) {
                        error(
                            'Workspace and build repository commits differ.'
                        )
                    }
                }
            }
        }

        stage('Build') {
            steps {
                dir("${env.PROJECT_DIR}") {
                    script {
                        def buildArguments = [
                            'python',
                            'Automation\\build.py',
                            '--config',
                            params.BUILD_CONFIG
                        ]

                        if (params.CLEAN_BUILD) {
                            buildArguments.add('--clean')
                        }

                        echo(
                            'Build command: ' +
                            buildArguments.join(' ')
                        )

                        bat(
                            label: 'Build STM32 firmware',
                            script:
                                "@echo off\r\n" +
                                buildArguments.join(' ')
                        )
                    }
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

                        if not exist "%BUILD_CONFIG%\\%FIRMWARE_NAME%.elf" (
                            echo ERROR: ELF artifact is missing.
                            exit /b 1
                        )

                        if not exist "%BUILD_CONFIG%\\%FIRMWARE_NAME%.hex" (
                            echo ERROR: HEX artifact is missing.
                            exit /b 1
                        )

                        if not exist "%BUILD_CONFIG%\\%FIRMWARE_NAME%.bin" (
                            echo ERROR: BIN artifact is missing.
                            exit /b 1
                        )

                        if not exist "%BUILD_CONFIG%\\%FIRMWARE_NAME%.map" (
                            echo ERROR: MAP artifact is missing.
                            exit /b 1
                        )

                        if not exist "%BUILD_CONFIG%\\%FIRMWARE_NAME%.list" (
                            echo ERROR: LIST artifact is missing.
                            exit /b 1
                        )

                        echo.
                        echo Firmware memory usage:

                        arm-none-eabi-size ^
                            "%BUILD_CONFIG%\\%FIRMWARE_NAME%.elf"

                        if errorlevel 1 exit /b 1

                        echo.
                        echo Artifact validation successful.
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

                    copy "%PROJECT_DIR%\\%BUILD_CONFIG%\\%FIRMWARE_NAME%.elf" artifacts\\
                    if errorlevel 1 exit /b 1

                    copy "%PROJECT_DIR%\\%BUILD_CONFIG%\\%FIRMWARE_NAME%.hex" artifacts\\
                    if errorlevel 1 exit /b 1

                    copy "%PROJECT_DIR%\\%BUILD_CONFIG%\\%FIRMWARE_NAME%.bin" artifacts\\
                    if errorlevel 1 exit /b 1

                    copy "%PROJECT_DIR%\\%BUILD_CONFIG%\\%FIRMWARE_NAME%.map" artifacts\\
                    if errorlevel 1 exit /b 1

                    copy "%PROJECT_DIR%\\%BUILD_CONFIG%\\%FIRMWARE_NAME%.list" artifacts\\
                    if errorlevel 1 exit /b 1
                '''

                archiveArtifacts(
                    artifacts: 'artifacts/*',
                    fingerprint: true
                )
            }
        }

        stage('Flash') {
            when {
                expression {
                    return params.RUN_FLASH
                }
            }

            steps {
                dir("${env.PROJECT_DIR}") {
                    timeout(time: 2, unit: 'MINUTES') {
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

    post {
        success {
            echo(
                'Build, artifact publication and flash ' +
                'completed successfully.'
            )
        }

        failure {
            echo(
                'Pipeline failed. Check the first failing ' +
                'stage and its console output.'
            )
        }

        always {
            echo "Final result: ${currentBuild.currentResult}"
        }
    }
}
# STM32F407 CI/CD Template

Template de firmware para a placa STM32F407G-DISC1 com automação de build e flash utilizando Python.

O objetivo do projeto é construir gradualmente um ambiente profissional de CI/CD para firmware embarcado, incluindo:

- build automatizado;
- geração de ELF, HEX e BIN;
- programação via ST-LINK;
- testes unitários;
- análise estática;
- smoke tests;
- testes funcionais;
- Hardware-in-the-Loop;
- integração com Jenkins e GitHub.

## Hardware

- Board: STM32F407G-DISC1 / STM32F4DISCOVERY
- MCU: STM32F407VGT6
- CPU: Arm Cortex-M4 com FPU
- Flash: 1 MB
- Interface de programação: ST-LINK via SWD
- Hello World: LED verde conectado ao pino PD12

## Ferramentas

O ambiente atual utiliza:

- STM32CubeMX
- STM32CubeIDE 2.0.0
- STM32CubeProgrammer 2.21.0
- GNU Arm Embedded Toolchain
- GNU Make
- Python 3
- Git
- GitHub
- Jenkins

## Estrutura do projeto



```text
stm32f407-cicd-template/
├── Core/
│   ├── Inc/
│   ├── Src/
│   └── Startup/
├── Drivers/
├── Middlewares/
├── USB_HOST/
├── Automation/
│   ├── build.py
│   └── flash.py
├── Debug/
├── STM32F407VGTX_FLASH.ld
├── stm32f407-cicd-template.ioc
├── Jenkinsfile
├── README.md
├── .gitignore
├── .project
└── .cproject
```
## Clean build
python .\Automation\build.py --config Debug --clean

## Build incremental
python .\Automation\build.py --config Debug

## Controlar o paralelismo
python .\Automation\build.py --config Debug --clean --jobs 4

## Flash da configuração debug
python .\Automation\flash.py --config Debug

## Flash com conexão sob reset
python .\Automation\flash.py `
  --config Debug `
  --under-reset

## Selecionar um STLINK especifico
python .\Automation\flash.py `
  --config Debug `
  --serial-number 066EFF353055423143241415

## Full erase antes da programação
python .\Automation\flash.py `
  --config Debug `
  --erase-all
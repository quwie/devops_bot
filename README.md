# DevOps Telegram Bot

Бот создан в рамках модуля DevOps во время стажировки PT_START.

## Getting Started

Чтобы начать работу с ботом Telegram, выполните следующие действия:

1. Склонируйте этот репозиторий:

    ```shell
    git clone https://github.com/quwie/devops_bot.git
    ```

2. Перейдите в ветку ansible:


3. Запустите конфиг используя команду:

    ```shell
    ansible-playbook -i inventory/hosts --extra-vars "@secret.yml" playbook_tg_bot.yml
    ```

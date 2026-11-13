# AI Password Challenge (Sandbox)

Публичный стенд для проверки перебора паролей в песочнице ИИ (безопасный эксперимент: хранится только `salt` + `SHA-256` слепок, сам пароль в репозиторий никогда не попадает).

## Текущая задача
Файл задачи: [`challenge.json`](./challenge.json)

Прямая ссылка для ИИ:
`https://raw.githubusercontent.com/garant-sv/ai-password-challenge/main/challenge.json`

## Как сгенерировать новый пароль локально
```bash
python3 generate_challenge.py --push
```
Скрипт создаст новый случайный 8-символьный пароль (строчные и заглавные буквы, цифры, спецсимволы), запишет настоящий ответ локально в `.secret_passwords.log` (игнорируется Git) и обновит `challenge.json`.

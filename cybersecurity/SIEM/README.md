# SIEM на Wazuh — обнаружение веб-атак на DVWA

## Цель

Развернуть SIEM Wazuh, передавать логи веб-сервера уязвимого тестового приложения (DVWA) через агент Wazuh и
обнаруживать веб-атаки (XSS, SQL-инъекции) практически в реальном времени.

## Лабораторный стенд

- Wazuh 4.10.0 в режиме single-node в Docker (manager, indexer, dashboard)
- Агент Wazuh 4.9.0 на Kali Linux
- DVWA в Docker на порту 8080, логи доступа Apache смонтированы на хост

```text
┌──────────────┐   access.log   ┌──────────────┐   1514/tcp   ┌──────────────┐
│ DVWA         │ ─────────────▶ │ Wazuh agent  │ ───────────▶ │ Wazuh        │
│ (Docker)     │   (volume)     │ (Kali)       │              │ manager      │
└──────────────┘                └──────────────┘              └──────┬───────┘
                                                                     │
                                                              ┌──────▼───────┐
                                                              │ Indexer +    │
                                                              │ Dashboard    │
                                                              └──────────────┘
```

## Настройка

### 1. Стек Wazuh

```bash
git clone https://github.com/wazuh/wazuh-docker.git -b v4.10.0
cd wazuh-docker/single-node
docker compose -f generate-indexer-certs.yml run --rm generator
docker compose up -d
```

Стандартные пароли были изменены до первого использования: `INDEXER_PASSWORD` и `API_PASSWORD` в `docker-compose.yml`,
хеши пользователей в `config/wazuh_indexer/internal_users.yml` и пароль API в
`config/wazuh_dashboard/wazuh.yml`.

### 2. DVWA с логами на томе хоста

```bash
docker run -d -p 8080:80 --name dvwa \
  -v /mnt/data/dvwa-logs:/var/log/apache2 \
  vulnerables/web-dvwa
```

### 3. Агент на Kali

```bash
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | sudo gpg --dearmor -o /usr/share/keyrings/wazuh.gpg
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" \
  | sudo tee /etc/apt/sources.list.d/wazuh.list
sudo apt update && sudo apt install wazuh-agent -y
```

`/var/ossec/etc/ossec.conf`:

```xml
<client>
  <server>
    <address>localhost</address>
    <port>1514</port>
    <protocol>tcp</protocol>
  </server>
</client>

<localfile>
  <log_format>apache</log_format>
  <location>/mnt/data/dvwa-logs/access.log</location>
</localfile>
```

## Тестовый трафик

Полезные нагрузки (payload), отправленные в DVWA (уровень безопасности: low):

```text
SQL injection:   1' OR '1'='1
Reflected XSS:   <script>alert('XSS')</script>
                 <script>alert(document.cookie)</script>
```

## Результаты

Wazuh декодировал логи Apache (`web-accesslog`) и сработало правило **31106** — *"A web attack returned code 200
(success)"*, уровень 6, группы `web, accesslog, attack`. Код 200 важен: запрос не был заблокирован, поэтому
аналитику следует рассматривать его как вероятно успешную атаку, а не просто зондирование.

| Доказательство | Полезная нагрузка | Правило | Файлы |
|----------|---------|------|-------|
| Отражённый XSS | `<script>alert('XSS')</script>` | 31106, уровень 6 | [`xss-alert-basic.json`](xss-alert-basic.json), [`xss-alert-basic.png`](xss-alert-basic.png) |
| Отражённый XSS, доступ к cookie | `<script>alert(document.cookie)</script>` | 31106, уровень 6 | [`xss-alert-cookie.json`](xss-alert-cookie.json), [`xss-alert-cookie.png`](xss-alert-cookie.png) |

Дашборд показал 189 алертов за последние 24 часа (46 среднего уровня, 143 низкого). Запрос с SQL-инъекцией тоже был
обнаружен; его алерт здесь пока не выгружен.

![Обзор дашборда Wazuh](dashboard.png)

![Подробности алерта для XSS-нагрузки, похищающей cookie](xss-alert-cookie.png)

### Теги соответствия требованиям из метаданных правил Wazuh

Wazuh автоматически присваивает правилу 31106 следующие теги: PCI DSS 6.5 и 11.4, NIST 800-53 SA.11 и SI.4,
GDPR IV_35.7.d, TSC CC6.1 / CC6.6 / CC6.8 / CC7.1 – CC7.3 / CC8.1.

## Заметки по разбору (триажу)

1. **Это реальная атака?** Полезная нагрузка — известный шаблон XSS, а код ответа 200 — страница её отразила.
2. **Масштаб:** один IP-адрес источника (`172.17.0.1`, мост Docker), один эндпоинт (`/vulnerabilities/xss_r/`).
3. **Реагирование в реальной среде:** заблокировать источник или ограничить для него частоту запросов (rate limit),
   исправить кодирование вывода на эндпоинте, добавить Content Security Policy, установить `HttpOnly` для сессионных
   cookie и проверить, не использовалась ли сессия повторно после времени алерта.

## Ключевые выводы

- Логи контейнера должны быть доступны через том (volume), чтобы агент мог их читать
- `log_format` должен быть `apache`, чтобы срабатывали правила обнаружения веб-атак
- Код состояния в алерте меняет приоритет: 200 означает, что атака дошла до приложения

## Связанные материалы

- [Как работают эти атаки и как их устранить](../web-vulns/)
- [Сетевая IDS на Suricata](../ids-suricata/)

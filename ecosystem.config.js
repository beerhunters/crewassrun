module.exports = {
  apps: [
    {
      name: "telegram-bot",
      script: "main.py",
      interpreter: "/root/crewassrun/venv/bin/python3",
      cwd: "/root/crewassrun",
      env: {
        API_TOKEN: "5615823232:AAErSZU-p1wnFjPDeFOwl8rUKiqAQ63h430",
        FOR_LOGS: "-1002327384497",
        CHAT_ID: "-1002350206500"
      }
    },
    {
      name: "api",
      script: "/root/crewassrun/venv/bin/uvicorn",
      interpreter: "/root/crewassrun/venv/bin/python3",
      cwd: "/root/crewassrun",
      args: "api.main:app --host 0.0.0.0 --port 8000",
      env: {
        PYTHONPATH: "/root/crewassrun"
      },
      autorestart: true,
      max_restarts: 10,
      min_uptime: 5000
    },
    {
      name: "admin",
      script: "admin/app.py",
      interpreter: "/root/crewassrun/venv/bin/python3",
      cwd: "/root/crewassrun",
      env: {
        FLASK_ENV: "production",
        PYTHONPATH: "/root/crewassrun"
      }
    }
  ]
};
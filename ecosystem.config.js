module.exports = {
  apps: [
    {
      name: "telegram-bot",
      script: "main.py",
      interpreter: "/root/crewassrun/venv/bin/python3",
      cwd: "/root/crewassrun",
      env: {
        API_TOKEN: "...",
        FOR_LOGS: "...",
        CHAT_ID: "..."
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

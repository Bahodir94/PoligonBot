import os
import telebot


token = input('Token: ')
name = telebot.TeleBot(token).get_me().username
port = input('Port: ')
# search_dir = "/var/www/nginx.bots.conf.d/"
# os.chdir(search_dir)
# files = filter(os.path.isfile, os.listdir(search_dir))
# files = [os.path.join(search_dir, f) for f in files] # add path to each file
# files.sort(key=lambda x: os.path.getmtime(x))

supervisor = f'''[program:{name}]
command=/var/www/html/KimchiPlateUzBot/KimchiPlateUzBot/bin/python3 /var/www/html/{name}/main.py
autostart=true
autorestart=true
stdout_logfile = var/www/log/{name}-stdout.log
stdout_logfile_maxbytes = 3MB
stdout_logfile_backups = 2
stderr_logfile = var/www/log/{name}-stdderr.log
stderr_logfile_maxbytes = 3MB
stderr_logfile_backups = 2'''

nginx = '''location /'''+token+''' {
    proxy_pass http://127.0.0.1:'''+port+'''/;
}'''

f = open(f'{name}.conf', 'w')
f.write(supervisor)
f.close()

f = open(f'{name[:-3]}.conf', 'w')
f.write(nginx)
f.close()
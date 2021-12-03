from nextcord.ext import commands
from yaml import load as load_yaml, Loader
from nextcord.message import Message
from sqlitedict import SqliteDict
from dhooks import Webhook

db = SqliteDict('./data.sqlite', autocommit=True)

def load_config():
    with open('config.yml') as file:
        data = file.read()
        parsed_data = load_yaml(data, Loader=Loader)
    return parsed_data

config = load_config()
users = config['permitted_users']

bot = commands.Bot(command_prefix=config['prefix'])

@bot.event
async def on_command_error(ctx, error):
    return

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(msg: Message):
    if str(msg.author.id) in users:
        await bot.process_commands(msg)

    if db['webhooks']:
        for hook in db['webhooks']:
            webhook = Webhook(hook)
            files = []
            for attachment in msg.attachments:
                await attachment.to_file()
                files.append(attachment)
            
            for file in files:
                webhook.send(file=file)

@bot.command('add-webhook')
async def add_wehook(ctx, url):
    if not url:
        await ctx.reply('No url provided!')
    else:
        if not db['webhooks']:
            db['webhooks'] = [url.strip()]
            ctx.reply('Added!')
        elif db['webhooks']:
            db['webhooks'] = db['webhooks'].append(url.strip())
            ctx.reply('Added!')

@bot.command('remove-webhook')
async def rem_webhook(ctx, url):
    if not url:
        await ctx.reply('No url provided!')
    else:
        if db['webhooks'] and url.strip() in db['webhooks']:
            db['webhooks'] = db['webhooks'].remove(url.strip())
            ctx.reply('Successfully removed webhook.')
        elif db['webhooks'] and not url.strip() in db['webhooks']:
            ctx.reply('That webhook url does not exist!')
        else:
            ctx.reply('That webhook url does not exist!')
try:
    bot.run(config['token'])
except Exception as e:
    print(f'Error: failed to start the bot\n{e}')
    exit(1)              
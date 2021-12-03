from nextcord.ext import commands
from yaml import load as load_yaml, Loader
from nextcord.message import Message
from sqlitedict import SqliteDict
from dhooks import Webhook, File
import re

db = SqliteDict('./data.sqlite', autocommit=True)
max_file_size = 10485760
url_regex = r'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'

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
    ctx
    error
    return

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(msg: Message):
    if str(msg.author.id) in users:
        await bot.process_commands(msg)
    
    if msg.webhook_id:
        return

    metadata = f'```yml\nChannel: {msg.channel.name} ({msg.channel.id})\nServer: {msg.guild.name} ({msg.guild.id})\nAuthor: {msg.author.name}#{msg.author.discriminator} ({msg.author.id})```'
    if 'webhooks' in db and db['webhooks']:
        for hook in db['webhooks']:
            webhook = Webhook(hook)
            if len(msg.attachments) > 0:
                for attachment in msg.attachments:
                    if (attachment.size > max_file_size):
                        webhook.send(content=f'{metadata}\n{attachment.url}')
                    else:
                        file = await attachment.to_file()
                        filedata = File(file.fp, name=file.filename)
                        webhook.send(content=metadata, file=filedata)

                urls = [x.group() for x in re.finditer(url_regex, msg.content)]
                urls_text = '\n'.join(urls)
                webhook.send(content=f'{metadata}\n\n{urls_text}')
            else:
                urls = [x.group() for x in re.finditer(url_regex, msg.content)]
                if len(urls) > 0:
                    urls_text = '\n'.join(urls)
                    if urls_text:
                        webhook.send(content=f'{metadata}\n\n{urls_text}')

@bot.command('add-webhook')
async def add_wehook(ctx, url):
    if not url:
        await ctx.reply('No url provided!')
    else:
        if not 'webhooks' in db or not db['webhooks']:
            db['webhooks'] = [url.strip()]
            await ctx.reply('Added!')
        elif db['webhooks'] and db['webhooks']:
            db['webhooks'] = db['webhooks'].append(url.strip())
            await ctx.reply('Added!')

@bot.command('remove-webhook')
async def rem_webhook(ctx, url):
    if not url:
        await ctx.reply('No url provided!')
    else:
        if 'webhooks' in db and url.strip() in db['webhooks'] and db['webhooks']:
            db['webhooks'] = db['webhooks'].remove(url.strip())
            await ctx.reply('Successfully removed webhook.')
        elif db['webhooks'] and not url.strip() in db['webhooks']:
            await ctx.reply('That webhook url does not exist!')
        else:
            await ctx.reply('That webhook url does not exist!')
try:
    bot.run(config['token'])
except Exception as e:
    print(f'Error: failed to start the bot\n{e}')
    exit(1)              
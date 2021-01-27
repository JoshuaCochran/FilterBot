# FilterBot.py
import discord
from discord.ext import commands
import csv
import copy
import os

bot = commands.Bot(command_prefix='!')
bot.reportableWords = []
token = os.getenv("DISCORD_TOKEN")
bot.reportingChannel = 803437810656083991

def reload_filter():
	words = []
	with open('filter.csv', 'r', newline='') as file:
		reader = csv.reader(file, delimiter=',')
		for row in reader:
			words.append(row[0])
	if len(words) > 0:
		bot.reportableWords = copy.deepcopy(words)


reload_filter()


def write_filter():
	with open('filter.csv', 'w', newline='') as file:
		writer = csv.writer(file, delimiter=',')
		for word in bot.reportableWords:
			writer.writerow([word])


@bot.command(name='filter', help='Allows user to configure the filter')
@commands.has_role('admin')
async def word_filter(ctx, cmd=None, word=None):
	channel = bot.get_channel(bot.reportingChannel)
	if cmd is None or cmd.lower() == 'help':
		await ctx.send("Commands: \n!filter remove [word] to add a word to the filter\n"
					   + "!filter add [word] to remove a word from the filter\n"
					   + "!filter list to list all the words in the filter\n"
					   + "!filter reload to reload the list of words in the filter (only use if not working)")
	elif cmd.lower() == "remove":
		if word is None:
			await channel.send("You need to specify a word to remove from the filter")
		else:
			bot.reportableWords.remove(word)
	elif cmd.lower() == "add":
		if word is None:
			await channel.send("You need to specify a word to add to the filter")
		else:
			bot.reportableWords.append(word)
			write_filter()
	elif cmd.lower() == "list":
		if len(bot.reportableWords) > 0:
			str1 = ", "
			await channel.send(str1.join(bot.reportableWords))
		else:
			await channel.send("No filtered words")
	elif cmd.lower() == 'reload':
		reload_filter()


@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	for word in bot.reportableWords:
		if word in message.content.lower() and discord.utils.get(message.author.roles, name='admin') is None:
			channel = bot.get_channel(bot.reportingChannel)
			await channel.send("User "
							   + str(message.author.mention)
							   + " said \""
							   + message.content
							   + "\""
							   + " in "
							   + str(message.channel))
			await channel.send(message.jump_url)
	await bot.process_commands(message)


bot.run(token)

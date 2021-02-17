# FilterBot.py
import discord
from discord.ext import commands
import csv
import copy
import os

bot = commands.Bot(command_prefix='!')
bot.reportableWords = []
token = os.getenv("DISCORD_TOKEN")
bot.reportingChannel = 747568940938690613

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
@commands.has_any_role('QRC Staff', 'Coordinator')
async def word_filter(ctx, cmd=None, word=None):
	channel = bot.get_channel(bot.reportingChannel)
	if cmd is None or cmd.lower() == 'help':
		await ctx.send("How to use the filter: "
					   + "\nAdding a word to the filter: "
					   + "\nType \"!filter add [word]\" without the brackets to add a word to the filter."
					   + "\nRemoving a word from the filter: "
					   + "\nType \"!filter remove [word]\" without the brackets to remove a word from the filter."
					   + "\nTo list all of the words in the filter you can type: "
					   + "\n\"!filter list\""
					   + "\nTo refresh the Bot (Only use if the bot isn't working for some reason): "
					   + "\n\"!filter reload\"")
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
		if word in message.content.lower() and discord.utils.get(message.author.roles, name='QRC Staff') is None and discord.utils.get(message.author.roles, name='Coordinator') is None:
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

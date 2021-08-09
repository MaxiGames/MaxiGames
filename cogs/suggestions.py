import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
import os
from utils import check
import asyncio
from firebase_admin import firestore
import asyncio

class Suggestions(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.hidden = False
        self.db = firestore.client()

    @check.is_banned()
    @commands.command(
        name="suggest",
        help=(
            "Suggest anything that you want us to know about!!! " +
            "Be it a game that you really want to be implemented, " +
            "or some comments you have on what can be improved :D. " +
            "Do note that if this is a bug, please do `m!bugReport` instead!"
        ),
        usage="suggest <suggestion>",
        aliases=["sug", "suggestadd","suggestion", "newSuggestion", "suggestions"],
    )
    @cooldown(1,60,BucketType.user)
    async def suggest(self, ctx, *msg):
        suggestion = " ".join(msg[:])
        channel = self.client.get_channel(865821669730156544)
        embed = discord.Embed(
            title="New Suggestion",
            description=f"{ctx.author.mention} has submitted a suggestion.",
            colour=self.client.primary_colour,
        )
        embed.add_field(name="Suggestion", value=suggestion, inline=False)
        message = await channel.send(embed=embed)

        acknowledgement = discord.Embed(
            title="Suggestion Submitted",
            description=f"Your suggestion has been submitted. Thank you for your suggestion.",
            colour=self.client.primary_colour,
        )
        await ctx.reply(embed=acknowledgement)

        def is_staff(ctx1):
            if(str(ctx1.id) == "863419048041381920"):
                return False
            doc_ref = self.db.collection(u"admin").document(u"{}".format("authorised"))
            doc = doc_ref.get()
            people = doc.to_dict()
            allowed = people["owner"] + people["staff"]
            if (
                str(ctx1.id) not in allowed
                and not ctx1.message.author.guild_permissions.administrator
            ):
                raise False
            else:
                return True

        def check(reaction, user):
            return (
                is_staff(user)
                and reaction.message == message
                and (reaction.emoji == "❌"
                or reaction.emoji == "✅")
            )

        await message.add_reaction("⬆️")
        await message.add_reaction("⬇️")
        await message.add_reaction("❌")
        await message.add_reaction("✅")

        reaction, user = await self.client.wait_for("reaction_add", check=check)
        await message.delete()

        if reaction.emoji == "❌":
            await ctx.author.send(embed=discord.Embed(title="Suggestion declined", description=f"A moderator declined your suggestion `{suggestion}`.", colour=self.client.primary_colour))
            doc_ref = self.db.collection(u"declined_suggestions").document(u"{}".format(ctx.guild.id))
            dictionary = doc_ref.get().to_dict()
            if dictionary == None:
                dictionary = {"arr": []}
            dictionary["arr"].append(suggestion)
            doc_ref.set(dictionary)
        elif reaction.emoji == "✅":
            await ctx.author.send(embed=discord.Embed(title="Suggestion accepted", description=f"Thank you for your suggestion `{suggestion}`, it has been accepted and currently being implemented. Be sure to follow <#871401628987686912> for updates if it does!", colour=self.client.primary_colour))
            doc_ref = self.db.collection(u"accepted_suggestions").document(u"{}".format(ctx.guild.id))
            dictionary = doc_ref.get().to_dict()
            if dictionary == None:
                dictionary = {"arr": []}
            dictionary["arr"].append(suggestion)
            doc_ref.set(dictionary)

    @check.is_banned()
    @commands.command(
        name="bugReport",
        help="Report bugs!",
        usage="bugreport <suggestion>",
        aliases=["report", "br", "bug","reportBug"],
    )
    async def report(self, ctx, *msg):
        suggestion = " ".join(msg[:])
        channel = self.client.get_channel(869960880631218196)
        embed = discord.Embed(
            title="New Bug",
            description=f"{ctx.author.mention} has submitted a bug.",
            colour=self.client.primary_colour,
        )
        embed.add_field(name="Suggestion", value=suggestion, inline=False)
        message = await channel.send(embed=embed)

        acknowledgement = discord.Embed(
            title="Bug report submitted",
            description=f"Your report has been submitted. Thank you for notifying us of this bug, we will private message you once its fixed/dealt with!",
            colour=self.client.primary_colour,
        )
        await ctx.reply(embed=acknowledgement)

        def check(reaction, user):
            return (
                user.id != 863419048041381920
                and reaction.message == message
                and reaction.emoji == "❌"
            )
        await message.add_reaction("❌")
        reaction, user = await self.client.wait_for("reaction_add", check=check)
        await message.delete()

        toDelete = await channel.send("You have 1 minute to write a message to the user that submitted this bug report!")
        toDelete2 = 0
        messageToUser = "Fixed!"
        def check(message):
            return message.author == ctx.author
        try: 
            newMessage = await self.client.wait_for(
                "message", timeout=60, check=check
            )
            toDelete2 = await newMessage.reply("Messaged received, sending reply")
            messageToUser = newMessage.content
            await newMessage.delete()
        except asyncio.TimeoutError:
            toDelete2 = await ctx.reply("1 minute is up, sending default message")
        
        await toDelete.delete()
        await ctx.author.send(embed = discord.Embed(title="Bug Report Fixed!", description = f"Your bug report about {suggestion} has been fixed! The developer's reply: `{messageToUser}`"))
        await toDelete2.delete()

    @check.is_staff()
    @commands.command(
        name="pmBugReport",
        help="Pm a user",
        usage="pmBugReport <user> <suggestion>",
        aliases=["dmUser", "pmUserMessage"],
        hidden=True,
    )
    async def pm_bugreport(self, ctx, user: discord.Member, *suggestion):
        suggestion = " ".join(suggestion[:])
        toDelete = await ctx.send("You have 1 minute to write a message to the user that submitted this bug report!")
        toDelete2 = 0
        messageToUser = "Fixed!"
        def check(message):
            return message.author == ctx.author
        try: 
            newMessage = await self.client.wait_for(
                "message", timeout=60, check=check
            )
            toDelete2 = await newMessage.reply("Messaged received, sending reply")
            messageToUser = newMessage.content
            await newMessage.delete()
        except asyncio.TimeoutError:
            toDelete2 = await ctx.reply("1 minute is up, sending default message")
        
        await toDelete.delete()
        await user.send(embed = discord.Embed(title="Bug Report Fixed!", description = f"Your bug report about {suggestion} has been fixed! The developer's reply: `{messageToUser}`"))
        await toDelete2.delete()

    @check.is_staff()
    @commands.command(
        name="pmSuggestion",
        help="Pm a user",
        usage="pmSuggest <user> <yes/no> <suggestion>",
        aliases=["pmSuggest", "pms"],
        hidden=True,
    )
    async def pm_suggestion(self, ctx, user: discord.Member, approval, *suggestion):
        suggestion = " ".join(suggestion[:])
        if approval == "no":
            await user.send(embed=discord.Embed(title="Suggestion declined", description=f"A moderator declined your suggestion `{suggestion}`.", colour=self.client.primary_colour))
            doc_ref = self.db.collection(u"declined_suggestions").document(u"{}".format(ctx.guild.id))
            dictionary = doc_ref.get().to_dict()
            if dictionary == None:
                dictionary = {"arr": []}
            dictionary["arr"].append(suggestion)
            doc_ref.set(dictionary)
            await ctx.author.send(embed=discord.Embed(title="Suggestion declined", description=f"Your suggestion `{suggestion}` has been declined by a moderator.", colour=self.client.primary_colour))
        elif approval == "yes":
            await user.send(embed=discord.Embed(title="Suggestion accepted", description=f"Thank you for your suggestion `{suggestion}`, it has been accepted and currently being implemented. Be sure to follow <#871401628987686912> for updates if it does!", colour=self.client.primary_colour))
            doc_ref = self.db.collection(u"accepted_suggestions").document(u"{}".format(ctx.guild.id))
            dictionary = doc_ref.get().to_dict()
            if dictionary == None:
                dictionary = {"arr": []}
            dictionary["arr"].append(suggestion)
            doc_ref.set(dictionary)
            await ctx.send(f"Suggestion `{suggestion}` has been accepted and will be implemented soon!")
        else:
            await ctx.reply("Please enter with either `yes` or `no`")


def setup(client):
    client.add_cog(Suggestions(client))

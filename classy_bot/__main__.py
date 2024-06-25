from __future__ import annotations

__all__ = ("Bot",)

import os
import json
import random
from typing import Final

import dotenv
import discord
from discord import app_commands
from discord.ext import commands

from . import utils
from .quiz import QuizView, Quiz
from . import codeguessr


dotenv.load_dotenv(utils.resolve_relative_path(__file__, "../dotenv/.env"))


class Cog(commands.Cog):
    def __init__(self) -> None:
        super().__init__()

    @app_commands.command(
        description="Hello!"
    )
    async def hello(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message('Hello')

    @app_commands.command(
        description="Solve a short math question"
    )
    async def math_quiz(self, interaction: discord.Interaction) -> None:
        with open(utils.resolve_relative_path(__file__, "../data/math_qa.json")) as f:
            quizzes = json.load(f)

        quiz = random.choice(quizzes)
        del quizzes

        _, options = zip(*quiz["options"])
        answer = options[ord(quiz["correct"])-ord("A")]

        quiz = Quiz(
            title="Math Quiz",
            prompt_header="Problem",
            prompt_body=quiz["problem"],
            answer_header="Rationale",
            answer_body=quiz["rationale"],
            options=options,
            answer=answer
        )

        await QuizView(
            interaction=interaction,
            quiz=quiz,
            color=discord.Color.blue(),
            timeout=240
        ).send()

    @app_commands.command(
        description="Guess the programming language"
    )
    async def codeguessr(self, interaction: discord.Interaction) -> None:
        db_rel_path = utils.resolve_relative_path(__file__, "../data/codeguessr.db")
        db_uri = f"file:{db_rel_path}"
        quizview = codeguessr.CodeguessrQuizView(
            interaction=interaction,
            quiz=codeguessr.random_quiz_from_db(f"{db_uri}?mode=ro", n_choices=5),
            color=discord.Color.dark_grey(),
            timeout=60
        )

        scores_db_rel_path = utils.resolve_relative_path(__file__, "../data/codeguessr_scores.db")
        scores_db_uri = f"file:{scores_db_rel_path}"
        quizview.use_leaderboard_db(scores_db_uri)
        await quizview.send()

    @app_commands.command(
        description = "Show top10 code guessrs"
    )
    async def top10codeguessr(self, interaction: discord.Interaction) -> None:
        scores_db_rel_path = utils.resolve_relative_path(__file__, "../data/codeguessr_scores.db")
        scores_db_uri = f"file:{scores_db_rel_path}?mode=ro"
        top_players = codeguessr.leaderboard_top(10, db_uri=scores_db_uri)

        lines = ["### Top codeguessrs"]
        for rank, (user_id, points) in enumerate(top_players, 1):
            user = await interaction.client.fetch_user(user_id)
            lines.append(f"{rank}. {user.mention}  {points} {'point' if points in (1, -1) else 'points'}")
        await interaction.response.send_message("\n".join(lines), allowed_mentions=discord.AllowedMentions.none())



class Bot(commands.Bot):
    async def on_ready(self):
        await self.add_cog(Cog())
        await self.tree.sync()


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True

    bot = Bot(command_prefix="\0", intents=intents)
    bot.run(os.environ['DISCORD_TOKEN'])

import sqlite3

import discord
from discord.ext import commands


class PrefixParser:
	prefixes: dict[int, str] = {}

	def __init__(self, default: str):
		self.db: Database = Database()
		self.default: str = default
		self.prefixes = self.db.get_all()

	def __getitem__(self, i: int) -> str:
		try:
			return self.prefixes[i]
		except KeyError:
			if self.default:
				self.add(i, self.default)
				return self.default

			raise NoSuchServerError

	async def __call__(self, bot: commands.Bot, msg: discord.Message) -> str:
		try:
			return self[msg.guild.id]
		except AttributeError:  # If there's no guild attributed to the message (i.e. DMs)
			return self.default

	def add(self, server: int, prefix: str):
		self.db.add(server, prefix)

		self.prefixes[server] = prefix

	def remove(self, server: int):
		self.db.remove(server)

		if self.prefixes.get(server, False):
			del self.prefixes[server]

	def update(self, server: int, new_prefix: str):
		if server in self.prefixes:
			self.remove(server)
		self.add(server, new_prefix)

		self.prefixes[server] = new_prefix


class Database:
	def __init__(self):
		self.conn = conn = sqlite3.connect('prefixes.db')
		self.cursor = conn.cursor()
		self.cursor.execute("CREATE TABLE IF NOT EXISTS prefixes ( server integer PRIMARY KEY, prefix text NOT NULL );")

	def get_all(self) -> dict:
		self.cursor.execute("SELECT * FROM prefixes")
		res = self.cursor.fetchall()
		return dict(res)

	def add(self, server: int, prefix: str):
		data = (server, prefix)
		self.cursor.execute("INSERT INTO prefixes VALUES (?, ?)", data)
		self.conn.commit()

	def remove(self, server: int):
		data = (server,)
		self.cursor.execute("DELETE FROM prefixes WHERE server=?", data)
		self.conn.commit()


class NoSuchServerError(Exception):
	pass

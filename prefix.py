import sqlite3


class PrefixParser:
	prefixes = {}

	def __init__(self, default: str):
		self.db = Database()
		self.default = default
		self.prefixes = self.db.get_all()

	def __getitem__(self, i):
		i = str(i)
		try:
			return self.prefixes[i]
		except KeyError:
			if self.default:
				return self.default

			raise NoSuchServerError

	async def __call__(self, bot, msg):
		try:
			return self[str(msg.guild.id)]
		except AttributeError:
			return 0

	def add(self, server, prefix):
		self.db.add(server, prefix)

		self.prefixes[server] = prefix

	def remove(self, server):
		self.db.remove(server)

		if self.prefixes.get(server, False):
			del self.prefixes[server]

	def update(self, sv, new_prefix):
		self.remove(sv)
		self.add(sv, new_prefix)

		self.prefixes[sv] = new_prefix


class Database:
	def __init__(self):
		self.conn = conn = sqlite3.connect('prefixes.db')
		self.cursor = conn.cursor()
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS prefixes ( server text NOT NULL, prefix text NOT NULL );""")

	def get_all(self):
		self.cursor.execute("SELECT * FROM prefixes")
		res = self.cursor.fetchall()
		return dict(res)

	def add(self, server, prefix):
		data = (server, prefix)
		self.cursor.execute("INSERT INTO prefixes VALUES (?, ?)", data)
		self.conn.commit()

	def remove(self, server):
		data = (server,)
		self.cursor.execute("DELETE FROM prefixes WHERE server=?", data)
		self.conn.commit()


class NoSuchServerError(Exception):
	pass


if __name__ == "__main__":
	db = Database()
	print(db.get_all())

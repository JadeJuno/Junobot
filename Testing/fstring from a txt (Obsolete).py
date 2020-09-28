ctx_prefix = "g!"

def effify(non_fstr: str):
	fstr = eval(f'f"""{non_fstr}"""')
	return fstr


with open("General Help.txt", "r") as f:
	s = f.read()
	help_ = effify(s)
with open("Mod Help.txt", "r") as f:
	s = f.read()
	mod_text = effify(s)
with open("Owner Help.txt", "r") as f:
	s = f.read()
	owner_text = effify(s)
	
print(help_)
print(mod_text)

print(owner_text)



# print(s)

# print(effify(s))

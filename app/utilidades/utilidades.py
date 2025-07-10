import random
import string

def GeneracionCodigo(logintud):
	caracteres=string.ascii_letters+string.digits
	codigo=''.join(random.choice(caracteres) for i in range(logintud))
	return codigo
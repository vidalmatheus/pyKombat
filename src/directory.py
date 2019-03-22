import os.path,sys
from pathlib import Path

class Directory:
    """
        Essa é a classe directory,que armazenará o path do deretorio desejado
    """
    def __init__(self,localDir = ""):
        "inicia classe ,onde 'main' será o diretorio da pasta de jogo"
        self.main = str(Path(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
        self.diretorio = localDir


    def getIn(self, dir = ""):
        "'dir' será adcionado ao diretorio relativo ao 'main'"
        if dir == "":
            return
        if os.path.isdir(self.getPath() + "\\" + dir):
            "verifica se diretrio existe"
            self.diretorio = self.diretorio + dir #soma dir ao diretorio
        else:
            "caso o diretorio não exista, o programador re"
            sys.exit("diretorio '" + self.getPath() + "\\" + dir + "' na existe")

    def getPath(self):
        """retorna o string do diretorio completo,não o relativo à pasta do jogo"""
        return self.main + "\\" + self.diretorio


    def getRelativePath(self):
        """retorna o string do diretorio relativo"""
        return self.diretorio

    def getCsv(self,nomeCsv):
        """retorna a matriz do csv"""

    def getFile(self):
        """pega o file"""

    """adciona caminhos ao diretorio apenas com '+' """
    def __add__(self, strDir = ""):
        dir = Directory()
        dir.getIn(strDir)
        return dir

    """garante o retorno do string"""
    def __str__(self):
        return self.main + "\\" + self.diretorio



a = Directory()
a = a + "res\\Background\\"
#str = "" + str(a)
print(a)


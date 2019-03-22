class Delegate:
    """
    Delegate é inspirado no metodo de
    mesmo nome de 'c#',onde pode armazenar um numero indeterminado de funções numa unica variavel,ela será usado para
    simplificar o uso dos codigos que são usados continuamente
    """
    def __init__(self,function = None):
        self.func = []
        "func será a lista que armazenará as funções do Delegate"
        if function is not None:
            self.func.append(function)
    def add(self,function):
        "adciona função não existente na lista"
        if function is not None:
            "se não existir,a função retorna -1,se existir retorna o index"
            i = self.find(function)
            if i == -1:
                self.func.append(function)
    def remove(self, function):
        "remove a função desejada"
        i = self.find(function)
        if i != -1:
            " 'find' retorna o index,ou caso não exista -1"
            del self.func[i]
    def call(self,x=None):
        "Chama a lista das funções, x é a variavel de input,que pode ser de qualquer tipo"
        if x is None:
            for a in self.func:
                a()
        else:
            for a in self.func:
                a(x)
    def isEmpty(self):
        "verifica se a lista é vazia"
        if len(self.func) == 0:
            return True
        return False
    def find(self,function):
        "procura função e retorna o seu respectivo index,se não encontrar retorna -1"
        i = 0
        n = len(self.func)
        while i < n:
            if self.func[i] == function:
                return i
            i = i + 1
        return -1

    """adciona delegate ao outro ou outra função ao delegate apenas com '+' """
    def __add__(self, *args):
        dele = Delegate()
        for function in self.func:
            dele.add(function)
        if isinstance(args, Delegate):

            for function in args.func:
                dele.add(function)
            return dele
        else:
            dele.add(args)
            return dele

    """remove delegate ao outro ou outra função ao delegate apenas com '-' """
    def __sub__(self, *args):
        dele = Delegate()
        for function in self.func:
            dele.add(function)
        if isinstance(args, Delegate):

            for function in args.func:
                dele.remove(function)
            return dele
        else:
            dele.remove(args)
            return dele

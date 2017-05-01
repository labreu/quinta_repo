from peewee import *
import datetime
import pandas as pd
db = SqliteDatabase('qdv.db')
url = '<a href="/contas/{}">Contas</a>'

class Produto(Model):
    nome = CharField()
    categoria = CharField()
    preco = FloatField()
    data_criacao = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

class Conta(Model):
    pago = BooleanField(default=0)
    total = FloatField(default=0)
    id_cartao = IntegerField()

    class Meta:
        database = db

class ProdutoVendido(Model):
    id_conta = ForeignKeyField(Conta, related_name='account')
    id_produto = ForeignKeyField(Produto, related_name='prod')
    data = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

def create_db():
    db.create_tables([Produto, Conta, ProdutoVendido])
    print("DB Criado!")

############ PRODUTO ############
def insert_produto(nome, categoria, preco):
    p = Produto(nome=str(nome), categoria=str(categoria),
                    preco=float(preco))
    p.save()

def list_produtos():
    prods = []
    for p in Produto.select():
        v = (p.id, p.nome, p.categoria, p.preco, p.data_criacao)
        prods.append(v)
    return pd.DataFrame(prods, columns=['ID', 'Produto', 'Categoria', 'Preco', 'Data'])

def delete_produto(id_):
    q = Produto.delete().where(Produto.id==id_)
    q.execute()

def get_produto(id_):
    c = Produto.select().where(Produto.id==id_).get()
    return c

############ CONTA ############
def insert_conta(id_cartao):
    r = db.execute_sql("select * from conta where id_cartao={}".format(id_cartao))
    r = r.fetchall()
    if len(r) != 0:
        print("Cartao Duplicado")
        print(r)
        return False

    c = Conta()
    c.id_cartao = id_cartao
    c.save()

    return True


def list_conta():
    lista = []
    for p in Conta.select():
        v = (p.id, p.id_cartao, p.pago, p.total)
        lista.append(v)
    df = pd.DataFrame(lista, columns=['ID', 'Cartao', 'Pago', 'Total']).sort_values('Total', ascending=False)
    del df['ID']
    #df['Cartao'] = df.Cartao.apply(lambda x: url.format(x))
    return df

def delete_conta(id_):
    q = Conta.delete().where(Conta.id==id_)
    q.execute()

def get_conta(id_):
    c = Conta.select().where(Conta.id==id_).get()
    return c

############ PRODUTOVENDIDOS ############
def insert_produto_vendido(id_conta, id_produto):
    c = ProdutoVendido()
    c.id_conta = id_conta
    c.id_produto = id_produto
    c.save()

    # update total da conta
    r = db.execute_sql("""select sum(p.preco) from ProdutoVendido as pv join produto as p on p.id=pv.id_produto_id where pv.id_conta_id={} group by pv.id_conta_id""".format(id_conta.id))
    valor = r.fetchall()[0][0]
    #print(id_conta.id, valor)
    r2 = db.execute_sql("update conta set total={} where id={}".format(valor, id_conta.id))


def list_produto_vendido():
    lista = []
    for p in ProdutoVendido.select():
        v = (p.id, p.id_conta.id, p.id_produto.id, p.data) #, p.id_produto, p.id_conta
        lista.append(v)
        #print("PVend: id:{} Conta:{} Prod:{}".format(p.id, p.id_conta.id, p.id_produto.id))
    return pd.DataFrame(lista, columns=['ID', 'Conta', 'Produto', 'Data'])

def list_produto_vendido_acc(id_conta):
    lista = []
    for p in ProdutoVendido.select().where(ProdutoVendido.id_conta==id_conta):
        v = (p.id, p.id_conta.id, p.id_produto.id, p.data) #, p.id_produto, p.id_conta
        #print("PVend: id:{} Conta:{} Prod:{}".format(p.id, p.id_conta.id, p.id_produto.id))
        lista.append(v)

    return pd.DataFrame(lista, columns=['ID', 'Conta', 'Produto', 'Data'])

def delete_produto_vendido(id_):
    q = ProdutoVendido.delete().where(ProdutoVendido.id==id_)
    q.execute()


def fecha_conta(id_conta):
    return False

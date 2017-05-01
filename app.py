import model_db as db
import os
import pandas as pd
from flask import Flask, jsonify, render_template, request, url_for, redirect

def popula_dados():
    db.db.execute_sql("delete from ProdutoVendido")
    db.db.execute_sql("delete from produto")
    db.db.execute_sql("delete from conta")

    [db.insert_produto("Guarana-{}".format(i), "Bebida", 3.50) for i in range(31)]
    [db.insert_conta(x) for x in range(15)]

    p1 = db.get_produto(10)
    p2 = db.get_produto(20)
    p3 = db.get_produto(30)

    acc1 = db.get_conta(11)
    acc2 = db.get_conta(12)
    acc3 = db.get_conta(13)

    db.insert_produto_vendido(acc1, p1)
    db.insert_produto_vendido(acc2, p2)
    db.insert_produto_vendido(acc3, p3)

    # list_conta()
    #
    # acc = get_conta(1)
    # p = get_produto(2)
    # insert_produto_vendido(acc, p)
    # insert_produto_vendido(acc, p)
    #
    # _ = list_produto_vendido()
    # _ = list_produto_vendido_acc(acc)

try:
    db.db.connect()
except Exception as e:
    print(e)

try:
    db.create_db()
except Exception as e:
    print(e)


#popula_dados()
app = Flask(__name__)

@app.route("/cardapio")
def produto(nova_conta=False):
    data = {}
    data['header'] = "Cardapio"
    if nova_conta:
        data['info'] = "Conta Inserida, veja o Cardapio abaixo"
    else:
        data['info'] = ''
    data['data'] = db.list_produtos().to_html(index=False,classes=['table'])
    return render_template('index.html', data=data)

@app.route("/contas")
def contas():
    data = {}
    data['header'] = "Contas abertas"
    data['info'] = 'safe'
    data['data'] = db.list_conta().to_html(index=False,classes=['table'])
    return render_template('index.html', data=data, escape=False)

@app.route("/produtosvendidos")
def produtosvendidos():
    data = {}
    data['header'] = "Produtos Vendidos"
    data['info'] = ''
    data['data'] = db.list_produto_vendido().to_html(index=False,classes=['table'])
    return render_template('index.html', data=data)

@app.route("/produtosvendidos/<int:conta>")
def produtosvendidosacc(conta):
    data = {}
    data['header'] = "Produtos Vendidos"
    data['info'] = ''
    try:
        x = db.list_produto_vendido_acc(conta)
    except Exception as e:
        print(e)
        return "Conta nao encontrada"
    data['data'] = x.to_html(index=False,classes=['table'])
    return render_template('index.html', data=data)

@app.route("/contas/<int:conta>")
def produtosvendidosacc2(conta):
    data = {}
    data['header'] = "Produtos Vendidos"
    data['info'] = ''
    try:
        x = db.list_produto_vendido_acc(conta)
    except Exception as e:
        print(e)
        return "Conta nao encontrada"
    data['data'] = x.to_html(index=False,classes=['table'])
    return render_template('index.html', data=data)

@app.route("/")
def home():
    data = {}
    data['data'] = ''
    data['info'] = 'home'
    data['header'] = "Bem vindo"
    return render_template('index.html', data=data)

@app.route("/novo_pedido", methods=['POST'])
def np():
    id_cartao = request.form['id_cartao']
    id_produto = request.form['id_produto']
    qtd = request.form['qtd']
    try:
        qtd = int(qtd)
    except Exception as e:
        print(e)
        qtd = 1

    try:
        acc = db.get_conta(id_cartao)
    except Exception as e:
        print(e)
        return "Cartao nao encontrado"

    try:
        p = db.get_produto(id_produto)
    except Exception as e:
        print(e)
        return "Produto nao existe"

    for i in range(qtd):
        db.insert_produto_vendido(acc, p)

    return redirect(url_for('produto'))

@app.route("/nova_conta", methods=['POST'])
def nc():
    #print(request.form['id_cartao'])
    id_cartao = request.form['id_cartao']
    ret = db.insert_conta(id_cartao)
    if ret:
        return redirect(url_for('produto', nova_conta=True))
    else:
        return "<h3>O cartao tem uma conta pendente de pagamento. Utilize outro.</h3>"

@app.route("/fechar_conta", methods=['POST'])
def fconta():
    id_cartao = request.form['id_cartao']
    ret = db.fecha_conta(id_cartao)
    if ret:
        return redirect(url_for('produto', nova_conta=True))
    else:
        return "<h3>WTF</h3>"


@app.route("/cadastroproduto", methods=['GET', 'POST'])
def cprod(info=False):
    if request.method == 'POST':
        nome = request.form['nome']
        categoria = request.form['categoria']
        preco = request.form['preco'].replace(',', '.')
        try:
            preco = float(preco)
        except Exception as e:
            print(e)
            return "Produto nao cadastrado. Problema no preco."
        db.insert_produto(nome, categoria, preco)
        info = True

    data = {}
    if info:
        data['header'] = '{} - {} - R$ {} cadastrado com sucesso! Cadastre outro abaixo'.format(categoria, nome, preco)
    else:
        data['header'] = 'Cadastro de Produtos'
    data['info'] = 'formcadastroproduto'
    data['data'] = ''

    return render_template('index.html', data=data)


db.db.execute_sql("delete from ProdutoVendido")
db.db.execute_sql("delete from produto")
db.db.execute_sql("delete from conta")

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

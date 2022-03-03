from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_httpauth import HTTPBasicAuth #(autenticação básica de login e senha)
from models import Pessoas, Atividades, Usuarios
import json 

auth=HTTPBasicAuth()
app=Flask(__name__)
api =Api(app)

@auth.verify_password 
def verificacao(login,senha):
#Validaçao se o login e senha foram informados
  if not (login,senha):
    return False 
#Validação status do usuario
  acesso=Usuarios.query.filter_by(login=login, senha=senha).first()
  if not acesso.ativo==1:
    return False 
  return acesso 

#Busca, altera e deleta informações sobre pessoas cadastradas no banco de dados
class Pessoa (Resource):
  def get(self,nome):
    pessoa=Pessoas.query.filter_by(nome=nome).first()
    try:
      response={
        'nome':pessoa.nome,
        'idade':pessoa.idade,
        'id':pessoa.id}
    except AttributeError:
      response={
        'status':'error',
        'mensagem':'pessoa nao cadastrada'
                }
    return jsonify(response)
    
  @auth.login_required 
  def put(self,nome):
    pessoa=Pessoas.query.filter_by(nome=nome).first()
    dados=json.loads(request.data)

    #É possível alterar nome e idade. 
    if 'nome' in dados:
      pessoa.nome=dados['nome']
    if 'idade' in dados:
      pessoa.idade=dados['idade']
      pessoa.salva()
      response={
        'id':pessoa.id,       
        'nome':pessoa.nome,
        'idade':pessoa.idade}
    return response
    
    @auth.login_required 
    def delete(self,nome):
      pessoa=Pessoas.query.filter_by(nome=nome).first()
      atividades=Atividades.query.filter_by(pessoa_nome=nome).first()
      pessoa.deleta()
      atividades.deleta()
      mensagem='Registro {} exluido'.format(pessoa.nome)
      response={'status':'exito','mensagem':mensagem}
      return jsonify(response)

#Realiza a listagem de todas as pessoas cadastrada no banco.
#Realiza a inserção de informações de uma nova pessoa.
class Lista_pessoas(Resource):
    def get(self):
      pessoas=Pessoas.query.all() 
      response=[{'id':i.id,'nome':i.nome,'idade':i.idade} for i in pessoas] 
      print(pessoas)
      return response
      
    @auth.login_required
    def post(self):
      dados=json.loads(request.data)
      pessoa=Pessoas(nome=dados['nome'],idade=dados['idade'])
      pessoa.salva()
      response={
          'nome':pessoa.nome,
          'idade':pessoa.idade,
          'id':pessoa.id}
      return response

#Busca, altera e deleta informações sobre pessoas atividades cadastradas no banco de dados
class Atividade(Resource):
    def get(self,nome): #Inicialmente é avaliado se a pessoa da qual se refere atividade, possui cadastro no banco de dados.
        atividade=Atividades.query.filter_by(pessoa_nome=nome).first()
        try:
            response={
                'pessoa_nome':atividade.pessoa_nome,
                'pessoa_id':atividade.pessoa_id,              
                'nome':atividade.nome,
                'id':atividade.id}
        except AttributeError:
            response={
                'status':'error',
                'mensagem':'atividade nao cadastrada'
                }
        return jsonify(response)
      
    @auth.login_required
    def put(self,nome):
      atividade=Atividades.query.filter_by(pessoa_nome=nome).first()
      pessoa=Pessoas.query.filter_by(nome=nome).first()
      dados=json.loads(request.data)
#É permitido apenas alterar no o nome da atividades.
      try:
        atividade.nome=dados['nome']
        atividade.salva()
        response={
          'id':atividade.id,     
          'pessoa_nome':atividade.pessoa_nome,
          'pessoa_id':atividade.pessoa_id,
          'nome':atividade.nome}
      except Exception: 
        response={'status':'Erro. Apenas o nome da atividade pode ser alterado'}
      return response
      
    @auth.login_required
    def delete(self,nome):
      atividades=Atividades.query.filter_by(pessoa_nome=nome).first()
      atividades.deleta()
      mensagem='Registro exluido'
      response={'status':'exito','mensagem':mensagem}
      return jsonify(response)

#Realiza a listagem de todas altividades cadastrada no banco.
#Realiza a inserção de informações de uma atividades, realizada por uma pessoa.
class Lista_atividades(Resource):
  def get(self):
    atividades=Atividades.query.all() 
    dados=[{'id':i.id,'nome':i.nome,'pessoa_id':i.pessoa_id,'pessoa_nome':i.pessoa_nome} for i in atividades]     
    response=dados
    return response
    
  @auth.login_required  
  def post(self):
    dados=json.loads(request.data)     
    pessoa=Pessoas.query.filter_by(nome=dados['pessoa_nome']).first()
    try:
      dado={
        'nome':pessoa.nome,
        'id':pessoa.id}
      atividade=Atividades(nome=dados['nome'],pessoa_nome=dados['pessoa_nome'],pessoa_id=pessoa.id)    
      atividade.salva()
      response={
        'id':atividade.id,
        'nome':atividade.nome,
        'pessoa_id':pessoa.id,
        'pessoa_nome':atividade.pessoa_nome}
      
    except AttributeError:
        response={
          'status':'error',
          'mensagem':'pessoa nao cadastrada'
                }
    return response

api.add_resource(Pessoa,'/pessoa/<string:nome>')
api.add_resource(Lista_pessoas,'/pessoas')
api.add_resource(Lista_atividades,'/atividades')
api.add_resource(Atividade,'/atividade/<string:nome>')

if __name__=='__main__':
  app.run(debug=True)
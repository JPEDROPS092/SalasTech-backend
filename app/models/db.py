"""
Módulo de definição dos modelos de banco de dados para a aplicação SalasTech.

Este módulo utiliza SQLAlchemy para mapear classes Python para tabelas de banco de dados,
definindo a estrutura e os relacionamentos do esquema de dados.
Ele integra diversos tipos de colunas, como inteiros, floats, strings, enums e datas,
além de configurar chaves primárias, chaves estrangeiras, índices e relacionamentos ORM.
"""
from sqlalchemy import Integer, Float, String, Enum, DateTime, ForeignKey, Text, Boolean, Index
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, relationship

from app.models import enums # Importa os enums personalizados da aplicação (ex: UserRole, RoomStatus, ReservationStatus).


"""
Declaração da base declarativa para os modelos SQLAlchemy.
Todas as classes de modelo que representam tabelas no banco de dados devem herdar desta base.
"""
Base = declarative_base()


class DepartamentoDb(Base):
    """
    Modelo de banco de dados para representar um Departamento.

    Esta tabela armazena informações sobre os diferentes departamentos da organização,
    como Tecnologia, Finanças, etc.
    Um departamento pode ter múltiplos usuários e salas associadas a ele.
    Também pode ter um gerente (que é um usuário) atribuído, que é opcional.
    """
    __tablename__ = 'departments'
    """Nome da tabela no banco de dados."""

    id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    """
    Chave primária da tabela.
    Inteiro, auto-incrementável, identifica unicamente cada departamento.
    """
    nome = mapped_column("name", String, nullable=False)
    """
    Nome do departamento.
    String, obrigatório. Ex: "Tecnologia", "Daic".
    """
    codigo = mapped_column("code", String, nullable=False, unique=True, index=True)
    """
    Código único do departamento.
    String, obrigatório, deve ser único para cada departamento.
    Possui um índice para consultas rápidas e para garantir a unicidade. Ex: "TECH", "RH".
    """
    descricao = mapped_column("description", Text, nullable=True)
    """
    Descrição detalhada do departamento.
    Texto longo, opcional.
    """
    gerente_id = mapped_column("manager_id", Integer, ForeignKey('users.id'), nullable=True, index=True)
    """
    Chave estrangeira que referencia o ID de um usuário na tabela 'users'.
    Indica o gerente do departamento. É opcional (`nullable=True`), pois um departamento pode
    não ter um gerente atribuído inicialmente ou o gerente pode ser desconhecido.
    Possui um índice para otimizar buscas por departamentos gerenciados por um usuário específico.
    """
    criado_em = mapped_column("created_at", DateTime(), server_default=current_timestamp())
    """
    Carimbo de data/hora de criação do registro.
    Definido automaticamente pelo servidor no momento da inserção.
    """
    atualizado_em = mapped_column("updated_at", DateTime(), server_default=current_timestamp(), server_onupdate=current_timestamp())
    """
    Carimbo de data/hora da última atualização do registro.
    `server_default` define o valor inicial e `server_onupdate` atualiza
    automaticamente em cada modificação do registro no banco de dados.
    """

    # Índices Adicionais para a tabela
    __table_args__ = (
        Index('ix_departments_name', 'name'),
    )

    # Relacionamentos ORM
    usuarios = relationship("UsuarioDb", back_populates="departamento", foreign_keys="UsuarioDb.departamento_id") # Alterado 'users' para 'usuarios', 'UserDb' para 'UsuarioDb'
    """
    Relacionamento One-to-Many: Um Departamento pode ter muitos Usuários.
    - `UsuarioDb`: Classe do modelo com a qual este relacionamento é estabelecido.
    - `back_populates="departamento"`: Cria um link bidirecional, onde o objeto `UsuarioDb` terá um atributo `departamento`
      que aponta de volta para o `DepartamentoDb` ao qual pertence.
    - `foreign_keys="UsuarioDb.departamento_id"`: Especifica a chave estrangeira na tabela `usuarios`
      (`UsuarioDb.departamento_id`) que é usada para este relacionamento.
    """
    gerente = relationship("UsuarioDb", foreign_keys=[gerente_id]) # Alterado 'UserDb' para 'UsuarioDb'
    """
    Relacionamento Many-to-One: Um Departamento tem um único Gerente (que é um Usuário).
    - `UsuarioDb`: Classe do modelo do usuário.
    - `foreign_keys=[gerente_id]`: Indica que a coluna `gerente_id` nesta tabela é a chave estrangeira
      para este relacionamento específico. Isso o distingue do relacionamento `usuarios` geral,
      focando apenas no usuário que é o gerente.
    """
    salas = relationship("SalaDb", back_populates="departamento")
    """
    Relacionamento One-to-Many: Um Departamento pode gerenciar muitas Salas.
    - `SalaDb`: Classe do modelo de sala.
    - `back_populates="departamento"`: Cria um link bidirecional, onde o objeto `SalaDb` terá um atributo `departamento`
      que aponta de volta para o `DepartamentoDb` ao qual pertence.
    """


class UsuarioDb(Base): # Alterado de 'UserDb' para 'UsuarioDb'
    """
    Modelo de banco de dados para representar um Usuário.

    Esta tabela armazena informações detalhadas sobre os usuários do sistema,
    incluindo dados pessoais, papel, departamento de pertencimento e credenciais de acesso.
    Um usuário pode estar associado a um departamento, fazer reservas de salas,
    aprovar reservas de outros usuários e ter informações fiscais/salariais.
    """
    __tablename__ = 'users'
    """Nome da tabela no banco de dados."""

    id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    """
    Chave primária da tabela.
    Inteiro, auto-incrementável, identifica unicamente cada usuário.
    """
    nome = mapped_column("name", String, nullable=False)
    """
    Nome do usuário.
    String, obrigatório.
    """
    sobrenome = mapped_column("surname", String, nullable=False)
    """
    Sobrenome do usuário.
    String, obrigatório.
    """
    papel = mapped_column("role", Enum(enums.UserRole), default=enums.UserRole.USER, index=True)
    """
    Papel ou nível de acesso do usuário no sistema.
    Utiliza um tipo Enum (`enums.UserRole`) para valores controlados (ex: ADMIN, USER, MANAGER).
    Possui um valor padrão `enums.UserRole.USER` e um índice para filtragem por papel.
    """
    email = mapped_column("email", String, unique=True, index=True, nullable=False)
    """
    Endereço de e-mail do usuário.
    String, obrigatório, deve ser único para cada usuário.
    Possui um índice para buscas eficientes e para garantir a unicidade. Utilizado para login.
    """
    senha = mapped_column("password", String, nullable=False)
    """
    Senha do usuário (geralmente armazenada como um hash por segurança).
    String, obrigatório.
    """
    departamento_id = mapped_column("department_id", Integer, ForeignKey('departments.id'), nullable=True, index=True)
    """
    Chave estrangeira que referencia o ID do departamento (`DepartamentoDb`) ao qual o usuário pertence.
    É opcional (`nullable=True`), pois um usuário pode não estar vinculado a um departamento.
    Possui um índice para otimizar buscas por usuários de um departamento específico.
    """
    atualizado_em = mapped_column("updated_at", DateTime(), server_default=current_timestamp(), server_onupdate=current_timestamp())
    """
    Carimbo de data/hora da última atualização do registro.
    """
    criado_em = mapped_column("created_at", DateTime(), server_default=current_timestamp())
    """
    Carimbo de data/hora de criação do registro.
    """

    # Índices Adicionais para a tabela
    __table_args__ = (
        Index('ix_users_name_surname', 'name', 'surname'),
    )

    # Relacionamentos ORM
    departamento = relationship("DepartamentoDb", back_populates="usuarios", foreign_keys=[departamento_id]) # Alterado 'DepartmentDb' para 'DepartamentoDb', 'users' para 'usuarios'
    """
    Relacionamento Many-to-One: Um Usuário pertence a um Departamento.
    - `DepartamentoDb`: Classe do modelo do departamento.
    - `back_populates="usuarios"`: Cria um link bidirecional com o atributo `usuarios` em `DepartamentoDb`,
      permitindo acessar a lista de usuários de um departamento.
    """
    reservas = relationship("ReservaDb", back_populates="usuario", foreign_keys="ReservaDb.usuario_id") # Alterado 'ReservaDb.user_id' para 'ReservaDb.usuario_id', 'user' para 'usuario'
    """
    Relacionamento One-to-Many: Um Usuário pode fazer muitas Reservas.
    - `ReservaDb`: Classe do modelo de reserva.
    - `back_populates="usuario"`: Cria um link bidirecional com o atributo `usuario` em `ReservaDb`,
      permitindo acessar o usuário que fez a reserva.
    """
    reservas_aprovadas = relationship("ReservaDb", back_populates="aprovada_por_usuario", foreign_keys="ReservaDb.aprovado_por") # Alterado 'approved_reservations' para 'reservas_aprovadas', 'aprovada_por_user' para 'aprovada_por_usuario'
    """
    Relacionamento One-to-Many: Um Usuário pode aprovar muitas Reservas.
    - `ReservaDb`: Classe do modelo de reserva.
    - `back_populates="aprovada_por_usuario"`: Cria um link bidirecional com o atributo `aprovada_por_usuario` em `ReservaDb`.
    Este relacionamento é distinto do `reservas` e permite rastrear as aprovações realizadas por este usuário.
    """


class SalaDb(Base):
    """
    Modelo de banco de dados para representar uma Sala.

    Esta tabela armazena informações sobre as salas físicas disponíveis para reserva
    dentro da organização.
    Uma sala pertence a um departamento, pode ter múltiplos recursos associados
    e registrar várias reservas ao longo do tempo.
    """
    __tablename__ = 'salas'
    """Nome da tabela no banco de dados."""

    id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    """
    Chave primária da tabela.
    Inteiro, auto-incrementável, identifica unicamente cada sala.
    """
    codigo = mapped_column("codigo", String, unique=True, nullable=False, index=True) # Alterado de 'code' para 'codigo'
    """
    Código único da sala.
    String, obrigatório, deve ser único para cada sala.
    Possui um índice para buscas rápidas e garantia de unicidade. Ex: "SALA001".
    """
    nome = mapped_column("nome", String, nullable=False, index=True)
    """
    Nome da sala.
    String, obrigatório. Possui um índice para buscas por nome. Ex: "Sala de Reuniões Principal".
    """
    capacidade = mapped_column("capacidade", Integer, nullable=False, index=True)
    """
    Capacidade máxima de pessoas que a sala pode acomodar.
    Inteiro, obrigatório. Possui um índice para filtragem por capacidade.
    """
    predio = mapped_column("predio", String, nullable=False, index=True) # Alterado de 'building' para 'predio'
    """
    Nome ou código do edifício onde a sala está localizada.
    String, obrigatório. Possui um índice.
    """
    andar = mapped_column("andar", String, nullable=False, index=True) # Alterado de 'floor' para 'andar'
    """
    Andar onde a sala está localizada.
    String, obrigatório. Possui um índice.
    """
    departamento_id = mapped_column("departamento_id", Integer, ForeignKey('departamentos.id'), nullable=False, index=True) # Alterado ForeignKey para 'departamentos.id'
    """
    Chave estrangeira que referencia o ID do departamento (`DepartamentoDb`) ao qual a sala pertence.
    Inteiro, obrigatório. Possui um índice.
    """
    status = mapped_column("status", Enum(enums.RoomStatus), default=enums.RoomStatus.ATIVA, nullable=False, index=True)
    """
    Status atual da sala (ex: ATIVA, EM_MANUTENCAO, INATIVA).
    Utiliza um tipo Enum (`enums.RoomStatus`) para valores controlados.
    Possui um valor padrão `enums.RoomStatus.ATIVA` e um índice para filtragem por status.
    """
    responsavel = mapped_column("responsavel", String, nullable=True)
    """
    Nome da pessoa ou equipe responsável pela manutenção ou gestão da sala.
    String, opcional.
    """
    descricao = mapped_column("descricao", Text, nullable=True)
    """
    Descrição detalhada da sala, incluindo características adicionais ou observações.
    Texto longo, opcional.
    """
    criado_em = mapped_column("criado_em", DateTime(), server_default=current_timestamp()) # Alterado de 'created_at' para 'criado_em'
    """
    Carimbo de data/hora de criação do registro.
    """
    atualizado_em = mapped_column("atualizado_em", DateTime(), server_default=current_timestamp(), server_onupdate=current_timestamp()) # Alterado de 'updated_at' para 'atualizado_em'
    """
    Carimbo de data/hora da última atualização do registro.
    """

    # Índices para consultas combinadas
    __table_args__ = (
        Index('ix_salas_predio_andar', 'predio', 'andar'),
        Index('ix_salas_capacidade_status', 'capacidade', 'status'),
    )

    # Relacionamentos ORM
    departamento = relationship("DepartamentoDb", back_populates="salas") # Alterado 'DepartmentDb' para 'DepartamentoDb', 'rooms' para 'salas'
    """
    Relacionamento Many-to-One: Uma Sala pertence a um Departamento.
    - `DepartamentoDb`: Classe do modelo do departamento.
    - `back_populates="salas"`: Cria um link bidirecional com o atributo `salas` em `DepartamentoDb`.
    """
    recursos = relationship("RecursoSalaDb", back_populates="sala", cascade="all, delete-orphan") # Alterado 'resources' para 'recursos', 'RoomResourceDb' para 'RecursoSalaDb', 'room' para 'sala'
    """
    Relacionamento One-to-Many: Uma Sala pode ter muitos Recursos de Sala.
    - `RecursoSalaDb`: Classe do modelo de recurso de sala.
    - `back_populates="sala"`: Cria um link bidirecional com o atributo `sala` em `RecursoSalaDb`.
    - `cascade="all, delete-orphan"`: Garante que, ao deletar uma sala, todos os seus recursos associados
      também sejam deletados do banco de dados (cascata). Além disso, se um `RecursoSalaDb` for removido
      da coleção `sala.recursos`, ele será excluído do banco de dados.
    """
    reservas = relationship("ReservaDb", back_populates="sala", cascade="all, delete-orphan") # Alterado 'reservations' para 'reservas', 'ReservationDb' para 'ReservaDb', 'room' para 'sala'
    """
    Relacionamento One-to-Many: Uma Sala pode ter muitas Reservas.
    - `ReservaDb`: Classe do modelo de reserva.
    - `back_populates="sala"`: Cria um link bidirecional com o atributo `sala` em `ReservaDb`.
    - `cascade="all, delete-orphan"`: Garante que, ao deletar uma sala, todas as suas reservas associadas
      também sejam deletadas do banco de dados. Similarmente, se uma `ReservaDb` for removida
      da coleção `sala.reservas`, ela será excluída do banco de dados.
    """


class RecursoSalaDb(Base): # Alterado de 'RoomResourceDb' para 'RecursoSalaDb'
    """
    Modelo de banco de dados para Recursos de Sala.

    Esta tabela detalha os equipamentos ou características específicas (ex: projetor, quadro branco)
    disponíveis em uma determinada sala.
    Representa uma relação One-to-Many de `SalaDb` para `RecursoSalaDb`,
    onde cada recurso é específico para uma instância de sala.
    """
    __tablename__ = 'recursos_salas' # Alterado de 'room_resources' para 'recursos_salas'
    """Nome da tabela no banco de dados."""

    id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    """
    Chave primária da tabela.
    Inteiro, auto-incrementável, identifica unicamente cada recurso de sala.
    """
    sala_id = mapped_column("sala_id", Integer, ForeignKey('salas.id', ondelete='CASCADE'), nullable=False, index=True) # Alterado de 'room_id' para 'sala_id', ForeignKey para 'salas.id'
    """
    Chave estrangeira que referencia o ID da sala (`SalaDb`) à qual o recurso pertence.
    Inteiro, obrigatório.
    - `ondelete='CASCADE'`: Garante que, se uma sala for deletada, todos os seus recursos associados
      também sejam automaticamente deletados do banco de dados.
    Possui um índice para otimizar buscas por recursos de uma sala específica.
    """
    nome_recurso = mapped_column("nome_recurso", String, nullable=False, index=True) # Alterado de 'resource_name' para 'nome_recurso'
    """
    Nome do recurso (ex: "Projetor HDMI", "Quadro Interativo", "Sistema de Videoconferência").
    String, obrigatório. Possui um índice para buscas por tipo de recurso.
    """
    quantidade = mapped_column("quantidade", Integer, default=1, nullable=False) # Alterado de 'quantity' para 'quantidade'
    """
    Quantidade deste recurso disponível na sala.
    Inteiro, obrigatório, com valor padrão de 1.
    """
    descricao = mapped_column("descricao", Text, nullable=True) # Alterado de 'description' para 'descricao'
    """
    Descrição detalhada do recurso.
    Texto longo, opcional.
    """
    criado_em = mapped_column("criado_em", DateTime(), server_default=current_timestamp()) # Alterado de 'created_at' para 'criado_em'
    """
    Carimbo de data/hora de criação do registro.
    """
    atualizado_em = mapped_column("atualizado_em", DateTime(), server_default=current_timestamp(), server_onupdate=current_timestamp()) # Alterado de 'updated_at' para 'atualizado_em'
    """
    Carimbo de data/hora da última atualização do registro.
    """

    # Relacionamentos ORM
    sala = relationship("SalaDb", back_populates="recursos") # Alterado 'RoomDb' para 'SalaDb', 'room' para 'sala', 'resources' para 'recursos'
    """
    Relacionamento Many-to-One: Um Recurso de Sala pertence a uma Sala.
    - `SalaDb`: Classe do modelo da sala.
    - `back_populates="recursos"`: Cria um link bidirecional com o atributo `recursos` em `SalaDb`.
    """


class ReservaDb(Base): # Alterado de 'ReservationDb' para 'ReservaDb'
    """
    Modelo de banco de dados para Reservas de Sala.

    Esta tabela registra as reservas de salas feitas pelos usuários.
    Detalha quem reservou, qual sala, o período da reserva, seu status,
    e informações de aprovação/cancelamento.
    """
    __tablename__ = 'reservas' # Alterado de 'reservations' para 'reservas'
    """Nome da tabela no banco de dados."""

    id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    """
    Chave primária da tabela.
    Inteiro, auto-incrementável, identifica unicamente cada reserva.
    """
    sala_id = mapped_column("sala_id", Integer, ForeignKey('salas.id', ondelete='CASCADE'), nullable=False, index=True) # Alterado de 'room_id' para 'sala_id', ForeignKey para 'salas.id'
    """
    Chave estrangeira que referencia o ID da sala (`SalaDb`) que foi reservada.
    Inteiro, obrigatório.
    - `ondelete='CASCADE'`: Garante que, se uma sala for deletada, todas as reservas associadas
      também sejam automaticamente deletadas do banco de dados.
    Possui um índice.
    """
    usuario_id = mapped_column("usuario_id", Integer, ForeignKey('usuarios.id'), nullable=False, index=True) # Alterado de 'user_id' para 'usuario_id', ForeignKey para 'usuarios.id'
    """
    Chave estrangeira que referencia o ID do usuário (`UsuarioDb`) que fez a reserva.
    Inteiro, obrigatório. Possui um índice.
    """
    titulo = mapped_column("titulo", String, nullable=False) # Alterado de 'title' para 'titulo'
    """
    Título ou assunto da reserva (ex: "Reunião de Equipe", "Apresentação de Projeto").
    String, obrigatório.
    """
    descricao = mapped_column("descricao", Text, nullable=True) # Alterado de 'description' para 'descricao'
    """
    Descrição detalhada do propósito da reserva.
    Texto longo, opcional.
    """
    inicio_data_hora = mapped_column("inicio_data_hora", DateTime(), nullable=False, index=True) # Alterado de 'start_datetime' para 'inicio_data_hora'
    """
    Data e hora de início da reserva.
    DateTime, obrigatório. Possui um índice para consultas de intervalo de tempo.
    """
    fim_data_hora = mapped_column("fim_data_hora", DateTime(), nullable=False, index=True) # Alterado de 'end_datetime' para 'fim_data_hora'
    """
    Data e hora de término da reserva.
    DateTime, obrigatório. Possui um índice para consultas de intervalo de tempo.
    """
    status = mapped_column("status", Enum(enums.ReservationStatus), default=enums.ReservationStatus.PENDENTE, nullable=False, index=True)
    """
    Status atual da reserva (ex: PENDENTE, APROVADA, RECUSADA, CANCELADA, CONCLUIDA).
    Utiliza um tipo Enum (`enums.ReservationStatus`) para valores controlados.
    Possui um valor padrão `enums.ReservationStatus.PENDENTE` e um índice para filtragem por status.
    """
    aprovado_por = mapped_column("aprovado_por", Integer, ForeignKey('usuarios.id'), nullable=True, index=True) # Alterado de 'approved_by' para 'aprovado_por', ForeignKey para 'usuarios.id'
    """
    Chave estrangeira que referencia o ID do usuário (`UsuarioDb`) que aprovou a reserva.
    Inteiro, opcional (`nullable=True`), pois nem todas as reservas requerem aprovação ou ainda não foram aprovadas.
    Possui um índice.
    """
    aprovado_em = mapped_column("aprovado_em", DateTime(), nullable=True) # Alterado de 'approved_at' para 'aprovado_em'
    """
    Carimbo de data/hora da aprovação da reserva.
    DateTime, opcional (`nullable=True`).
    """
    motivo_cancelamento = mapped_column("motivo_cancelamento", Text, nullable=True) # Alterado de 'cancellation_reason' para 'motivo_cancelamento'
    """
    Motivo do cancelamento da reserva, se aplicável.
    Texto longo, opcional (`nullable=True`).
    """
    criado_em = mapped_column("criado_em", DateTime(), server_default=current_timestamp()) # Alterado de 'created_at' para 'criado_em'
    """
    Carimbo de data/hora de criação do registro.
    """
    atualizado_em = mapped_column("atualizado_em", DateTime(), server_default=current_timestamp(), server_onupdate=current_timestamp()) # Alterado de 'updated_at' para 'atualizado_em'
    """
    Carimbo de data/hora da última atualização do registro.
    """

    # Índices para consultas combinadas
    __table_args__ = (
        Index('ix_reservas_intervalo_data_hora', 'inicio_data_hora', 'fim_data_hora'),
        Index('ix_reservas_sala_data_hora_status', 'sala_id', 'inicio_data_hora', 'fim_data_hora', 'status'),
        Index('ix_reservas_usuario_status', 'usuario_id', 'status'),
    )

    # Relacionamentos ORM
    sala = relationship("SalaDb", back_populates="reservas") # Alterado 'RoomDb' para 'SalaDb', 'room' para 'sala', 'reservations' para 'reservas'
    """
    Relacionamento Many-to-One: Uma Reserva pertence a uma Sala.
    - `SalaDb`: Classe do modelo da sala.
    - `back_populates="reservas"`: Cria um link bidirecional com o atributo `reservas` em `SalaDb`.
    """
    usuario = relationship("UsuarioDb", back_populates="reservas", foreign_keys=[usuario_id]) # Alterado 'UserDb' para 'UsuarioDb', 'user' para 'usuario', 'reservations' para 'reservas', 'user_id' para 'usuario_id'
    """
    Relacionamento Many-to-One: Uma Reserva foi feita por um Usuário.
    - `UsuarioDb`: Classe do modelo do usuário.
    - `back_populates="reservas"`: Cria um link bidirecional com o atributo `reservas` em `UsuarioDb`.
    """
    aprovada_por_usuario = relationship("UsuarioDb", back_populates="reservas_aprovadas", foreign_keys=[aprovado_por]) # Alterado 'UserDb' para 'UsuarioDb', 'approved_by_user' para 'aprovada_por_usuario', 'approved_reservations' para 'reservas_aprovadas', 'approved_by' para 'aprovado_por'
    """
    Relacionamento Many-to-One: Uma Reserva foi aprovada por um Usuário.
    - `UsuarioDb`: Classe do modelo do usuário.
    - `back_populates="reservas_aprovadas"`: Cria um link bidirecional com o atributo `reservas_aprovadas` em `UsuarioDb`.
    """
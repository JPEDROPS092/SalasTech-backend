"""
Script para popular o banco de dados com dados de teste.
Este script cria departamentos, usuários, salas, recursos e reservas para fins de teste e demonstração.
"""

import random
import datetime
from sqlalchemy.orm import Session
from typing import List

from SalasTech.app.models.db import (
    DepartmentDb, 
    UserDb, 
    RoomDb, 
    RoomResourceDb, 
    ReservationDb
)
from SalasTech.app.models.enums import UserRole, RoomStatus, ReservationStatus
from SalasTech.app.core.security.bcrypt_hashing import hash as get_password_hash


def seed_departments(session: Session) -> List[DepartmentDb]:
    """Cria departamentos de exemplo no banco de dados."""
    department_data = [
        {
            "name": "Departamento de Ciência da Computação",
            "code": "DCC",
            "description": "Departamento responsável pelos cursos de computação e tecnologia da informação"
        },
        {
            "name": "Departamento de Engenharia Elétrica",
            "code": "DEE",
            "description": "Departamento responsável pelos cursos de engenharia elétrica e eletrônica"
        },
        {
            "name": "Departamento de Administração",
            "code": "DAD",
            "description": "Departamento responsável pelos cursos de administração e gestão"
        },
        {
            "name": "Departamento de Matemática",
            "code": "DMAT",
            "description": "Departamento responsável pelos cursos de matemática e estatística"
        },
        {
            "name": "Departamento de Física",
            "code": "DFIS",
            "description": "Departamento responsável pelos cursos de física e astronomia"
        },
        {
            "name": "Departamento de Mecânica",
            "code": "DMEC",
            "description": "Departamento responsável pelos cursos de engenharia mecânica"
        },
        {
            "name": "Departamento de Química",
            "code": "DQUI",
            "description": "Departamento responsável pelos cursos de química e engenharia química"
        },
        {
            "name": "Departamento de Biologia",
            "code": "DBIO",
            "description": "Departamento responsável pelos cursos de biologia e biotecnologia"
        },
    ]
    
    departments = []
    for dept_info in department_data:
        # Verifica se o departamento já existe pelo código
        existing_dept = session.query(DepartmentDb).filter_by(code=dept_info["code"]).first()
        
        if existing_dept:
            # Se já existe, atualiza os dados se necessário
            existing_dept.name = dept_info["name"]
            existing_dept.description = dept_info["description"]
            departments.append(existing_dept)
            print(f"  Departamento {dept_info['code']} já existe, atualizando informações.")
        else:
            # Se não existe, cria um novo departamento
            new_dept = DepartmentDb(**dept_info)
            session.add(new_dept)
            departments.append(new_dept)
            print(f"  Criando departamento {dept_info['code']}.")
    
    session.commit()
    return departments


def seed_users(session: Session, departments: List[DepartmentDb]) -> List[UserDb]:
    """Cria usuários de exemplo no banco de dados."""
    users = []
    
    # Verifica se o usuário administrador já existe
    admin_email = "admin@ifam.edu.br"
    existing_admin = session.query(UserDb).filter_by(email=admin_email).first()
    
    if existing_admin:
        print(f"  Usuário admin já existe: {admin_email}")
        users.append(existing_admin)
    else:
        # Cria o usuário administrador principal
        admin_user = UserDb(
            name="Admin",
            surname="Sistema",
            role=UserRole.ADMIN,
            email=admin_email,
            password=get_password_hash("admin123"),
            department_id=departments[0].id
        )
        session.add(admin_user)
        users.append(admin_user)
        print(f"  Criando usuário admin: {admin_email}")
    
    # Criar ou atualizar gestores para cada departamento
    for i, dept in enumerate(departments):
        gestor_email = f"gestor.{dept.code.lower()}@ifam.edu.br"
        existing_gestor = session.query(UserDb).filter_by(email=gestor_email).first()
        
        if existing_gestor:
            print(f"  Usuário gestor já existe: {gestor_email}")
            users.append(existing_gestor)
            
            # Atualiza o gerente do departamento se necessário
            if dept.manager_id != existing_gestor.id:
                dept.manager_id = existing_gestor.id
        else:
            # Cria um novo gestor
            gestor_user = UserDb(
                name=f"Gestor{i+1}",
                surname=f"Departamento {dept.code}",
                role=UserRole.GESTOR,
                email=gestor_email,
                password=get_password_hash("gestor123"),
                department_id=dept.id
            )
            session.add(gestor_user)
            users.append(gestor_user)
            print(f"  Criando usuário gestor: {gestor_email}")
            
            # Atualiza o gerente do departamento
            dept.manager_id = gestor_user.id
    
    # Dados para criação de usuários
    first_names = [
        "João", "Maria", "Pedro", "Ana", "Carlos", "Juliana", "Lucas", "Fernanda", "Rafael", "Camila",
        "Bruno", "Larissa", "Gustavo", "Amanda", "Felipe", "Mariana", "Diego", "Beatriz", "Thiago", "Gabriela",
        "Ricardo", "Isabela", "Marcelo", "Natália", "Alexandre", "Carolina", "Eduardo", "Leticia", "Rodrigo", "Vanessa"
    ]
    
    last_names = [
        "Silva", "Santos", "Oliveira", "Souza", "Pereira", "Lima", "Costa", "Ferreira", "Rodrigues", "Almeida",
        "Nascimento", "Carvalho", "Gomes", "Martins", "Araújo", "Ribeiro", "Mendes", "Barros", "Freitas", "Barbosa",
        "Pinto", "Moreira", "Cavalcanti", "Dias", "Campos", "Cardoso", "Rocha", "Nunes", "Farias", "Vieira"
    ]
    
    # Criar usuários com diferentes papéis
    roles = [UserRole.USER, UserRole.USUARIO_AVANCADO, UserRole.GUEST]
    role_weights = [0.6, 0.3, 0.1]  # 60% usuários normais, 30% avançados, 10% convidados
    
    # Criar 30 usuários regulares
    for i in range(30):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}{i}@ifam.edu.br"
        role = random.choices(roles, weights=role_weights, k=1)[0]
        
        user = UserDb(
            name=first_name,
            surname=last_name,
            role=role,
            email=email,
            password=get_password_hash("user123"),
            department_id=random.choice(departments).id
        )
        users.append(user)
    
    # Adicionar todos os usuários ao banco de dados
    for user in users:
        session.add(user)
    
    session.commit()
    return users


def seed_rooms(session: Session, departments: List[DepartmentDb]) -> List[RoomDb]:
    """Cria salas de exemplo no banco de dados, verificando se já existem."""
    buildings = ["Bloco A", "Bloco B", "Bloco C", "Bloco D", "Bloco E", "Bloco F"]
    floors = ["Térreo", "1º Andar", "2º Andar", "3º Andar", "4º Andar"]
    
    # Tipos de salas com suas capacidades típicas
    room_types = [
        {"prefix": "LAB", "name": "Laboratório", "min_capacity": 15, "max_capacity": 30},
        {"prefix": "AUD", "name": "Auditório", "min_capacity": 80, "max_capacity": 200},
        {"prefix": "SAL", "name": "Sala de Aula", "min_capacity": 30, "max_capacity": 60},
        {"prefix": "REU", "name": "Sala de Reunião", "min_capacity": 8, "max_capacity": 20},
        {"prefix": "BIB", "name": "Biblioteca", "min_capacity": 40, "max_capacity": 100},
        {"prefix": "INF", "name": "Laboratório de Informática", "min_capacity": 20, "max_capacity": 40}
    ]
    
    # Status possíveis para as salas (com probabilidades)
    status_options = [
        (RoomStatus.ATIVA, 0.8),       # 80% das salas estão ativas
        (RoomStatus.INATIVA, 0.1),     # 10% das salas estão inativas
        (RoomStatus.MANUTENCAO, 0.1)   # 10% das salas estão em manutenção
    ]
    
    rooms = []
    room_counter = 0
    
    # Cria salas para cada departamento
    for dept in departments:
        # Determina quantas salas de cada tipo o departamento terá
        for room_type in room_types:
            # Cada departamento terá entre 1 e 4 salas de cada tipo
            num_rooms = random.randint(1, 4)
            
            for i in range(num_rooms):
                room_counter += 1
                building = random.choice(buildings)
                floor = random.choice(floors)
                
                # Determina o status da sala com base nas probabilidades
                status = random.choices(
                    [s[0] for s in status_options],
                    weights=[s[1] for s in status_options],
                    k=1
                )[0]
                
                # Gera um código único para a sala
                code = f"{dept.code}-{room_type['prefix']}{building[-1]}{floor[0]}{i+1:02d}"
                
                # Determina a capacidade da sala com base no tipo
                capacity = random.randint(room_type['min_capacity'], room_type['max_capacity'])
                
                # Cria o nome da sala
                name = f"{room_type['name']} {i+1} - {dept.name}"
                
                # Cria a descrição da sala
                description = f"{room_type['name']} {i+1} do departamento {dept.name} localizada no {floor} do {building}."
                if status == RoomStatus.MANUTENCAO:
                    description += " Atualmente em manutenção programável."
                elif status == RoomStatus.INATIVA:
                    description += " Temporariamente inativa."
                
                # Cria o responsável pela sala
                responsible = f"Responsável {dept.code}-{room_type['prefix']}"
                
                # Verifica se a sala já existe pelo código
                existing_room = session.query(RoomDb).filter_by(code=code).first()
                
                if existing_room:
                    # Atualiza a sala existente
                    existing_room.name = name
                    existing_room.capacity = capacity
                    existing_room.building = building
                    existing_room.floor = floor
                    existing_room.department_id = dept.id
                    existing_room.status = status
                    existing_room.description = description
                    
                    rooms.append(existing_room)
                    print(f"  Sala {code} já existe, atualizando informações.")
                else:
                    # Cria uma nova sala
                    room = RoomDb(
                        code=code,
                        name=name,
                        capacity=capacity,
                        building=building,
                        floor=floor,
                        department_id=dept.id,
                        status=status,
                        description=description
                    )
                    
                    rooms.append(room)
                    session.add(room)
                    print(f"  Criando sala {code}.")
    
    for room in rooms:
        session.add(room)
    
    session.commit()
    print(f"✓ {len(rooms)} salas criadas.")
    return rooms


def seed_room_resources(session: Session, rooms: List[RoomDb]) -> List[RoomResourceDb]:
    """Cria recursos para as salas de exemplo no banco de dados, verificando se já existem."""
    # Recursos básicos que podem estar em qualquer tipo de sala
    basic_resources = [
        {"name": "Ar-condicionado", "description": "Sistema de ar-condicionado", "min": 1, "max": 2},
        {"name": "Quadro branco", "description": "Quadro branco para escrita", "min": 1, "max": 2},
        {"name": "Cadeiras", "description": "Cadeiras para os alunos", "min": 0, "max": 0},  # Quantidade baseada na capacidade
        {"name": "Mesas", "description": "Mesas para os alunos", "min": 0, "max": 0},      # Quantidade baseada na capacidade
        {"name": "Lixeira", "description": "Lixeira para descarte de resíduos", "min": 1, "max": 3},
        {"name": "Relógio de parede", "description": "Relógio para controle do tempo", "min": 0, "max": 1},
        {"name": "Extintor", "description": "Extintor de incêndio", "min": 1, "max": 2}
    ]
    
    # Recursos específicos por tipo de sala (identificado pelo prefixo no código)
    specific_resources = {
        "LAB": [
            {"name": "Bancadas", "description": "Bancadas para experimentos", "min": 4, "max": 10},
            {"name": "Microscópios", "description": "Microscópios para análises", "min": 5, "max": 15},
            {"name": "Equipamentos de segurança", "description": "Kits de segurança para laboratório", "min": 1, "max": 3},
            {"name": "Vidraria", "description": "Conjunto de vidrarias para experimentos", "min": 5, "max": 20}
        ],
        "AUD": [
            {"name": "Sistema de som", "description": "Sistema de som para apresentações", "min": 1, "max": 1},
            {"name": "Projetor", "description": "Projetor multimídia de alta definição", "min": 1, "max": 2},
            {"name": "Microfones", "description": "Microfones para palestras", "min": 2, "max": 5},
            {"name": "Palco", "description": "Palco elevado para apresentações", "min": 1, "max": 1},
            {"name": "Iluminação especial", "description": "Sistema de iluminação para eventos", "min": 1, "max": 1}
        ],
        "SAL": [
            {"name": "Projetor", "description": "Projetor multimídia", "min": 1, "max": 1},
            {"name": "Computador", "description": "Computador para o professor", "min": 1, "max": 1},
            {"name": "Mesa do professor", "description": "Mesa para o professor", "min": 1, "max": 1},
            {"name": "Apagador", "description": "Apagador para quadro", "min": 1, "max": 2},
            {"name": "Canetas para quadro", "description": "Conjunto de canetas para quadro branco", "min": 4, "max": 10}
        ],
        "REU": [
            {"name": "Mesa de reunião", "description": "Mesa grande para reuniões", "min": 1, "max": 1},
            {"name": "TV", "description": "TV para apresentações", "min": 1, "max": 1},
            {"name": "Sistema de videoconferência", "description": "Equipamento para videoconferências", "min": 0, "max": 1},
            {"name": "Quadro de avisos", "description": "Quadro para anotações e lembretes", "min": 1, "max": 1}
        ],
        "BIB": [
            {"name": "Estantes", "description": "Estantes para livros", "min": 10, "max": 30},
            {"name": "Computadores", "description": "Computadores para pesquisa", "min": 5, "max": 15},
            {"name": "Mesas de estudo", "description": "Mesas para estudo individual", "min": 5, "max": 20},
            {"name": "Cabines de estudo", "description": "Cabines para estudo em grupo", "min": 2, "max": 8}
        ],
        "INF": [
            {"name": "Computadores", "description": "Computadores para os alunos", "min": 15, "max": 40},
            {"name": "Switches", "description": "Switches para rede local", "min": 1, "max": 3},
            {"name": "Roteadores", "description": "Roteadores para conexão com a internet", "min": 1, "max": 2},
            {"name": "Impressora", "description": "Impressora para uso dos alunos", "min": 0, "max": 2},
            {"name": "Quadro interativo", "description": "Quadro interativo para aulas", "min": 0, "max": 1}
        ]
    }
    
    all_resources = []
    
    for room in rooms:
        # Adiciona recursos básicos para todas as salas
        for resource in basic_resources:
            # Determina a quantidade do recurso
            if resource["name"] == "Cadeiras":
                quantity = room.capacity
            elif resource["name"] == "Mesas":
                quantity = max(1, room.capacity // 2)  # Assumindo 2 alunos por mesa
            elif resource["min"] == 0 and resource["max"] == 0:
                continue  # Pula recursos com min e max zerados
            elif resource["min"] == 0 and random.random() < 0.3:  # 30% de chance de não ter o recurso se min=0
                continue
            else:
                quantity = random.randint(resource["min"], resource["max"])
            
            # Verifica se o recurso já existe para esta sala
            existing_resource = session.query(RoomResourceDb).filter_by(
                room_id=room.id, 
                resource_name=resource["name"]
            ).first()
            
            if existing_resource:
                # Atualiza o recurso existente
                existing_resource.quantity = quantity
                existing_resource.description = resource["description"]
                
                all_resources.append(existing_resource)
            else:
                # Cria um novo recurso para a sala
                resource = RoomResourceDb(
                    room_id=room.id,
                    resource_name=resource["name"],
                    quantity=quantity,
                    description=resource["description"]
                )
                
                all_resources.append(resource)
                session.add(resource)
        
        # Identifica o tipo de sala pelo código e adiciona recursos específicos
        room_type = None
        for prefix in specific_resources.keys():
            if prefix in room.code:
                room_type = prefix
                break
        
        if room_type and room_type in specific_resources:
            for resource in specific_resources[room_type]:
                # Verifica se o recurso deve ser adicionado (chance de 80% se min=0)
                if resource["min"] == 0 and random.random() > 0.8:
                    continue
                    
                quantity = random.randint(resource["min"], resource["max"])
                
                # Ajusta a quantidade para recursos especiais
                if resource["name"] == "Computadores" and room_type == "INF":
                    quantity = min(room.capacity, quantity)  # Limita ao número de alunos
                
                # Verifica se o recurso já existe para esta sala
                existing_resource = session.query(RoomResourceDb).filter_by(
                    room_id=room.id, 
                    resource_name=resource["name"]
                ).first()
                
                if existing_resource:
                    # Atualiza o recurso existente
                    existing_resource.quantity = quantity
                    existing_resource.description = resource["description"]
                    
                    all_resources.append(existing_resource)
                else:
                    # Cria um novo recurso para a sala
                    resource = RoomResourceDb(
                        room_id=room.id,
                        resource_name=resource["name"],
                        quantity=quantity,
                        description=resource["description"]
                    )
                    
                    all_resources.append(resource)
                    session.add(resource)
    
    for resource in all_resources:
        session.add(resource)
    
    session.commit()
    print(f"✓ {len(all_resources)} recursos criados.")
    return all_resources


def seed_reservations(session: Session, rooms: List[RoomDb], users: List[UserDb]) -> List[ReservationDb]:
    """Cria reservas de exemplo no banco de dados, evitando duplicação."""
    reservations = []
    
    # Apenas salas ativas podem ser reservadas
    active_rooms = [room for room in rooms if room.status == RoomStatus.ATIVA]
    
    # Apenas usuários normais, avançados e gestores podem fazer reservas
    eligible_users = [user for user in users if user.role in [UserRole.USER, UserRole.USUARIO_AVANCADO, UserRole.GESTOR]]
    
    # Gestores que podem aprovar reservas
    approvers = [user for user in users if user.role in [UserRole.GESTOR, UserRole.ADMIN]]
    
    # Títulos e descrições para reservas
    reservation_types = [
        {"title": "Aula de Programação", "description": "Aula prática de programação em Python"},
        {"title": "Reunião de Departamento", "description": "Reunião mensal do departamento"},
        {"title": "Palestra sobre IA", "description": "Palestra sobre os avanços da Inteligência Artificial"},
        {"title": "Workshop de Robótica", "description": "Workshop prático sobre robótica educacional"},
        {"title": "Defesa de TCC", "description": "Apresentação e defesa de Trabalho de Conclusão de Curso"},
        {"title": "Aula de Cálculo", "description": "Aula sobre cálculo diferencial e integral"},
        {"title": "Laboratório de Física", "description": "Experimentos práticos de física"},
        {"title": "Apresentação de Projeto", "description": "Apresentação dos resultados de projetos de pesquisa"},
        {"title": "Seminário Acadêmico", "description": "Seminário sobre temas relevantes para a academia"},
        {"title": "Orientação de Alunos", "description": "Sessão de orientação acadêmica"}
    ]
    
    # Horários típicos de aulas e eventos
    time_slots = [
        (8, 0, 2),    # 8:00 - 10:00 (2h)
        (10, 15, 2),  # 10:15 - 12:15 (2h)
        (13, 30, 2),  # 13:30 - 15:30 (2h)
        (15, 45, 2),  # 15:45 - 17:45 (2h)
        (18, 0, 3),   # 18:00 - 21:00 (3h - noturno)
        (9, 0, 1),    # 9:00 - 10:00 (1h - reunião curta)
        (14, 0, 1),   # 14:00 - 15:00 (1h - reunião curta)
        (16, 0, 1)    # 16:00 - 17:00 (1h - reunião curta)
    ]
    
    # Cria reservas para os próximos 30 dias
    for _ in range(50):
        # Escolhe uma sala aleatória
        room = random.choice(active_rooms)
        
        # Escolhe um usuário aleatório
        user = random.choice(eligible_users)
        
        # Escolhe uma data aleatória nos próximos 30 dias
        days_ahead = random.randint(0, 30)
        reservation_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=days_ahead)
        
        # Escolhe um horário aleatório
        time_slot = random.choice(time_slots)
        start_hour, start_minute, duration = time_slot
        
        start_datetime = reservation_date.replace(hour=start_hour, minute=start_minute)
        end_datetime = start_datetime + datetime.timedelta(hours=duration)
        
        # Escolhe um tipo de reserva aleatório
        reservation_type = random.choice(reservation_types)
        title = reservation_type["title"]
        description = f"{reservation_type['description']} - Reservado por {user.name} {user.surname}"
        
        # Define o status da reserva
        # 60% confirmadas, 30% pendentes, 10% canceladas
        status_choice = random.random()
        if status_choice < 0.6:
            status = ReservationStatus.CONFIRMADA
            approved_by = random.choice(approvers).id
            approved_at = start_datetime - datetime.timedelta(days=random.randint(1, 5))
            cancellation_reason = None
        elif status_choice < 0.9:
            status = ReservationStatus.PENDENTE
            approved_by = None
            approved_at = None
            cancellation_reason = None
        else:
            status = ReservationStatus.CANCELADA
            approved_by = None
            approved_at = None
            cancellation_reason = "Cancelado pelo usuário"
        
        # Verifica se já existe uma reserva similar para evitar duplicação
        existing_reservation = session.query(ReservationDb).filter_by(
            room_id=room.id,
            user_id=user.id,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        ).first()
        
        if existing_reservation:
            # Atualiza a reserva existente se necessário
            existing_reservation.title = title
            existing_reservation.description = description
            existing_reservation.status = status
            existing_reservation.approved_by = approved_by
            existing_reservation.approved_at = approved_at
            existing_reservation.cancellation_reason = cancellation_reason
            
            reservations.append(existing_reservation)
        else:
            # Cria uma nova reserva
            reservation = ReservationDb(
                room_id=room.id,
                user_id=user.id,
                title=title,
                description=description,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                status=status,
                approved_by=approved_by,
                approved_at=approved_at,
                cancellation_reason=cancellation_reason
            )
            
            reservations.append(reservation)
            session.add(reservation)
    
    # Adiciona mensagem de conclusão
    print(f"✓ {len(reservations)} reservas criadas.")
    
    for reservation in reservations:
        session.add(reservation)
    
    session.commit()
    return reservations


def seed_database(session: Session):
    """Função principal para popular o banco de dados com dados de teste."""
    print("Iniciando população do banco de dados...")
    
    try:
        # Cria departamentos
        print("Criando departamentos...")
        departments = seed_departments(session)
        print(f"✓ {len(departments)} departamentos processados.")
        
        # Cria usuários
        print("Criando usuários...")
        users = seed_users(session, departments)
        print(f"✓ {len(users)} usuários processados.")
        
        # Cria salas
        print("Criando salas...")
        rooms = seed_rooms(session, departments)
        print(f"✓ {len(rooms)} salas processadas.")
        
        # Cria recursos para as salas
        print("Criando recursos para as salas...")
        resources = seed_room_resources(session, rooms)
        print(f"✓ {len(resources)} recursos processados.")
        
        # Cria reservas
        print("Criando reservas...")
        reservations = seed_reservations(session, rooms, users)
        print(f"✓ {len(reservations)} reservas processadas.")
        
        print("\nBanco de dados populado com sucesso!")
        print("\nCredenciais de acesso:")
        print("Admin: admin@ifam.edu.br / admin123")
        print("Gestor: gestor.<código-departamento>@ifam.edu.br / gestor123")
        print("Usuários: email gerado / user123")
        
        return True
    except Exception as e:
        session.rollback()
        print(f"\nErro durante a população do banco de dados: {e}")
        return False


if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker
    from SalasTech.app.core.db_context import engine, create_tables
    
    # Cria as tabelas se não existirem
    create_tables()
    
    # Cria uma sessão
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Popula o banco de dados
        seed_database(session)
    except Exception as e:
        session.rollback()
        print(f"Erro ao popular o banco de dados: {e}")
    finally:
        session.close()

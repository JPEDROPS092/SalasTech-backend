#!/usr/bin/env python3
"""
Script para gerenciar usuários administradores do SalasTech

Este script (manage_admins.py) permite criar, listar, editar e excluir usuários administradores
que podem acessar o painel administrativo web do sistema.
"""

import os
import sys
import secrets
import string
import getpass
import datetime
from pathlib import Path
import datetime

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.db_context import SessionLocal
from app.core.security.password import PasswordManager
from app.models.db import UsuarioDb
from app.models.enums import UserRole


def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Imprime o cabeçalho da aplicação"""
    clear_screen()
    print("🚀" + "=" * 48 + "🚀")
    print("    SalasTech - Criador de Usuário Administrador")
    print("🚀" + "=" * 48 + "🚀")
    print()


def generate_random_password(length=12):
    """Gera uma senha aleatória segura"""
    characters = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(secrets.choice(characters) for _ in range(length))


def get_input_with_validation(prompt, validator=None, error_msg="Entrada inválida!"):
    """Solicita entrada com validação"""
    while True:
        value = input(f"📝 {prompt}: ").strip()
        if not value:
            print(f"❌ {prompt} é obrigatório!")
            continue
        if validator and not validator(value):
            print(f"❌ {error_msg}")
            continue
        return value


def validate_email(email):
    """Validação básica de email"""
    return "@" in email and "." in email.split("@")[1]


def get_password_choice():
    """Menu para escolha de senha"""
    print("\n🔐 Configuração de Senha:")
    print("   1️⃣  Digitar senha manualmente")
    print("   2️⃣  Gerar senha aleatória segura")
    print("   3️⃣  Usar senha padrão (admin123)")
    
    while True:
        choice = input("\n🎯 Escolha uma opção (1/2/3): ").strip()
        
        if choice == "1":
            while True:
                senha = getpass.getpass("🔒 Digite a senha (oculta): ")
                if not senha:
                    print("❌ Senha é obrigatória!")
                    continue
                if len(senha) < 6:
                    print("❌ Senha deve ter pelo menos 6 caracteres!")
                    continue
                
                # Confirmar senha
                confirma = getpass.getpass("🔒 Confirme a senha: ")
                if senha != confirma:
                    print("❌ Senhas não coincidem! Tente novamente.")
                    continue
                
                return senha
                
        elif choice == "2":
            senha = generate_random_password()
            print(f"🎲 Senha gerada: {senha}")
            print("⚠️  IMPORTANTE: Anote essa senha!")
            input("📋 Pressione ENTER após anotar a senha...")
            return senha
            
        elif choice == "3":
            print("🔑 Usando senha padrão: admin123")
            print("⚠️  IMPORTANTE: Altere esta senha após o primeiro login!")
            return "admin123"
            
        else:
            print("❌ Opção inválida! Escolha 1, 2 ou 3.")


def show_confirmation(dados):
    """Mostra dados para confirmação"""
    print("\n" + "📋" + "=" * 40 + "📋")
    print("           DADOS DO ADMINISTRADOR")
    print("📋" + "=" * 40 + "📋")
    print(f"   👤 Nome: {dados['nome']} {dados['sobrenome']}")
    print(f"   📧 Email: {dados['email']}")
    print(f"   🔑 Senha: {'*' * len(dados['senha'])}")
    print(f"   👑 Papel: Administrador")
    print("📋" + "=" * 40 + "📋")


def list_existing_admins(db):
    """Lista administradores existentes"""
    admins = db.query(UsuarioDb).filter(UsuarioDb.papel == UserRole.ADMIN).all()
    
    if admins:
        print("\n👥 Administradores existentes:")
        print("-" * 40)
        for admin in admins:
            print(f"   📧 {admin.email} - {admin.nome} {admin.sobrenome}")
        print("-" * 40)
        return len(admins)
    return 0


def save_credentials_to_file(dados, admin_user):
    """Salva credenciais em arquivo"""
    try:
        filename = f"admin_credentials_{admin_user.id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("🚀 SalasTech - Credenciais do Administrador\n")
            f.write("=" * 45 + "\n\n")
            f.write(f"🌐 URL do Painel: http://localhost:8000/admin\n")
            f.write(f"📧 Email: {dados['email']}\n")
            f.write(f"🔑 Senha: {dados['senha']}\n")
            f.write(f"👤 Nome: {dados['nome']} {dados['sobrenome']}\n")
            f.write(f"🆔 ID: {admin_user.id}\n")
            f.write(f"📅 Criado em: {admin_user.criado_em}\n\n")
            f.write("⚠️  IMPORTANTE:\n")
            f.write("- Guarde este arquivo em local seguro\n")
            f.write("- Delete este arquivo após anotar as credenciais\n")
            f.write("- Altere a senha após o primeiro login\n")
        
        print(f"💾 Credenciais salvas em: {filename}")
        return True
    except Exception as e:
        print(f"⚠️  Erro ao salvar arquivo: {e}")
        return False


def manage_admin_users():
    """
    Interface principal para gerenciar usuários administradores.
    Permite criar, listar, editar e excluir administradores.
    """
    print_header()
    
    # Criar sessão do banco
    db: Session = SessionLocal()
    
    try:
        while True:
            print("\n🚀" + "=" * 40 + "🚀")
            print("      GERENCIAMENTO DE ADMINISTRADORES")
            print("🚀" + "=" * 40 + "🚀")
            print("   1️⃣  Criar novo administrador")
            print("   2️⃣  Listar administradores")
            print("   3️⃣  Editar administrador")
            print("   4️⃣  Excluir administrador")
            print("   5️⃣  Sair")
            
            choice = input("\n🎯 Escolha uma opção (1-5): ").strip()
            
            if choice == "1":
                create_admin_user(db)
            elif choice == "2":
                list_admin_users(db)
            elif choice == "3":
                edit_admin_user(db)
            elif choice == "4":
                delete_admin_user(db)
            elif choice == "5":
                print("\n👋 Até logo!")
                return True
            else:
                print("❌ Opção inválida! Escolha entre 1 e 5.")
    except Exception as e:
        print(f"\n💥 ERRO: {e}")
        return False
    finally:
        db.close()


def create_admin_user(db: Session):
    """
    Cria um usuário administrador.
    """
    clear_screen()
    print("🚀" + "=" * 40 + "🚀")
    print("       CRIAÇÃO DE ADMINISTRADOR")
    print("🚀" + "=" * 40 + "🚀")
    
    try:
        # Mostrar admins existentes
        num_admins = list_existing_admins(db)
        
        print("\n🎯 Vamos criar um novo administrador!\n")
        
        # Coletar dados do administrador
        nome = get_input_with_validation("Nome do administrador")
        sobrenome = get_input_with_validation("Sobrenome do administrador")
        email = get_input_with_validation(
            "Email do administrador",
            validate_email,
            "Email deve ter formato válido (exemplo@dominio.com)"
        )
        
        # Verificar se email já existe
        existing_user = db.query(UsuarioDb).filter(UsuarioDb.email == email).first()
        if existing_user:
            print(f"\n❌ ERRO: Já existe um usuário com o email '{email}'!")
            print("💡 Use um email diferente ou delete o usuário existente.")
            input("\nPressione ENTER para continuar...")
            return False
        
        # Obter senha
        senha = get_password_choice()
        
        # Dados coletados
        dados = {
            'nome': nome,
            'sobrenome': sobrenome,
            'email': email,
            'senha': senha
        }
        
        # Mostrar confirmação
        show_confirmation(dados)
        
        print("\n🤔 Confirma a criação do administrador?")
        confirmacao = input("✅ Digite 'CONFIRMAR' para prosseguir (ou ENTER para cancelar): ").strip()
        
        if confirmacao.upper() != "CONFIRMAR":
            print("❌ Operação cancelada!")
            input("\nPressione ENTER para continuar...")
            return False
        
        print("\n⏳ Criando administrador...")
        
        # Criar hash da senha
        senha_hash = PasswordManager.hash_password(senha)
        
        # Criar usuário administrador
        admin_user = UsuarioDb(
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            senha=senha_hash,
            papel=UserRole.ADMIN
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Sucesso!
        print("\n🎉" + "=" * 45 + "🎉")
        print("        ADMINISTRADOR CRIADO COM SUCESSO!")
        print("🎉" + "=" * 45 + "🎉")
        print(f"   🆔 ID: {admin_user.id}")
        print(f"   👤 Nome: {admin_user.nome} {admin_user.sobrenome}")
        print(f"   📧 Email: {admin_user.email}")
        print(f"   👑 Papel: {admin_user.papel.value}")
        print(f"   📅 Criado em: {admin_user.criado_em}")
        
        print("\n🔑" + "=" * 45 + "🔑")
        print("           CREDENCIAIS DE ACESSO")
        print("🔑" + "=" * 45 + "🔑")
        print(f"   🌐 URL: http://localhost:8000/admin")
        print(f"   📧 Email: {email}")
        print(f"   🔒 Senha: {senha}")
        print("🔑" + "=" * 45 + "🔑")
        
        # Opção de salvar credenciais
        print("\n💾 Deseja salvar as credenciais em arquivo?")
        salvar = input("📁 Digite 's' para salvar ou ENTER para pular: ").strip().lower()
        
        if salvar in ['s', 'sim', 'y', 'yes']:
            save_credentials_to_file(dados, admin_user)
        
        input("\nPressione ENTER para continuar...")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n💥 ERRO: Falha ao criar administrador!")
        print(f"📋 Detalhes: {e}")
        input("\nPressione ENTER para continuar...")
        return False


def list_admin_users(db: Session):
    """
    Lista todos os administradores existentes com detalhes.
    """
    clear_screen()
    print("🚀" + "=" * 40 + "🚀")
    print("       LISTAGEM DE ADMINISTRADORES")
    print("🚀" + "=" * 40 + "🚀")
    
    try:
        admins = db.query(UsuarioDb).filter(UsuarioDb.papel == UserRole.ADMIN).all()
        
        if not admins:
            print("\n⚠️  Nenhum administrador encontrado no sistema!")
            input("\nPressione ENTER para continuar...")
            return
        
        print(f"\n🔍 Encontrados {len(admins)} administrador(es):\n")
        print("-" * 70)
        print(f"{'ID':<5} | {'Nome':<20} | {'Email':<25} | {'Criado em':<19}")
        print("-" * 70)
        
        for admin in admins:
            nome_completo = f"{admin.nome} {admin.sobrenome}"
            criado_em = admin.criado_em.strftime('%d/%m/%Y %H:%M') if admin.criado_em else 'N/A'
            print(f"{admin.id:<5} | {nome_completo:<20} | {admin.email:<25} | {criado_em:<19}")
        
        print("-" * 70)
        
        # Opção para ver detalhes
        print("\n🔍 Deseja ver detalhes de algum administrador?")
        admin_id = input("🆔 Digite o ID (ou ENTER para voltar): ").strip()
        
        if admin_id:
            view_admin_details(db, admin_id)
        
        input("\nPressione ENTER para continuar...")
        
    except Exception as e:
        print(f"\n💥 ERRO: {e}")
        input("\nPressione ENTER para continuar...")


def view_admin_details(db: Session, admin_id):
    """
    Exibe detalhes de um administrador específico.
    """
    try:
        admin = db.query(UsuarioDb).filter(
            UsuarioDb.id == admin_id,
            UsuarioDb.papel == UserRole.ADMIN
        ).first()
        
        if not admin:
            print(f"\n❌ ERRO: Administrador com ID {admin_id} não encontrado!")
            return
        
        clear_screen()
        print("🚀" + "=" * 40 + "🚀")
        print("       DETALHES DO ADMINISTRADOR")
        print("🚀" + "=" * 40 + "🚀")
        
        print(f"\n🆔 ID: {admin.id}")
        print(f"👤 Nome: {admin.nome} {admin.sobrenome}")
        print(f"📧 Email: {admin.email}")
        print(f"👑 Papel: {admin.papel.value}")
        print(f"📅 Criado em: {admin.criado_em}")
        print(f"📅 Atualizado em: {admin.atualizado_em}")
        
    except Exception as e:
        print(f"\n💥 ERRO: {e}")


def edit_admin_user(db: Session):
    """
    Edita informações de um administrador existente.
    """
    clear_screen()
    print("🚀" + "=" * 40 + "🚀")
    print("       EDIÇÃO DE ADMINISTRADOR")
    print("🚀" + "=" * 40 + "🚀")
    
    try:
        # Variável para armazenar senha, se alterada
        senha_alterada = None
        # Listar administradores para seleção
        admins = db.query(UsuarioDb).filter(UsuarioDb.papel == UserRole.ADMIN).all()
        
        if not admins:
            print("\n⚠️  Nenhum administrador encontrado para editar!")
            input("\nPressione ENTER para continuar...")
            return
        
        print("\n🔍 Selecione um administrador para editar:\n")
        print("-" * 60)
        print(f"{'ID':<5} | {'Nome':<20} | {'Email':<25}")
        print("-" * 60)
        
        for admin in admins:
            nome_completo = f"{admin.nome} {admin.sobrenome}"
            print(f"{admin.id:<5} | {nome_completo:<20} | {admin.email:<25}")
        
        print("-" * 60)
        
        admin_id = input("\n🆔 Digite o ID do administrador (ou ENTER para cancelar): ").strip()
        
        if not admin_id:
            print("❌ Operação cancelada!")
            return
        
        # Buscar o administrador
        admin = db.query(UsuarioDb).filter(
            UsuarioDb.id == admin_id,
            UsuarioDb.papel == UserRole.ADMIN
        ).first()
        
        if not admin:
            print(f"\n❌ ERRO: Administrador com ID {admin_id} não encontrado!")
            input("\nPressione ENTER para continuar...")
            return
        
        # Mostrar detalhes atuais e opções de edição
        clear_screen()
        print("🚀" + "=" * 40 + "🚀")
        print("       EDIÇÃO DE ADMINISTRADOR")
        print("🚀" + "=" * 40 + "🚀")
        
        print(f"\n👤 Editando: {admin.nome} {admin.sobrenome} (ID: {admin.id})")
        print(f"📧 Email atual: {admin.email}")
        
        print("\n📝 Selecione o que deseja editar:")
        print("   1️⃣  Nome")
        print("   2️⃣  Sobrenome")
        print("   3️⃣  Email")
        print("   4️⃣  Senha")
        print("   5️⃣  Voltar")
        
        option = input("\n🎯 Escolha uma opção (1-5): ").strip()
        
        if option == "1":
            nome = get_input_with_validation(f"Novo nome (atual: {admin.nome})")
            admin.nome = nome
            campo = "nome"
            
        elif option == "2":
            sobrenome = get_input_with_validation(f"Novo sobrenome (atual: {admin.sobrenome})")
            admin.sobrenome = sobrenome
            campo = "sobrenome"
            
        elif option == "3":
            email = get_input_with_validation(
                f"Novo email (atual: {admin.email})",
                validate_email,
                "Email deve ter formato válido (exemplo@dominio.com)"
            )
            
            # Verificar se o novo email já está em uso
            existing = db.query(UsuarioDb).filter(
                UsuarioDb.email == email,
                UsuarioDb.id != admin.id
            ).first()
            
            if existing:
                print(f"\n❌ ERRO: O email '{email}' já está em uso!")
                input("\nPressione ENTER para continuar...")
                return
            
            admin.email = email
            campo = "email"
            
        elif option == "4":
            print("\n🔄 Alterando senha...")
            senha_alterada = get_password_choice()
            
            # Atualizar senha
            senha_hash = PasswordManager.hash_password(senha_alterada)
            admin.senha = senha_hash
            campo = "senha"
            
        elif option == "5":
            print("↩️  Voltando ao menu principal...")
            return
            
        else:
            print("❌ Opção inválida!")
            input("\nPressione ENTER para continuar...")
            return
        
        # Confirmar alterações
        print(f"\n🤔 Confirma a alteração do campo '{campo}'?")
        confirma = input("✅ Digite 'CONFIRMAR' para prosseguir (ou ENTER para cancelar): ").strip()
        
        if confirma.upper() != "CONFIRMAR":
            print("❌ Operação cancelada!")
            input("\nPressione ENTER para continuar...")
            return
        
        # Salvar alterações
        admin.atualizado_em = datetime.datetime.utcnow()
        db.commit()
        
        print(f"\n✅ Administrador atualizado com sucesso!")
        print(f"🔄 Campo '{campo}' foi alterado.")
        
        # Mostrar senha se foi alterada
        if option == "4" and senha_alterada:
            print(f"\n🔑 Nova senha: {senha_alterada}")
            print("⚠️  IMPORTANTE: Anote esta senha!")
        
        input("\nPressione ENTER para continuar...")
        
    except Exception as e:
        db.rollback()
        print(f"\n💥 ERRO: {e}")
        input("\nPressione ENTER para continuar...")


def delete_admin_user(db: Session):
    """
    Exclui um administrador do sistema.
    """
    clear_screen()
    print("🚀" + "=" * 40 + "🚀")
    print("       EXCLUSÃO DE ADMINISTRADOR")
    print("🚀" + "=" * 40 + "🚀")
    
    try:
        # Listar administradores para seleção
        admins = db.query(UsuarioDb).filter(UsuarioDb.papel == UserRole.ADMIN).all()
        
        if not admins:
            print("\n⚠️  Nenhum administrador encontrado para excluir!")
            input("\nPressione ENTER para continuar...")
            return
        
        # Verificar se temos pelo menos 2 administradores
        if len(admins) < 2:
            print("\n⚠️  ATENÇÃO: Existe apenas um administrador no sistema!")
            print("❌ Não é possível excluir o único administrador.")
            print("💡 Crie outro administrador antes de excluir este.")
            input("\nPressione ENTER para continuar...")
            return
        
        print("\n🔍 Selecione um administrador para excluir:\n")
        print("-" * 60)
        print(f"{'ID':<5} | {'Nome':<20} | {'Email':<25}")
        print("-" * 60)
        
        for admin in admins:
            nome_completo = f"{admin.nome} {admin.sobrenome}"
            print(f"{admin.id:<5} | {nome_completo:<20} | {admin.email:<25}")
        
        print("-" * 60)
        
        admin_id = input("\n🆔 Digite o ID do administrador a excluir (ou ENTER para cancelar): ").strip()
        
        if not admin_id:
            print("❌ Operação cancelada!")
            return
        
        # Buscar o administrador
        admin = db.query(UsuarioDb).filter(
            UsuarioDb.id == admin_id,
            UsuarioDb.papel == UserRole.ADMIN
        ).first()
        
        if not admin:
            print(f"\n❌ ERRO: Administrador com ID {admin_id} não encontrado!")
            input("\nPressione ENTER para continuar...")
            return
        
        # Confirmar exclusão
        print("\n⚠️  ATENÇÃO: Esta operação não pode ser desfeita!")
        print(f"🗑️  Você está prestes a excluir o administrador:")
        print(f"   👤 {admin.nome} {admin.sobrenome}")
        print(f"   📧 {admin.email}")
        print(f"   🆔 ID: {admin.id}")
        
        confirm = input("\n⚠️  Digite o email do administrador para confirmar a exclusão: ").strip()
        
        if confirm != admin.email:
            print("❌ Email incorreto! Operação cancelada.")
            input("\nPressione ENTER para continuar...")
            return
        
        print("\n🔄 Excluindo administrador...")
        
        # Excluir administrador
        db.delete(admin)
        db.commit()
        
        print("\n✅ Administrador excluído com sucesso!")
        input("\nPressione ENTER para continuar...")
        
    except Exception as e:
        db.rollback()
        print(f"\n💥 ERRO: {e}")
        input("\nPressione ENTER para continuar...")


def main():
    """
    Função principal do script.
    """
    try:
        print("🌟 Bem-vindo ao SalasTech Admin Creator!")
        
        # Verificar se está no diretório correto
        if not os.path.exists("app/models/db.py"):
            print("\n❌ ERRO: Execute este script a partir do diretório raiz do projeto!")
            print("💡 Navegue até o diretório SalasTech-backend e execute novamente.")
            sys.exit(1)
        
        success = manage_admin_users()
        
        if success:
            print("\n" + "🎊" * 15)
            print("🎉 PROCESSO CONCLUÍDO COM SUCESSO! 🎉")
            print("🎊" * 15)
            
            # Menu pós-criação
            print("\n🎯 Próximos passos:")
            print("   1️⃣  Iniciar o servidor SalasTech")
            print("   2️⃣  Acessar o painel administrativo")
            print("   3️⃣  Voltar ao gerenciamento de administradores")
            print("   4️⃣  Sair")
            
            while True:
                choice = input("\n🚀 Escolha uma opção (1/2/3/4): ").strip()
                
                if choice == "1":
                    print("\n🔥 Para iniciar o servidor, execute:")
                    print("   uvicorn app.main:app --reload --port 8000")
                    break
                elif choice == "2":
                    print("\n🌐 Acesse o painel em: http://localhost:8000/admin")
                    print("📱 Certifique-se de que o servidor está rodando!")
                    break
                elif choice == "3":
                    return main()  # Volta ao menu de gerenciamento
                elif choice == "4":
                    print("\n👋 Até logo!")
                    break
                else:
                    print("❌ Opção inválida! Escolha 1, 2, 3 ou 4.")
            
            sys.exit(0)
        else:
            print("\n" + "💥" * 15)
            print("💔 PROCESSO FALHOU!")
            print("💥" * 15)
            
            retry = input("\n🔄 Deseja tentar novamente? (s/N): ").strip().lower()
            if retry in ['s', 'sim', 'y', 'yes']:
                return main()  # Tentar novamente
            
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚡ Operação interrompida pelo usuário!")
        print("👋 Até logo!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 ERRO INESPERADO: {e}")
        print("\n🔧 Possíveis soluções:")
        print("   • Verifique a conexão com o banco de dados")
        print("   • Confirme se todas as dependências estão instaladas")
        print("   • Execute 'pip install -r requirements.txt'")
        print("   • Verifique se as migrações foram aplicadas")
        sys.exit(1)


if __name__ == "__main__":
    main()

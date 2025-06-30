#!/usr/bin/env python3
"""
SalasTech Admin Manager - Gerenciador Completo de Administradores

Este script oferece um menu interativo para gerenciar administradores do sistema:
- Criar novos administradores
- Listar administradores existentes
- Alterar senhas
- Atualizar dados pessoais
- Promover/rebaixar usuários
- Desativar/reativar contas
"""

import os
import sys
import secrets
import string
import getpass
from datetime import datetime
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent.parent
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
    print("🛡️" + "=" * 60 + "🛡️")
    print("               SalasTech - Admin Manager")
    print("            Gerenciador de Administradores")
    print("🛡️" + "=" * 60 + "🛡️")
    print()


def generate_random_password(length=12):
    """Gera uma senha aleatória segura"""
    characters = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(secrets.choice(characters) for _ in range(length))


def validate_email(email):
    """Validação básica de email"""
    return "@" in email and "." in email.split("@")[1]


def get_input_with_validation(prompt, validator=None, error_msg="Entrada inválida!", allow_empty=False):
    """Solicita entrada com validação"""
    while True:
        value = input(f"📝 {prompt}: ").strip()
        if not value and not allow_empty:
            print(f"❌ {prompt} é obrigatório!")
            continue
        if value and validator and not validator(value):
            print(f"❌ {error_msg}")
            continue
        return value


def get_password_choice(current_password=None):
    """Menu para escolha de senha"""
    if current_password:
        print("\n🔐 Alterar Senha:")
        print("   1️⃣  Digitar nova senha manualmente")
        print("   2️⃣  Gerar senha aleatória segura")
        print("   3️⃣  Manter senha atual")
    else:
        print("\n🔐 Configuração de Senha:")
        print("   1️⃣  Digitar senha manualmente")
        print("   2️⃣  Gerar senha aleatória segura")
        print("   3️⃣  Usar senha padrão (admin123)")
    
    while True:
        choice = input(f"\n🎯 Escolha uma opção (1/2/3): ").strip()
        
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
            if current_password:
                return None  # Manter senha atual
            else:
                print("🔑 Usando senha padrão: admin123")
                print("⚠️  IMPORTANTE: Altere esta senha após o primeiro login!")
                return "admin123"
            
        else:
            print("❌ Opção inválida! Escolha 1, 2 ou 3.")


def list_all_users(db, filter_role=None):
    """Lista usuários com filtro opcional por papel"""
    query = db.query(UsuarioDb)
    
    if filter_role:
        query = query.filter(UsuarioDb.papel == filter_role)
    
    users = query.order_by(UsuarioDb.nome, UsuarioDb.sobrenome).all()
    
    if not users:
        role_text = f" {filter_role.value}s" if filter_role else ""
        print(f"📭 Nenhum usuário{role_text} encontrado.")
        return []
    
    print(f"\n👥 {'Administradores' if filter_role == UserRole.ADMIN else 'Usuários'} ({len(users)}):")
    print("-" * 80)
    
    for i, user in enumerate(users, 1):
        status = "🟢 Ativo" if getattr(user, 'ativo', True) else "🔴 Inativo"
        role_icon = {"ADMIN": "👑", "MANAGER": "👔", "USER": "👤"}.get(user.papel.name, "❓")
        
        print(f"{i:2}. {role_icon} {user.nome} {user.sobrenome}")
        print(f"    📧 {user.email}")
        print(f"    🆔 ID: {user.id} | 👑 {user.papel.value} | {status}")
        print(f"    📅 Criado: {user.criado_em.strftime('%d/%m/%Y %H:%M')}")
        print("-" * 80)
    
    return users


def create_admin_user(db):
    """Cria um novo administrador"""
    print("\n🆕 Criar Novo Administrador")
    print("=" * 30)
    
    # Coletar dados
    nome = get_input_with_validation("Nome")
    sobrenome = get_input_with_validation("Sobrenome")
    email = get_input_with_validation(
        "Email",
        validate_email,
        "Email deve ter formato válido (exemplo@dominio.com)"
    )
    
    # Verificar se email já existe
    existing_user = db.query(UsuarioDb).filter(UsuarioDb.email == email).first()
    if existing_user:
        print(f"\n❌ ERRO: Já existe um usuário com o email '{email}'!")
        return False
    
    # Obter senha
    senha = get_password_choice()
    if not senha:  # Se senha for None (manter atual), não deveria chegar aqui
        print("❌ Erro na configuração da senha!")
        return False
    
    # Confirmar criação
    print(f"\n📋 Dados do novo administrador:")
    print(f"   👤 Nome: {nome} {sobrenome}")
    print(f"   📧 Email: {email}")
    print(f"   🔑 Senha: {'*' * len(senha)}")
    print(f"   👑 Papel: Administrador")
    
    if input("\n✅ Confirmar criação? (s/N): ").strip().lower() not in ['s', 'sim', 'y', 'yes']:
        return False
    
    try:
        # Criar usuário
        admin_user = UsuarioDb(
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            senha=PasswordManager.hash_password(senha),
            papel=UserRole.ADMIN
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"\n✅ Administrador criado com sucesso!")
        print(f"   🆔 ID: {admin_user.id}")
        print(f"   📧 Email: {email}")
        print(f"   🔑 Senha: {senha}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar administrador: {e}")
        return False


def change_user_password(db):
    """Altera senha de um usuário"""
    print("\n🔄 Alterar Senha de Usuário")
    print("=" * 30)
    
    # Listar usuários
    users = list_all_users(db)
    if not users:
        return False
    
    # Selecionar usuário
    while True:
        try:
            choice = int(input(f"\n🎯 Escolha um usuário (1-{len(users)}): "))
            if 1 <= choice <= len(users):
                user = users[choice - 1]
                break
            else:
                print("❌ Número inválido!")
        except ValueError:
            print("❌ Digite um número válido!")
    
    print(f"\n👤 Usuário selecionado: {user.nome} {user.sobrenome} ({user.email})")
    
    # Obter nova senha
    nova_senha = get_password_choice(current_password=True)
    
    if nova_senha is None:
        print("⏭️ Senha mantida inalterada.")
        return True
    
    # Confirmar alteração
    if input("\n✅ Confirmar alteração de senha? (s/N): ").strip().lower() not in ['s', 'sim', 'y', 'yes']:
        return False
    
    try:
        user.senha = PasswordManager.hash_password(nova_senha)
        db.commit()
        
        print(f"\n✅ Senha alterada com sucesso!")
        print(f"   👤 Usuário: {user.nome} {user.sobrenome}")
        print(f"   📧 Email: {user.email}")
        print(f"   🔑 Nova senha: {nova_senha}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao alterar senha: {e}")
        return False


def update_user_info(db):
    """Atualiza informações pessoais do usuário"""
    print("\n✏️ Atualizar Dados do Usuário")
    print("=" * 30)
    
    # Listar usuários
    users = list_all_users(db)
    if not users:
        return False
    
    # Selecionar usuário
    while True:
        try:
            choice = int(input(f"\n🎯 Escolha um usuário (1-{len(users)}): "))
            if 1 <= choice <= len(users):
                user = users[choice - 1]
                break
            else:
                print("❌ Número inválido!")
        except ValueError:
            print("❌ Digite um número válido!")
    
    print(f"\n👤 Editando: {user.nome} {user.sobrenome} ({user.email})")
    print("💡 Deixe em branco para manter o valor atual")
    
    # Coletar novos dados
    nome = get_input_with_validation(f"Nome [{user.nome}]", allow_empty=True) or user.nome
    sobrenome = get_input_with_validation(f"Sobrenome [{user.sobrenome}]", allow_empty=True) or user.sobrenome
    email = get_input_with_validation(f"Email [{user.email}]", allow_empty=True) or user.email
    
    # Verificar se novo email já existe
    if email != user.email:
        existing = db.query(UsuarioDb).filter(UsuarioDb.email == email, UsuarioDb.id != user.id).first()
        if existing:
            print(f"❌ Email '{email}' já está em uso!")
            return False
    
    # Mostrar alterações
    print(f"\n📋 Alterações propostas:")
    if nome != user.nome:
        print(f"   👤 Nome: {user.nome} → {nome}")
    if sobrenome != user.sobrenome:
        print(f"   👤 Sobrenome: {user.sobrenome} → {sobrenome}")
    if email != user.email:
        print(f"   📧 Email: {user.email} → {email}")
    
    if nome == user.nome and sobrenome == user.sobrenome and email == user.email:
        print("   ℹ️ Nenhuma alteração detectada")
        return True
    
    # Confirmar alterações
    if input("\n✅ Confirmar alterações? (s/N): ").strip().lower() not in ['s', 'sim', 'y', 'yes']:
        return False
    
    try:
        user.nome = nome
        user.sobrenome = sobrenome
        user.email = email
        db.commit()
        
        print(f"\n✅ Dados atualizados com sucesso!")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao atualizar dados: {e}")
        return False


def change_user_role(db):
    """Altera papel do usuário (promover/rebaixar)"""
    print("\n👑 Alterar Papel do Usuário")
    print("=" * 30)
    
    # Listar usuários não-admin
    users = list_all_users(db)
    if not users:
        return False
    
    # Selecionar usuário
    while True:
        try:
            choice = int(input(f"\n🎯 Escolha um usuário (1-{len(users)}): "))
            if 1 <= choice <= len(users):
                user = users[choice - 1]
                break
            else:
                print("❌ Número inválido!")
        except ValueError:
            print("❌ Digite um número válido!")
    
    print(f"\n� Usuário: {user.nome} {user.sobrenome}")
    print(f"👑 Papel atual: {user.papel.value}")
    
    # Mostrar opções de papel
    roles = {
        '1': (UserRole.USER, "👤 Usuário"),
        '2': (UserRole.GESTOR, "👔 Gestor"),
        '3': (UserRole.ADMIN, "👑 Administrador"),
        '4': (UserRole.USUARIO_AVANCADO, "🔧 Usuário Avançado")
    }
    
    print("\n🎭 Papéis disponíveis:")
    for key, (role, desc) in roles.items():
        current = " (ATUAL)" if role == user.papel else ""
        print(f"   {key}. {desc}{current}")
    
    while True:
        choice = input("\n🎯 Escolha o novo papel (1/2/3): ").strip()
        if choice in roles:
            new_role, role_desc = roles[choice]
            break
        print("❌ Opção inválida!")
    
    if new_role == user.papel:
        print("ℹ️ Papel já está definido como selecionado.")
        return True
    
    # Confirmar alteração
    print(f"\n🔄 Alterar papel:")
    print(f"   De: {user.papel.value}")
    print(f"   Para: {new_role.value}")
    
    if input("\n✅ Confirmar alteração? (s/N): ").strip().lower() not in ['s', 'sim', 'y', 'yes']:
        return False
    
    try:
        user.papel = new_role
        db.commit()
        
        print(f"\n✅ Papel alterado com sucesso!")
        print(f"   👤 {user.nome} {user.sobrenome}")
        print(f"   👑 Novo papel: {new_role.value}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao alterar papel: {e}")
        return False


def save_credentials_file(user_data, password):
    """Salva credenciais em arquivo"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"admin_credentials_{user_data['id']}_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("🛡️ SalasTech - Credenciais de Administrador\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"🌐 URL do Painel: http://localhost:8000/admin\n")
            f.write(f"📧 Email: {user_data['email']}\n")
            f.write(f"🔑 Senha: {password}\n")
            f.write(f"👤 Nome: {user_data['nome']} {user_data['sobrenome']}\n")
            f.write(f"🆔 ID: {user_data['id']}\n")
            f.write(f"👑 Papel: {user_data['papel']}\n")
            f.write(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            f.write("⚠️  IMPORTANTE:\n")
            f.write("- Guarde este arquivo em local seguro\n")
            f.write("- Delete este arquivo após anotar as credenciais\n")
            f.write("- Altere a senha após o primeiro login\n")
        
        print(f"💾 Credenciais salvas em: {filename}")
        return True
    except Exception as e:
        print(f"⚠️ Erro ao salvar arquivo: {e}")
        return False


def show_main_menu():
    """Exibe o menu principal"""
    print("🎯 Menu Principal:")
    print("   1️⃣  Criar novo administrador")
    print("   2️⃣  Listar todos os usuários")
    print("   3️⃣  Listar apenas administradores")
    print("   4️⃣  Alterar senha de usuário")
    print("   5️⃣  Editar dados pessoais")
    print("   6️⃣  Alterar papel do usuário")
    print("   7️⃣  Salvar credenciais em arquivo")
    print("   0️⃣  Sair")
    print()


def main():
    """Função principal do gerenciador"""
    while True:
        print_header()
        
        # Verificar conexão com banco
        try:
            db = SessionLocal()
            # Teste básico de conexão
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
        except Exception as e:
            print(f"❌ Erro de conexão com banco de dados: {e}")
            print("🔧 Verifique se o banco está configurado corretamente.")
            input("\n📋 Pressione ENTER para tentar novamente...")
            continue
        
        show_main_menu()
        
        choice = "0"  # Valor padrão
        try:
            choice = input("🎯 Escolha uma opção (0-7): ").strip()
            
            if choice == "0":
                print("\n👋 Obrigado por usar o SalasTech Admin Manager!")
                print("🛡️ Mantenha sempre suas credenciais seguras!")
                break
            
            elif choice == "1":
                create_admin_user(db)
                
            elif choice == "2":
                list_all_users(db)
                
            elif choice == "3":
                list_all_users(db, filter_role=UserRole.ADMIN)
                
            elif choice == "4":
                change_user_password(db)
                
            elif choice == "5":
                update_user_info(db)
                
            elif choice == "6":
                change_user_role(db)
                
            elif choice == "7":
                save_credentials_menu(db)
                
            else:
                print("❌ Opção inválida! Escolha um número de 0 a 7.")
            
        except KeyboardInterrupt:
            print("\n\n🛑 Operação cancelada pelo usuário.")
            
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            
        finally:
            try:
                db.close()
            except:
                pass
        
        if choice != "0":
            input("\n📋 Pressione ENTER para continuar...")


def save_credentials_menu(db):
    """Menu para salvar credenciais de um usuário"""
    print("\n💾 Salvar Credenciais")
    print("=" * 25)
    
    # Listar administradores
    admins = list_all_users(db, filter_role=UserRole.ADMIN)
    if not admins:
        return False
    
    # Selecionar administrador
    while True:
        try:
            choice = int(input(f"\n🎯 Escolha um administrador (1-{len(admins)}): "))
            if 1 <= choice <= len(admins):
                admin = admins[choice - 1]
                break
            else:
                print("❌ Número inválido!")
        except ValueError:
            print("❌ Digite um número válido!")
    
    print(f"\n👤 Administrador: {admin.nome} {admin.sobrenome}")
    print("⚠️  Para salvar as credenciais, será necessário definir uma nova senha.")
    
    # Obter nova senha
    senha = get_password_choice(current_password=False)
    if not senha:
        print("❌ Operação cancelada.")
        return False
    
    try:
        # Atualizar senha no banco
        admin.senha = PasswordManager.hash_password(senha)
        db.commit()
        
        # Preparar dados do usuário
        user_data = {
            'id': admin.id,
            'email': admin.email,
            'nome': admin.nome,
            'sobrenome': admin.sobrenome,
            'papel': admin.papel.value
        }
        
        # Salvar arquivo
        if save_credentials_file(user_data, senha):
            print(f"\n✅ Credenciais salvas e senha atualizada!")
        else:
            print(f"\n⚠️ Senha atualizada, mas erro ao salvar arquivo.")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao atualizar senha: {e}")
        return False


if __name__ == "__main__":
    main()

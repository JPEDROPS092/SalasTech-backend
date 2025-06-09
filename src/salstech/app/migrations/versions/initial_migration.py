"""Initial database migration

Revision ID: 001_initial_migration
Revises: 
Create Date: 2025-05-30 22:20:46

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from salstech.app.models import enums

# revision identifiers, used by Alembic.
revision = '001_initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create departments table
    op.create_table('departments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), server_onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create index on department code for faster lookups
    op.create_index(op.f('ix_departments_code'), 'departments', ['code'], unique=True)
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('surname', sa.String(), nullable=False),
        sa.Column('role', sa.Enum(enums.UserRole), nullable=False, default=enums.UserRole.USER),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), server_onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create indexes for frequently queried fields
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    op.create_index(op.f('ix_users_department_id'), 'users', ['department_id'], unique=False)
    
    # Create tax_accounts table
    op.create_table('tax_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rate', sa.Float(precision=2), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), server_onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for tax_accounts
    op.create_index(op.f('ix_tax_accounts_id'), 'tax_accounts', ['id'], unique=True)
    
    # Create salaries table
    op.create_table('salaries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(precision=2), nullable=False),
        sa.Column('amount_hours', sa.Float(precision=1), nullable=False),
        sa.Column('salary_date', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), server_onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for salaries
    op.create_index(op.f('ix_salaries_user_id'), 'salaries', ['user_id'], unique=False)
    op.create_index(op.f('ix_salaries_salary_date'), 'salaries', ['salary_date'], unique=False)
    
    # Create rooms table
    op.create_table('rooms',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('building', sa.String(), nullable=False),
        sa.Column('floor', sa.String(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum(enums.RoomStatus), nullable=False, default=enums.RoomStatus.ATIVA),
        sa.Column('responsible', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), server_onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create indexes for rooms
    op.create_index(op.f('ix_rooms_code'), 'rooms', ['code'], unique=True)
    op.create_index(op.f('ix_rooms_department_id'), 'rooms', ['department_id'], unique=False)
    op.create_index(op.f('ix_rooms_status'), 'rooms', ['status'], unique=False)
    
    # Create room_resources table
    op.create_table('room_resources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('resource_name', sa.String(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, default=1),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), server_onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for room_resources
    op.create_index(op.f('ix_room_resources_room_id'), 'room_resources', ['room_id'], unique=False)
    
    # Create reservations table
    op.create_table('reservations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_datetime', sa.DateTime(), nullable=False),
        sa.Column('end_datetime', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum(enums.ReservationStatus), nullable=False, default=enums.ReservationStatus.PENDENTE),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), server_onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for reservations
    op.create_index(op.f('ix_reservations_room_id'), 'reservations', ['room_id'], unique=False)
    op.create_index(op.f('ix_reservations_user_id'), 'reservations', ['user_id'], unique=False)
    op.create_index(op.f('ix_reservations_start_datetime'), 'reservations', ['start_datetime'], unique=False)
    op.create_index(op.f('ix_reservations_end_datetime'), 'reservations', ['end_datetime'], unique=False)
    op.create_index(op.f('ix_reservations_status'), 'reservations', ['status'], unique=False)
    
    # Add foreign key constraint for departments.manager_id
    op.create_foreign_key('fk_departments_manager_id', 'departments', 'users', ['manager_id'], ['id'])


def downgrade() -> None:
    # Drop the foreign key constraint for departments.manager_id
    op.drop_constraint('fk_departments_manager_id', 'departments', type_='foreignkey')
    
    # Drop all tables in reverse order
    op.drop_table('reservations')
    op.drop_table('room_resources')
    op.drop_table('rooms')
    op.drop_table('salaries')
    op.drop_table('tax_accounts')
    op.drop_table('users')
    op.drop_table('departments')

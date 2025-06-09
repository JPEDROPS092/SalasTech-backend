#!/usr/bin/env bash

# Colors for better output formatting
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

help_message() {
    echo -e "${BLUE}IFAM FastAPI Database Migration Manager${NC}"
    echo -e "Usage: $0 <command> [options]"
    echo -e "\nCommands:"
    echo -e "  ${GREEN}generate${NC} [message]   Generate a new migration with optional message"
    echo -e "  ${GREEN}apply${NC} [revision]     Apply migrations up to specified revision (default: head)"
    echo -e "  ${GREEN}revert${NC} [steps]       Downgrade by specified number of steps (default: 1)"
    echo -e "  ${GREEN}all${NC} [message]        Generate and apply the latest migration"
    echo -e "  ${GREEN}status${NC}              Show current migration status"
    echo -e "  ${GREEN}history${NC}             Show migration history"
    echo -e "  ${GREEN}stamp${NC} <revision>    Stamp the database with the specified revision"
    echo -e "  ${GREEN}init${NC}                Initialize a new migration environment"
}

check_alembic() {
    if ! command -v alembic &> /dev/null; then
        echo -e "${RED}Error: alembic command not found${NC}"
        echo -e "Please install alembic with: pip install alembic"
        exit 1
    fi
}

generate_migration() {
    check_alembic
    
    local message="$1"
    if [ -z "$message" ]; then
        echo -e "${YELLOW}No message provided, using default message${NC}"
        message="Automatic migration"
    fi
    
    echo -e "${BLUE}Generating migration with message: ${message}${NC}"
    if alembic revision --autogenerate -m "$message"; then
        echo -e "${GREEN}Migration generated successfully${NC}"
    else
        echo -e "${RED}Failed to generate migration${NC}"
        exit 1
    fi
}

apply_migration() {
    check_alembic
    
    local target="$1"
    if [ -z "$target" ]; then
        target="head"
    fi
    
    echo -e "${BLUE}Applying migration to: ${target}${NC}"
    if alembic upgrade "$target"; then
        echo -e "${GREEN}Migration applied successfully${NC}"
    else
        echo -e "${RED}Failed to apply migration${NC}"
        exit 1
    fi
}

downgrade_migration() {
    check_alembic
    
    local steps="$1"
    if [ -z "$steps" ]; then
        steps="1"
    fi
    
    echo -e "${YELLOW}Downgrading ${steps} migration(s)...${NC}"
    if alembic downgrade -"$steps"; then
        echo -e "${GREEN}Downgrade completed successfully${NC}"
    else
        echo -e "${RED}Failed to downgrade migration${NC}"
        exit 1
    fi
}

all() {
    echo -e "${BLUE}Generating and applying migration...${NC}"
    generate_migration "$1" && apply_migration
}

show_status() {
    check_alembic
    
    echo -e "${BLUE}Current migration status:${NC}"
    alembic current
    
    echo -e "\n${BLUE}Migration history:${NC}"
    alembic history --verbose
}

show_history() {
    check_alembic
    
    echo -e "${BLUE}Migration history:${NC}"
    alembic history --verbose
}

stamp_revision() {
    check_alembic
    
    local revision="$1"
    if [ -z "$revision" ]; then
        echo -e "${RED}Error: No revision specified for stamp command${NC}"
        help_message
        exit 1
    fi
    
    echo -e "${YELLOW}Stamping database with revision: ${revision}${NC}"
    if alembic stamp "$revision"; then
        echo -e "${GREEN}Database stamped successfully${NC}"
    else
        echo -e "${RED}Failed to stamp database${NC}"
        exit 1
    fi
}

init_migrations() {
    check_alembic
    
    echo -e "${BLUE}Initializing migration environment...${NC}"
    if [ -d "migrations" ]; then
        echo -e "${YELLOW}Migration directory already exists${NC}"
    else
        if alembic init migrations; then
            echo -e "${GREEN}Migration environment initialized successfully${NC}"
            echo -e "${YELLOW}Remember to configure the alembic.ini file with your database connection${NC}"
        else
            echo -e "${RED}Failed to initialize migration environment${NC}"
            exit 1
        fi
    fi
}

# Check if the script is being run with the correct arguments
if [ "$#" -lt 1 ]; then
    echo -e "${RED}Error: No command specified${NC}"
    help_message
    exit 1
fi

COMMAND="$1"
shift  # Remove the first argument, leaving any additional arguments

# Check the command and call the appropriate function
case "$COMMAND" in
    generate)
        generate_migration "$1"
        ;;
    apply)
        apply_migration "$1"
        ;;
    all)
        all "$1"
        ;;
    revert)
        downgrade_migration "$1"
        ;;
    status)
        show_status
        ;;
    history)
        show_history
        ;;
    stamp)
        stamp_revision "$1"
        ;;
    init)
        init_migrations
        ;;
    help)
        help_message
        ;;
    *)
        echo -e "${RED}Invalid command: $COMMAND${NC}"
        help_message
        exit 1
        ;;
esac
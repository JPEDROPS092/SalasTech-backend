#!/usr/bin/env python3
"""
Script para executar os testes do sistema de gerenciamento de salas.
Suporta testes unitários, de integração e end-to-end.
"""

import os
import sys
import pytest
import argparse
import time


def run_tests(args):
    """Executa os testes com as opções especificadas."""
    # Configura os argumentos para o pytest
    pytest_args = []
    
    # Adiciona verbose se solicitado
    if args.verbose:
        pytest_args.append("-v")
    
    # Adiciona cobertura de código se solicitado
    if args.coverage:
        pytest_args.extend(["--cov=app", "--cov-report=term", "--cov-report=html"])
    
    # Adiciona relatório em XML se solicitado
    if args.xml_report:
        pytest_args.append("--junitxml=test-reports/results.xml")
    
    # Adiciona marcadores específicos se solicitado
    if args.markers:
        pytest_args.extend(["-m", args.markers])
    
    # Determina quais testes executar com base no tipo
    if args.test_type == "all":
        if args.test_path:
            pytest_args.append(args.test_path)
        else:
            pytest_args.append("tests/")
    elif args.test_type == "unit":
        if args.test_path:
            pytest_args.append(os.path.join("tests/unit", args.test_path))
        else:
            pytest_args.append("tests/unit/")
    elif args.test_type == "integration":
        if args.test_path:
            pytest_args.append(os.path.join("tests/integration", args.test_path))
        else:
            pytest_args.append("tests/integration/")
    elif args.test_type == "e2e":
        if args.test_path:
            pytest_args.append(os.path.join("tests/e2e", args.test_path))
        else:
            pytest_args.append("tests/e2e/")
    
    # Executa os testes
    start_time = time.time()
    result = pytest.main(pytest_args)
    end_time = time.time()
    
    # Exibe o tempo de execução
    print(f"\nTempo de execução: {end_time - start_time:.2f} segundos")
    
    return result


if __name__ == "__main__":
    # Configura o parser de argumentos
    parser = argparse.ArgumentParser(description="Executa os testes do sistema de gerenciamento de salas.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Exibe informações detalhadas durante a execução dos testes.")
    parser.add_argument("-c", "--coverage", action="store_true", help="Gera relatório de cobertura de código.")
    parser.add_argument("-x", "--xml-report", action="store_true", help="Gera relatório de testes em formato XML.")
    parser.add_argument("-m", "--markers", help="Executa apenas testes com os marcadores especificados.")
    parser.add_argument("-t", "--test-type", choices=["all", "unit", "integration", "e2e"], default="all",
                        help="Tipo de testes a executar (all, unit, integration, e2e).")
    parser.add_argument("test_path", nargs="?", help="Caminho específico para executar testes (arquivo ou diretório).")
    
    # Analisa os argumentos
    args = parser.parse_args()
    
    # Cria diretório para relatórios se necessário
    if args.xml_report:
        os.makedirs("test-reports", exist_ok=True)
    
    # Cria diretório para relatórios de cobertura se necessário
    if args.coverage:
        os.makedirs("coverage-reports", exist_ok=True)
    
    # Exibe informações sobre os testes que serão executados
    test_type_desc = {
        "all": "todos os testes",
        "unit": "testes unitários",
        "integration": "testes de integração",
        "e2e": "testes end-to-end"
    }
    
    print(f"Executando {test_type_desc[args.test_type]}...")
    if args.test_path:
        print(f"Caminho específico: {args.test_path}")
    if args.markers:
        print(f"Marcadores: {args.markers}")
    
    # Executa os testes
    sys.exit(run_tests(args))

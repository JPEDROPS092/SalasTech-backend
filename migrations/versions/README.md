# Versões de migração

Este diretório contém todos os scripts de migração de banco de dados do SalasTech.

As migrações são geradas pelo Alembic e organizadas em ordem cronológica.

## Nomenclatura

Os arquivos de migração seguem o formato:
`{ano}_{mês}_{dia}_{hora}{minuto}-{revision_id}_{slug}.py`

Por exemplo: `2025_06_26_1045-a1b2c3d4_adicionar_campo_status.py`

## Importante

- Não modifique scripts de migração já aplicados
- Ao criar scripts manualmente, garanta que eles são idempotentes
- Os scripts devem sempre conter métodos `upgrade()` e `downgrade()`

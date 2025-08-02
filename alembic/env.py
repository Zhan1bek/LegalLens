from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ─── импорт настроек и моделей проекта ────────────────────
from app.core.config import get_settings
from app.db import Base  # Base уже импортирует Document

# ───────────────────────────────────────────────────────────

# Alembic Config object
config = context.config

# подставляем URL из .env
settings = get_settings()
config.set_main_option("sqlalchemy.url", str(settings.database_url))

# настроим логирование (шаблонный код)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# главное: передаём MetaData всех моделей
target_metadata = Base.metadata


# ───────────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,  # удобно ловить смену типов
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

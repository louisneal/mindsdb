"""add training log table

Revision ID: a1b2c3d4e5f6
Revises: 608e376c19a7
Create Date: 2025-09-29 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import mindsdb.interfaces.storage.db  # noqa

# revision identifiers, used by Alembic.
revision = "b6b2c3d40caa"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():

    # 内置 TimesFM
    op.get_bind().execute(sa.text("""INSERT INTO "predictor" ("id", "updated_at", "created_at", "deleted_at", "name", "data", "to_predict", "company_id", "mindsdb_version", "native_version", "integration_id", "data_integration_ref", "fetch_data_query", "learn_args", "update_status", "status", "active", "training_data_columns_count", "training_data_rows_count", "training_start_at", "training_stop_at", "label", "version", "code", "lightwood_version", "dtype_dict", "project_id", "training_phase_current", "training_phase_total", "training_phase_name", "training_metadata") VALUES (1000, '2025-09-26 15:44:55.666292', '2025-09-26 15:44:50.123764', NULL, 'timesfm', '{"name": "timesfm"}', 'nil', NULL, '25.9.1.2', NULL, 1000, '{"type": "project"}', 'SELECT 0.0 AS nil, 0.0 AS data_col, ''2025-01-01'' AS timestamp_col, 12 AS horizon', '{"__mdb_sql_task": null, "target": "nil", "using": {}}', 'up_to_date', 'complete', 1, 4, 1, '2025-09-26 15:44:50.116771', '2025-09-26 15:44:55.665292', NULL, 1, NULL, NULL, NULL, 1, NULL, NULL, NULL, '{"hostname": "H-02005", "reason": "learn", "process_id": 46968}');"""))
    op.get_bind().execute(sa.text("""INSERT INTO "integration" ("id", "updated_at", "created_at", "name", "engine", "data", "company_id") VALUES (1000, '2025-09-26 15:10:15.914908', '2025-09-26 15:10:15.914908', 'timesfm', 'timesfm', '{}', NULL);"""))
    op.get_bind().execute(sa.text("""INSERT INTO "json_storage" ("id", "resource_group", "resource_id", "name", "content", "encrypted_content", "company_id") VALUES (1000, 'predictor', 1000, 'saved_args', '{}', NULL, NULL);"""))

    op.drop_table("training_log", if_exists=True)

    op.create_table(
        "training_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(), nullable=False, comment="Model name"),
        sa.Column("model_version", sa.String(), nullable=False, comment="Model version"),
        sa.Column("level", sa.String(), nullable=False, comment="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
        sa.Column("logger_name", sa.String(), nullable=True, comment="Logger name"),
        sa.Column("message", sa.Text(), nullable=False, comment="Log message"),
        sa.Column("process_name", sa.String(), nullable=True, comment="Process name"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id")
    )

    # 创建索引以提高查询性能
    op.create_index("idx_training_log_id", "training_log", ["model_name", "model_version"])
    op.create_index("idx_training_log_created_at", "training_log", ["created_at"])
    op.create_index("idx_training_log_level", "training_log", ["level"])


def downgrade():
    op.drop_index("idx_training_log_level", "training_log")
    op.drop_index("idx_training_log_created_at", "training_log")
    op.drop_index("idx_training_log_tid", "training_log")
    op.drop_table("training_log")
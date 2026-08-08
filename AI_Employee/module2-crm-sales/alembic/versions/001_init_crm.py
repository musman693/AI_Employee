from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("owner_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_customers_email"), "customers", ["email"], unique=False)
    op.create_index(op.f("ix_customers_id"), "customers", ["id"], unique=False)
    op.create_index(op.f("ix_customers_owner_id"), "customers", ["owner_id"], unique=False)

    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=100), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("assigned_to", sa.String(length=100), nullable=True),
        sa.Column("converted_customer_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_leads_assigned_to"), "leads", ["assigned_to"], unique=False)
    op.create_index(op.f("ix_leads_email"), "leads", ["email"], unique=False)
    op.create_index(op.f("ix_leads_id"), "leads", ["id"], unique=False)
    op.create_index(op.f("ix_leads_status"), "leads", ["status"], unique=False)

    op.create_table(
        "deals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("stage", sa.String(length=100), nullable=False),
        sa.Column("probability", sa.Integer(), nullable=True),
        sa.Column("expected_close_date", sa.Date(), nullable=True),
        sa.Column("owner_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_deals_customer_id"), "deals", ["customer_id"], unique=False)
    op.create_index(op.f("ix_deals_id"), "deals", ["id"], unique=False)
    op.create_index(op.f("ix_deals_owner_id"), "deals", ["owner_id"], unique=False)
    op.create_index(op.f("ix_deals_stage"), "deals", ["stage"], unique=False)

    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("lead_id", sa.Integer(), nullable=True),
        sa.Column("activity_type", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_activities_activity_type"), "activities", ["activity_type"], unique=False)
    op.create_index(op.f("ix_activities_created_by"), "activities", ["created_by"], unique=False)
    op.create_index(op.f("ix_activities_customer_id"), "activities", ["customer_id"], unique=False)
    op.create_index(op.f("ix_activities_id"), "activities", ["id"], unique=False)
    op.create_index(op.f("ix_activities_lead_id"), "activities", ["lead_id"], unique=False)

    op.create_table(
        "pipeline_stages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_won", sa.Boolean(), nullable=True),
        sa.Column("is_lost", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )


def downgrade() -> None:
    op.drop_table("pipeline_stages")
    op.drop_table("activities")
    op.drop_table("deals")
    op.drop_table("leads")
    op.drop_table("customers")
